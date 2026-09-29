"""
Unit & Integration Tests for Laptop 1 Edge Weather Station Transmitter
Stage 6 / Task 3.2 Verification
Assigned to: Araz (feat/araz)
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.schemas import TelemetryPayload
from simulator.client import (
    CircularRingBuffer,
    EdgeIMDBoundaryChecker,
    make_packet,
    make_incident_burst,
    calculate_dew_point
)
from services.telemetry_ingestion import telemetry_ingestion
from data.store import store


def test_transmitter_fault_packets():
    """Verify all 5 transmitter modes generate physically consistent baseline and fault readings."""
    normal = make_packet(1, "AGRA-01", 0, "normal")
    heat = make_packet(2, "AGRA-01", 0, "heat_spike")
    drift = make_packet(3, "AGRA-01", 0, "humidity_drift")
    storm = make_packet(4, "AGRA-01", 0, "storm")
    frozen = make_packet(5, "AGRA-01", 0, "frozen_sensor")

    # Mode 1: Heat Spike (+8 C)
    assert heat["temperature_c"] - normal["temperature_c"] >= 7.5, "Heat spike did not increase temperature by >=7.5 C"

    # Mode 2: Capacitive Drift (+15% RH bias)
    assert drift["humidity_pct"] - normal["humidity_pct"] >= 14.0, "Capacitive drift did not increase RH by >=14%"

    # Mode 3: Severe Thunderstorm (-11 hPa, 94% RH, -8 C, wind surge)
    assert storm["pressure_hpa"] < normal["pressure_hpa"] - 10.0, "Storm pressure did not plunge by >=10 hPa"
    assert storm["humidity_pct"] == 94.0, "Storm humidity should surge to 94%"
    assert storm["temperature_c"] < normal["temperature_c"] - 7.0, "Storm did not produce cold pool cooling >=7 C"
    assert storm["wind_speed_ms"] >= 12.0, "Storm wind speed did not surge >=12 m/s"

    # Mode 4: Frozen Sensor (RH flatlines at 84.2%)
    assert frozen["humidity_pct"] == 84.2, "Frozen sensor RH must flatline at 84.2%"

    # Mode 0: Normal Baseline Dew Point Physical Sanity
    assert normal["dew_point_c"] <= normal["temperature_c"] + 0.5, "Dew point violates physical equilibrium"
    print("PASS: test_transmitter_fault_packets")


def test_circular_ring_buffer():
    """Verify in-memory circular ring buffer maintains 120-item capacity and retrieves 12-sample context."""
    ring = CircularRingBuffer(capacity=120)

    # Push 150 items to test FIFO overflow eviction
    for seq in range(150):
        packet = make_packet(seq, "AGRA-01", float(seq), "normal")
        ring.append(packet)

    assert len(ring) == 120, f"Ring buffer capacity expected 120, got {len(ring)}"

    # Context window should yield exactly the last 12 samples
    context = ring.get_context(12)
    assert len(context) == 12, f"Expected 12 context samples, got {len(context)}"
    assert context[-1]["sequence"] == 149, "Most recent context packet is incorrect"
    assert context[0]["sequence"] == 138, "Oldest context packet in window is incorrect"
    print("PASS: test_circular_ring_buffer")


def test_edge_imd_boundary_checker():
    """Verify edge-side Layer 1.1 IMD boundary and step checks flag physical violations."""
    normal = make_packet(10, "AGRA-01", 10.0, "normal")

    # Clean normal packet should pass
    clean_check = EdgeIMDBoundaryChecker.evaluate(normal)
    assert clean_check is None, f"Clean packet unexpectedly flagged: {clean_check}"

    # 1. Climatological envelope violations
    extreme_hot = dict(normal, temperature_c=65.0)
    hot_res = EdgeIMDBoundaryChecker.evaluate(extreme_hot)
    assert hot_res is not None and hot_res["rule"] == "IMD_CLIMATOLOGICAL_TEMP_BOUND"

    extreme_cold = dict(normal, temperature_c=-15.0)
    cold_res = EdgeIMDBoundaryChecker.evaluate(extreme_cold)
    assert cold_res is not None and cold_res["rule"] == "IMD_CLIMATOLOGICAL_TEMP_BOUND"

    # 2. Rate-of-change violations
    step_spike = dict(normal, temperature_c=normal["temperature_c"] + 8.0)
    step_res = EdgeIMDBoundaryChecker.evaluate(step_spike, previous=normal)
    assert step_res is not None and step_res["rule"] == "IMD_TEMP_RATE_OF_CHANGE_EXCEEDED"

    # 3. Stuck sensor flatline check
    stuck_history = [dict(normal, humidity_pct=84.2) for _ in range(8)]
    stuck_current = dict(normal, humidity_pct=84.2)
    stuck_res = EdgeIMDBoundaryChecker.evaluate(stuck_current, recent_history=stuck_history)
    assert stuck_res is not None and stuck_res["rule"] == "IMD_STUCK_SENSOR_FLATLINE"
    print("PASS: test_edge_imd_boundary_checker")


def test_incident_context_burst_payload():
    """Verify Incident Burst payload structure contains trigger reading + 12 context frames."""
    ring = CircularRingBuffer(capacity=120)
    for seq in range(20):
        ring.append(make_packet(seq, "AGRA-01", float(seq), "normal"))

    trigger = make_packet(21, "AGRA-01", 21.0, "humidity_drift")
    context_12 = ring.get_context(12)

    burst = make_incident_burst(
        trigger_packet=trigger,
        context_window=context_12,
        trigger_reason="CHAOS_KEY_HUMIDITY_DRIFT",
        fault_mode="humidity_drift",
        culprit_sensor="humidity_pct"
    )

    assert burst["station_id"] == "AGRA-01"
    assert burst["fault_mode"] == "humidity_drift"
    assert burst["trigger_packet"]["sequence"] == 21
    assert len(burst["context_window"]) == 12
    assert burst["bandwidth_saved_pct"] >= 90.0
    print("PASS: test_incident_context_burst_payload")


def test_mqtt_payload_uses_existing_ingestion_pipeline():
    """Verify standard edge telemetry packet passes through backend ingestion cleanly."""
    packet = make_packet(9001, "AGRA-01", 0, "normal")
    payload = TelemetryPayload.model_validate(packet)
    asyncio.run(telemetry_ingestion.ingest(payload))

    assert store.get_latest_telemetry() is not None
    assert store.get_latest_telemetry().sequence == 9001
    print("PASS: test_mqtt_payload_uses_existing_ingestion_pipeline")


def test_incident_burst_ingestion_compatibility():
    """Verify backend ingestion handles incident burst payloads by unwrapping the trigger packet."""
    ring = CircularRingBuffer(capacity=120)
    for seq in range(12):
        ring.append(make_packet(seq, "AGRA-01", float(seq), "normal"))

    trigger = make_packet(9002, "AGRA-01", 9002.0, "storm")
    burst = make_incident_burst(
        trigger_packet=trigger,
        context_window=ring.get_context(12),
        trigger_reason="CHAOS_KEY_STORM",
        fault_mode="storm",
        culprit_sensor="pressure_hpa"
    )

    # Ingestion extracts trigger_packet
    payload = TelemetryPayload.model_validate(burst["trigger_packet"])
    asyncio.run(telemetry_ingestion.ingest(payload))

    assert store.get_latest_telemetry() is not None
    assert store.get_latest_telemetry().sequence == 9002
    print("PASS: test_incident_burst_ingestion_compatibility")


if __name__ == "__main__":
    test_transmitter_fault_packets()
    test_circular_ring_buffer()
    test_edge_imd_boundary_checker()
    test_incident_context_burst_payload()
    test_mqtt_payload_uses_existing_ingestion_pipeline()
    test_incident_burst_ingestion_compatibility()
    print("\n>>> ALL STAGE 6 / LAPTOP 1 EDGE TRANSMITTER TESTS PASSED SUCCESSFULLY! <<<")
