"""Imputation: estimates what a faulty sensor should read, using the sensors
that are still healthy.

Methods, tried in order:
- RH or T, live fit: RH = a + b*T fitted on this station's healthy readings
  from the last hour. Needs 120+ readings spanning at least 2 C.
- RH or T, dew-point hold: the moisture in the air (dew point) changes slowly,
  so the last healthy dew point plus the current healthy temperature gives RH,
  and the reverse gives T. Used while the reference is under 3 hours old.
- RH or T, linear fit: RH = a + b*T fitted on the baseline CSV.
- P, trend hold: last healthy pressure extended along its recent trend,
  capped at one hour of extrapolation.
Wind and solar are not imputed.
"""
from __future__ import annotations

import csv
import math
import os
from collections import deque

MAGNUS_A, MAGNUS_B = 17.62, 243.12
DEWPOINT_MAX_AGE_S = float(os.getenv("IMPUTE_DEWPOINT_MAX_AGE_S", str(3 * 3600)))
LIVE_FIT_WINDOW_S = 3600
LIVE_FIT_MIN_POINTS = 120
LIVE_FIT_MIN_T_RANGE = 2.0
P_TREND_WINDOW_S = 600
P_MAX_EXTRAPOLATE_S = 3600

COLUMN_ALIASES = {
    "T": ("T", "temp", "temperature", "temperature_c", "t_c"),
    "RH": ("RH", "rh", "humidity", "humidity_pct", "relative_humidity", "rh_pct"),
    "P": ("P", "pressure", "pressure_hpa", "p_hpa"),
}


def sat_vp(t: float) -> float:
    return 6.112 * math.exp(MAGNUS_A * t / (MAGNUS_B + t))


def dew_point(t: float, rh: float) -> float:
    rh = min(max(rh, 1e-3), 100.0)
    g = math.log(rh / 100.0) + MAGNUS_A * t / (MAGNUS_B + t)
    return MAGNUS_B * g / (MAGNUS_A - g)


def rh_from_dewpoint(t: float, td: float) -> float:
    return min(100.0, 100.0 * sat_vp(td) / sat_vp(t))


def t_from_dewpoint(rh: float, td: float) -> float:
    rh = min(max(rh, 1e-3), 100.0)
    a = math.log(sat_vp(td) * 100.0 / rh / 6.112)
    return MAGNUS_B * a / (MAGNUS_A - a)


def find_column(fieldnames, key):
    lower = {f.lower(): f for f in fieldnames}
    for alias in COLUMN_ALIASES[key]:
        if alias.lower() in lower:
            return lower[alias.lower()]
    return None


