"""Harsh: predictive maintenance + imputation.  Run: python -m pytest tests -q"""
import asyncio
import os
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.schemas import TelemetryPayload
from services import imputation_engine as ie
from services.predictive_maintenance import DriftTracker
from services.sensor_health import SensorHealthService
from simulator.client import make_packet

START = datetime(2026, 9, 28, tzinfo=timezone.utc)


def feed(scenario, n, fault_at=700):
    """Runs packets through a fresh SensorHealthService (no detector)."""
    random.seed(3)
    svc = SensorHealthService()
    outs = []
    for i in range(n):
        p = make_packet(i, "AGRA-01", i, "normal")
        p["timestamp"] = (START + timedelta(seconds=i)).isoformat()
        k = i - fault_at
        if k >= 0 and scenario == "drift":
            p["humidity_pct"] = min(100, p["humidity_pct"] + min(15, 15 * k / 120))
        if k >= 0 and scenario == "storm":
            f = min(1, k / 90)
            p["pressure_hpa"] -= 11 * f
            p["temperature_c"] -= 8 * f
            p["humidity_pct"] += (94 - p["humidity_pct"]) * f + random.gauss(0, 0.3)
        payload = TelemetryPayload.model_validate(p)
        outs.append((payload, svc.process(payload, None)))
    return outs


def test_dewpoint_roundtrip():
    td = ie.dew_point(30.0, 60.0)
    assert abs(ie.rh_from_dewpoint(30.0, td) - 60.0) < 0.01
    assert abs(ie.t_from_dewpoint(60.0, td) - 30.0) < 0.01


def test_tracker_flags_offset():
    random.seed(1)
    d = DriftTracker()
    d.seed("humidity", 0.0, 1.0)
    for t in range(600):
        r = d.update("S", "humidity", random.gauss(3 if t > 200 else 0, 1), t)
    assert r["status"] in ("At Risk", "Recalibrate Now")


def test_normal_weather_stays_healthy():
    outs = feed("normal", 2400)
    statuses = {h["maintenance"]["humidity"]["status"] for _, h in outs[600:]}
    assert statuses == {"Healthy"}
    assert not any(h["event"] for _, h in outs)


def test_drift_detected_and_imputed():
    outs = feed("drift", 1000)
    events = [h["event"] for _, h in outs if h["event"]]
    assert len(events) == 1 and events[0].anomaly_type == "sensor_health"
    payload, last = outs[-1]
    assert last["maintenance"]["humidity"]["status"] in ("At Risk", "Recalibrate Now")
    imp = last["imputation"]
    assert imp["active"] and imp["sensor"] == "humidity"
    assert abs(imp["suggested"] - (payload.humidity_pct - 15)) < 4


def test_storm_pauses_maintenance():
    outs = feed("storm", 1300)
    assert any(h["weather"]["event"] for _, h in outs)
    assert not any(h["event"] for _, h in outs)
    assert all(not h["imputation"]["active"] for _, h in outs)
