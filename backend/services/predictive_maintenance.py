"""Predictive maintenance: tracks slow sensor drift and estimates when a
sensor will need recalibration.

Per station and per tracked sensor:
1. The pipeline passes in a residual every second: reported value minus a
   reference value. For RH the reference is what the temperature says RH
   should be. For pressure it is the long-run baseline mean.
2. The residual's normal mean and spread (sigma) come from the baseline CSV,
   or from the first WARMUP_SAMPLES readings if no CSV was loaded.
3. An EWMA of the residual ignores single spikes but builds up under a steady
   offset. drift_sigma = (ewma - baseline_mean) / baseline_sigma.
4. A least-squares line through recent |drift_sigma| values gives the growth
   rate, and from that the time left until FAIL_SIGMA.

The pipeline should not feed this tracker while a natural weather event is
in progress, otherwise a long storm looks like drift.
"""
from __future__ import annotations

import math
import os
from collections import deque
from dataclasses import dataclass, field

EWMA_LAMBDA = float(os.getenv("MAINT_EWMA_LAMBDA", "0.01"))  # ~100 s memory at 1 Hz
# 600 = one full fake day in simulator/client.py. For a real station this
# should cover at least a full day of data.
WARMUP_SAMPLES = int(os.getenv("MAINT_WARMUP_SAMPLES", "600"))
WATCH_SIGMA = 1.0
AT_RISK_SIGMA = 2.0
FAIL_SIGMA = 3.0
# 1.0 means real time. A value above 1 speeds up the countdown for a demo.
# If you use it, say so in the video.
TIME_SCALE = float(os.getenv("MAINT_TIME_SCALE", "1.0"))
TREND_SAMPLE_EVERY_S = float(os.getenv("MAINT_TREND_EVERY_S", "5"))
TREND_POINTS = int(os.getenv("MAINT_TREND_POINTS", "120"))
MIN_TREND_POINTS = 10
SECONDS_PER_DAY = 86400.0


@dataclass
class _SensorState:
    base_mean: float | None = None
    base_sigma: float | None = None
    n: int = 0          # warmup count (Welford)
    wm: float = 0.0
    wm2: float = 0.0
    ewma: float | None = None
    trend: deque = field(default_factory=lambda: deque(maxlen=TREND_POINTS))
    last_trend_t: float = -math.inf

    @property
    def ready(self) -> bool:
        return self.base_sigma is not None


class DriftTracker:
    def __init__(self) -> None:
        self._states: dict[tuple[str, str], _SensorState] = {}
        self._seeds: dict[str, tuple[float, float]] = {}
        self._min_sigma: dict[str, float] = {}

    # ---- setup -----------------------------------------------------------
    def seed(self, sensor: str, mean: float, sigma: float) -> None:
        """Use baseline statistics instead of a live warmup (all stations)."""
        self._seeds[sensor] = (float(mean), max(float(sigma), 1e-6))
        for (_, s_name), st in self._states.items():
            if s_name == sensor and not st.ready:
                self._apply_seed(st, sensor)

    def set_min_sigma(self, sensor: str, sigma: float) -> None:
        """Keep the live warmup, but never assume less noise than this."""
        self._min_sigma[sensor] = float(sigma)

    def reset(self, station_id: str, sensor: str) -> None:
        """Call after a technician recalibrates the sensor."""
        self._states.pop((station_id, sensor), None)

    # ---- per-second update -------------------------------------------------
    def update(self, station_id: str, sensor: str, residual: float | None, t: float) -> dict:
        st = self._state(station_id, sensor)
        if residual is None or not math.isfinite(residual):
            return self._report(st, sensor)

        if not st.ready:
            st.n += 1
            d = residual - st.wm
            st.wm += d / st.n
            st.wm2 += d * (residual - st.wm)
            if st.n >= WARMUP_SAMPLES:
                st.base_mean = st.wm
                st.base_sigma = max(math.sqrt(st.wm2 / (st.n - 1)), self._min_sigma.get(sensor, 1e-6))
                st.ewma = st.base_mean
            return self._report(st, sensor)

        st.ewma = EWMA_LAMBDA * residual + (1 - EWMA_LAMBDA) * st.ewma
        if t - st.last_trend_t >= TREND_SAMPLE_EVERY_S:
            st.trend.append((t, abs(self._z(st))))
            st.last_trend_t = t
        return self._report(st, sensor)

    def hold(self, station_id: str, sensor: str) -> dict:
        """Report current state without feeding a new residual."""
        return self._report(self._state(station_id, sensor), sensor)

    def snapshot(self, station_id: str) -> dict:
        return {s: self._report(st, s) for (stn, s), st in self._states.items() if stn == station_id}

    # ---- internals -----------------------------------------------------------
    def _state(self, station_id: str, sensor: str) -> _SensorState:
        key = (station_id, sensor)
        if key not in self._states:
            st = _SensorState()
            self._apply_seed(st, sensor)
            self._states[key] = st
        return self._states[key]

    def _apply_seed(self, st: _SensorState, sensor: str) -> None:
        if sensor in self._seeds:
            st.base_mean, st.base_sigma = self._seeds[sensor]
            st.ewma = st.base_mean

    @staticmethod
    def _z(st: _SensorState) -> float:
        return (st.ewma - st.base_mean) / st.base_sigma

    def _report(self, st: _SensorState, sensor: str) -> dict:
        if not st.ready:
            return {
                "sensor": sensor, "status": "Learning", "drift_sigma": None,
                "days_to_recalibration": None, "progress": 0.0,
                "warmup": f"{st.n}/{WARMUP_SAMPLES}",
            }
        z = self._z(st)
        az = abs(z)
        if az >= FAIL_SIGMA:
            status = "Recalibrate Now"
        elif az >= AT_RISK_SIGMA:
            status = "At Risk"
        elif az >= WATCH_SIGMA:
            status = "Watch"
        else:
            status = "Healthy"
        days, rate = self._days_left(st, az)
        return {
            "sensor": sensor,
            "status": status,
            "drift_sigma": round(z, 3),
            "direction": "high" if z > 0 else "low",
            "ewma_residual": round(st.ewma - st.base_mean, 4),
            "baseline_sigma": round(st.base_sigma, 4),
            "progress": round(min(az / FAIL_SIGMA, 1.0), 3),
            "trend": "rising" if rate and rate > 0 else "stable",
            "days_to_recalibration": days,
            "time_scale": TIME_SCALE,
        }

    @staticmethod
    def _days_left(st: _SensorState, az: float) -> tuple[float | None, float | None]:
        if az >= FAIL_SIGMA:
            return 0.0, None
        if len(st.trend) < MIN_TREND_POINTS:
            return None, None
        n = len(st.trend)
        mt = sum(t for t, _ in st.trend) / n
        mz = sum(z for _, z in st.trend) / n
        var = sum((t - mt) ** 2 for t, _ in st.trend)
        if var == 0:
            return None, None
        slope = sum((t - mt) * (z - mz) for t, z in st.trend) / var  # sigma per second
        if slope <= 1e-9:
            return None, slope
        seconds = (FAIL_SIGMA - az) / slope * TIME_SCALE
        return round(seconds / SECONDS_PER_DAY, 2), slope