class ImputationEngine:
    def __init__(self) -> None:
        # Defaults from the project spec: ~85% RH at 22 C, ~40% RH at 38 C.
        self.a, self.b = 146.9, -2.8125
        self.rh_resid_sigma: float | None = None
        self.p_mean, self.p_sigma = 1005.0, None
        self.baseline_source = "spec_defaults"
        self._ref: dict[str, dict] = {}

    # ---- baseline --------------------------------------------------------
    def load_baseline(self, path: str) -> dict:
        """Fit RH-vs-T and pressure stats from the normal-weather CSV."""
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            cols = {k: find_column(reader.fieldnames or [], k) for k in COLUMN_ALIASES}
            if not cols["T"] or not cols["RH"]:
                raise ValueError(f"CSV needs temperature and humidity columns, found {reader.fieldnames}")
            ts, rhs, ps = [], [], []
            for row in reader:
                try:
                    t, rh = float(row[cols["T"]]), float(row[cols["RH"]])
                except (TypeError, ValueError):
                    continue
                ts.append(t)
                rhs.append(rh)
                if cols["P"]:
                    try:
                        ps.append(float(row[cols["P"]]))
                    except (TypeError, ValueError):
                        pass
        if len(ts) < 100:
            raise ValueError("fewer than 100 usable rows in baseline CSV")
        n = len(ts)
        mt, mr = sum(ts) / n, sum(rhs) / n
        var_t = sum((t - mt) ** 2 for t in ts)
        cov = sum((t - mt) * (r - mr) for t, r in zip(ts, rhs))
        self.b = cov / var_t
        self.a = mr - self.b * mt
        resid = [r - (self.a + self.b * t) for t, r in zip(ts, rhs)]
        self.rh_resid_sigma = math.sqrt(sum(e * e for e in resid) / (n - 2))
        if len(ps) > 100:
            self.p_mean = sum(ps) / len(ps)
            self.p_sigma = math.sqrt(sum((p - self.p_mean) ** 2 for p in ps) / (len(ps) - 1))
        var_r = sum((r - mr) ** 2 for r in rhs)
        corr = cov / math.sqrt(var_t * var_r) if var_r else float("nan")
        self.baseline_source = os.path.basename(path)
        return {
            "rows": n, "rh_fit": f"RH = {self.a:.2f} + {self.b:.3f}*T",
            "rh_resid_sigma": round(self.rh_resid_sigma, 3), "t_rh_corr": round(corr, 3),
            "p_mean": round(self.p_mean, 2),
            "p_sigma": round(self.p_sigma, 3) if self.p_sigma else None,
        }

    def expected_rh_from_t(self, t: float) -> float:
        return min(100.0, max(0.0, self.a + self.b * t))

    # ---- reference tracking ------------------------------------------------
    def observe_healthy(self, station_id: str, reading: dict, healthy=("T", "RH", "P")) -> None:
        ref = self._ref.setdefault(station_id, {"p_hist": deque(maxlen=900), "trh": deque(maxlen=3600)})
        ts, t, rh, p = reading["ts"], reading.get("T"), reading.get("RH"), reading.get("P")
        if "T" in healthy and "RH" in healthy and _ok(t) and _ok(rh):
            ref["td"], ref["td_ts"] = dew_point(t, rh), ts
            ref["trh"].append((ts, t, rh))
        if "P" in healthy and _ok(p):
            ref["p_hist"].append((ts, p))

    @staticmethod
    def _live_fit(trh, now):
        if not trh:
            return None
        pts = [(t, rh) for ts, t, rh in trh if now - ts <= LIVE_FIT_WINDOW_S]
        if len(pts) < LIVE_FIT_MIN_POINTS:
            return None
        ts_ = [t for t, _ in pts]
        if max(ts_) - min(ts_) < LIVE_FIT_MIN_T_RANGE:
            return None
        fit = _fit_line(pts)
        if not fit or abs(fit[1]) < 1e-3:
            return None
        return (*fit, round(now - trh[-1][0], 1))

    # ---- suggestion -----------------------------------------------------------
    def suggest(self, station_id: str, sensor: str, reading: dict) -> dict:
        ref = self._ref.get(station_id, {})
        ts = reading["ts"]
        out = {"active": True, "sensor": sensor, "reported": reading.get(sensor),
               "suggested": None, "method": None, "reference_age_s": None, "uncertainty": None}

        td, td_ts = ref.get("td"), ref.get("td_ts")
        td_fresh = td is not None and ts - td_ts <= DEWPOINT_MAX_AGE_S
        live = self._live_fit(ref.get("trh"), ts)

        if sensor == "RH":
            t = reading.get("T")
            if not _ok(t):
                out["method"] = "unavailable: temperature also missing"
            elif live:
                a, b, sig, age = live
                out.update(suggested=min(100.0, max(0.0, a + b * t)), method="live_fit",
                           reference_age_s=age, uncertainty=sig)
            elif td_fresh:
                out.update(suggested=rh_from_dewpoint(t, td), method="dewpoint_hold",
                           reference_age_s=round(ts - td_ts, 1))
            else:
                out.update(suggested=self.expected_rh_from_t(t), method="baseline_regression",
                           uncertainty=self.rh_resid_sigma)
        elif sensor == "T":
            rh = reading.get("RH")
            if not _ok(rh):
                out["method"] = "unavailable: humidity also missing"
            elif live:
                a, b, sig, age = live
                out.update(suggested=(rh - a) / b, method="live_fit",
                           reference_age_s=age, uncertainty=sig / abs(b))
            elif td_fresh:
                out.update(suggested=t_from_dewpoint(rh, td), method="dewpoint_hold",
                           reference_age_s=round(ts - td_ts, 1))
            else:
                out.update(suggested=(rh - self.a) / self.b, method="baseline_regression",
                           uncertainty=self.rh_resid_sigma / abs(self.b) if self.rh_resid_sigma else None)
        elif sensor == "P":
            hist = ref.get("p_hist")
            if hist:
                t0, p0 = hist[-1]
                recent = [(t, p) for t, p in hist if t >= t0 - P_TREND_WINDOW_S]
                slope = _slope(recent) if len(recent) >= 30 else 0.0
                dt = min(max(ts - t0, 0.0), P_MAX_EXTRAPOLATE_S)
                out.update(suggested=p0 + slope * dt, method="trend_hold",
                           reference_age_s=round(ts - t0, 1))
            else:
                out.update(suggested=self.p_mean, method="baseline_mean", uncertainty=self.p_sigma)
        else:
            out["method"] = "unsupported_sensor"

        for k in ("suggested", "uncertainty"):
            if out[k] is not None:
                out[k] = round(out[k], 2)
        return out


def _fit_line(pts):
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    vx = sum((x - mx) ** 2 for x, _ in pts)
    if vx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in pts) / vx
    a = my - b * mx
    sig = math.sqrt(sum((y - a - b * x) ** 2 for x, y in pts) / max(n - 2, 1))
    return a, b, sig


def _ok(v) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(v)


def _slope(points) -> float:
    n = len(points)
    mt = sum(t for t, _ in points) / n
    mp = sum(p for _, p in points) / n
    var = sum((t - mt) ** 2 for t, _ in points)
    return sum((t - mt) * (p - mp) for t, p in points) / var if var else 0.0
