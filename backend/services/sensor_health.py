"""Sensor health: predictive maintenance + imputation, run once per packet
from TelemetryIngestionService.ingest().

Inputs: the TelemetryPayload and whatever anomaly the detector raised.
Outputs, attached to the payload and sent in the existing "telemetry" SSE event:
  payload.maintenance  {"humidity": {...}, "temperature": {...}, "pressure": {...}}
  payload.imputation   {"active": bool, "sensor": "humidity", "reported", "suggested", ...}
Plus an AnomalyEvent of type "sensor_health" the first time humidity drift
reaches "At Risk" (re-armed when it drops back below).
"""
from __future__ import annotations

import math
import os
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from models.schemas import AnomalyEvent, ShapAttribution, TelemetryPayload
from services.imputation_engine import ImputationEngine
from services.predictive_maintenance import DriftTracker

BASELINE_CSV = os.getenv(
    "BASELINE_CSV", str(Path(__file__).resolve().parents[2] / "data" / "train_baseline_normal.csv")
)
# Drift tracking pauses during a weather event and for this long after it.
WEATHER_COOLDOWN_S = float(os.getenv("WEATHER_COOLDOWN_S", "1800"))
# Fallback weather check until the confluence engine exists: over the last
# WEATHER_WINDOW_S, pressure fell and humidity rose by at least these amounts.
WEATHER_WINDOW_S = 120
WEATHER_DP_HPA = 5.0  # client.py's compressed day moves ~3.8 hPa in 2 min on its own
WEATHER_DRH_PCT = 5.0

TO_KEY = {"humidity": "RH", "temperature": "T", "pressure": "P",
          "dRH_dt": "RH", "dT_dt": "T", "dP_dt": "P"}
TO_NAME = {"RH": "humidity", "T": "temperature", "P": "pressure"}
NOT_TRACKED = "needs an independent reference (second sensor or neighbour station)"
SUSPECT_STATUSES = ("Watch", "At Risk", "Recalibrate Now")
ALERT_STATUSES = ("At Risk", "Recalibrate Now")


def _epoch(ts: str) -> float:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return time.time()


