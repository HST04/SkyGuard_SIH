import asyncio
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.schemas import TelemetryPayload
from simulator.client import make_packet
from services.telemetry_ingestion import telemetry_ingestion
from data.store import store


def test_transmitter_fault_packets():
    normal = make_packet(1, "AGRA-01", 0, "normal")
    heat = make_packet(2, "AGRA-01", 0, "heat_spike")
    drift = make_packet(3, "AGRA-01", 0, "humidity_drift")
    storm = make_packet(4, "AGRA-01", 0, "storm")

    assert heat["temperature_c"] - normal["temperature_c"] >= 7.5
    assert drift["humidity_pct"] - normal["humidity_pct"] >= 14.0
    assert storm["pressure_hpa"] < normal["pressure_hpa"] - 10.0
    assert storm["humidity_pct"] == 94.0


def test_mqtt_payload_uses_existing_ingestion_pipeline():
    packet = make_packet(9001, "AGRA-01", 0, "normal")
    payload = TelemetryPayload.model_validate(packet)
    asyncio.run(telemetry_ingestion.ingest(payload))

    assert store.get_latest_telemetry() is not None
    assert store.get_latest_telemetry().sequence == 9001