class SensorHealthService:
    def __init__(self) -> None:
        self.drift = DriftTracker()
        self.imputer = ImputationEngine()
        self.baseline_info: Optional[dict] = None
        self._history: dict[str, deque] = {}
        self._last_weather: dict[str, float] = {}
        self._alerted: dict[str, bool] = {}
        self.accepted: list[dict] = []
        if os.path.exists(BASELINE_CSV):
            try:
                self.baseline_info = self.imputer.load_baseline(BASELINE_CSV)
                # Live data and the CSV don't follow exactly the same curve, so the
                # normal offset is learned live; the CSV only sets a noise floor.
                self.drift.set_min_sigma("humidity", self.imputer.rh_resid_sigma)
                print(f"[SensorHealth] Baseline loaded: {self.baseline_info}")
            except Exception as e:  # noqa: BLE001
                print(f"[SensorHealth] Baseline CSV unusable ({e}); drift tracker will warm up live.")
        else:
            print("[SensorHealth] No baseline CSV found.")
        print("[SensorHealth] Drift tracker warms up on the first 10 minutes of live data.")

    # ------------------------------------------------------------------
    def process(self, payload: TelemetryPayload, anomaly: Optional[AnomalyEvent],
                weather_event: Optional[bool] = None) -> dict:
        """weather_event: pass the confluence engine's answer once it exists.
        Left as None, a simple pressure-fall + humidity-rise check is used."""
        sid = payload.station_id
        ts = _epoch(payload.timestamp)
        reading = {"ts": ts, "T": payload.temperature_c, "RH": payload.humidity_pct, "P": payload.pressure_hpa}
        hist = self._history.setdefault(sid, deque(maxlen=300))
        hist.append(reading)

        weather_source = "confluence"
        if weather_event is None:
            weather_event, weather_source = self._looks_like_weather(hist), "fallback_rule"
        if weather_event:
            self._last_weather[sid] = ts
        cooling = ts - self._last_weather.get(sid, -math.inf) < WEATHER_COOLDOWN_S

        culprit = None
        if anomaly and anomaly.culprit_sensors:
            culprit = TO_KEY.get(anomaly.culprit_sensors[0])
        rule_hit = anomaly is not None and anomaly.anomaly_type == "rule_flag"

        # --- maintenance (humidity checked against what temperature predicts)
        if cooling or (rule_hit and culprit in ("RH", "T")):
            rh = self.drift.hold(sid, "humidity")
            rh["paused"] = "weather" if cooling else "rule_flag"
        else:
            resid = payload.humidity_pct - self.imputer.expected_rh_from_t(payload.temperature_c)
            rh = self.drift.update(sid, "humidity", resid, ts)
        maintenance = {
            "humidity": rh,
            "temperature": {"sensor": "temperature", "status": "Not Tracked", "note": NOT_TRACKED},
            "pressure": {"sensor": "pressure", "status": "Not Tracked", "note": NOT_TRACKED},
        }

        # --- imputation
        drifting = rh.get("status") in ALERT_STATUSES
        target = None
        if anomaly and culprit and (rule_hit or not cooling):
            target = culprit  # hard rule violations are trusted even after a storm
        elif drifting:
            target = "RH"  # keep correcting a known-drifting sensor after the alarm fades
        if target:
            imputation = self.imputer.suggest(sid, target, reading)
            imputation["sensor"] = TO_NAME.get(target, target)
            imputation["reason"] = "anomaly" if target == culprit and anomaly else "drift"
        else:
            imputation = {"active": False}

        suspect = {target} if target else set()
        if rh.get("status") in SUSPECT_STATUSES:
            suspect.add("RH")
        if rule_hit and culprit:
            suspect.add(culprit)
        self.imputer.observe_healthy(sid, reading, tuple(s for s in ("T", "RH", "P") if s not in suspect))

        return {
            "maintenance": maintenance,
            "imputation": imputation,
            "weather": {"event": bool(weather_event), "cooldown": cooling, "source": weather_source},
            "event": self._maintenance_event(sid, payload, rh),
        }

    # ------------------------------------------------------------------
    def _looks_like_weather(self, hist: deque) -> bool:
        now = hist[-1]
        then = next((r for r in hist if now["ts"] - r["ts"] <= WEATHER_WINDOW_S), None)
        if then is None or then is now:
            return False
        return (then["P"] - now["P"] >= WEATHER_DP_HPA) and (now["RH"] - then["RH"] >= WEATHER_DRH_PCT)

    def _maintenance_event(self, sid: str, payload: TelemetryPayload, rh: dict) -> Optional[AnomalyEvent]:
        at_risk = rh.get("status") in ALERT_STATUSES
        if not at_risk:
            self._alerted[sid] = False
            return None
        if self._alerted.get(sid):
            return None
        self._alerted[sid] = True
        days = rh.get("days_to_recalibration")
        when = f" Estimated {days} days to recalibration at the current rate." if days is not None else ""
        direction = "above" if rh.get("direction") == "high" else "below"
        return AnomalyEvent(
            anomaly_id=f"health-{uuid.uuid4().hex[:8]}",
            detected_at=payload.timestamp,
            station_id=sid,
            anomaly_type="sensor_health",
            severity_score=0.8 if rh["status"] == "Recalibrate Now" else 0.6,
            culprit_sensors=["humidity"],
            diagnostic_message=(
                f"Humidity reads {abs(rh['ewma_residual']):.1f}% {direction} what the temperature predicts "
                f"({abs(rh['drift_sigma']):.1f} sigma, status {rh['status']}).{when}"
            ),
            shap_values=[ShapAttribution(feature="humidity", importance=1.0,
                                         direction="positive" if direction == "above" else "negative",
                                         message="Sustained offset from the temperature-humidity baseline.")],
            status="open",
        )

    # ------------------------------------------------------------------
    def accept_imputation(self, body: dict) -> dict:
        rec = {"accepted_at": datetime.now(timezone.utc).isoformat(), **body}
        self.accepted.append(rec)
        return rec

    def snapshot(self, station_id: str) -> dict:
        return {
            "maintenance": self.drift.snapshot(station_id),
            "baseline": self.baseline_info,
            "accepted_imputations": [a for a in self.accepted if a.get("station_id") == station_id][-20:],
        }


sensor_health = SensorHealthService()
