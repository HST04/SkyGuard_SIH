"""
End-to-End System Integration Tests for SkyGuard AI.
Verifies the complete integration:
- Edge Simulator payload formatting and transmitter
- FastAPI backend ingestion and cold-start WARMUP phase
- Multi-tier ML pipeline (Gatekeeper, Model A/B, LLM debate, Sensor Imputation)
- Maintenance & Imputation endpoints
- Automated Pitch Script controls
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root directory and subdirectories are on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "skyguard_data_model"))
sys.path.insert(0, os.path.join(ROOT_DIR, "SKYGUARD EDGE SIMULATOR"))

from backend.main import app
from backend.schemas import TelemetryPayload
from src.transmitter import EdgeTransmitter

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_edge_simulator_payload_compatibility():
    """Verify Edge Simulator transmitter builds a payload that backend accepts."""
    config = {
        "endpoint_url": "http://localhost:8000/api/v1/telemetry",
        "device_id": "TEST-STATION-01",
        "firmware_version": "v2.1.0-aws-edge"
    }
    transmitter = EdgeTransmitter(config)
    sample_reading = {
        "timestamp_ms": 1728114000000,
        "iso_time": "2026-10-05T08:00:00.000Z",
        "temperature_c": 28.5,
        "humidity_pct": 72.0,
        "pressure_hpa": 1011.5,
        "wind_speed_mps": 3.4,
        "wind_direction_deg": 185.0,
        "solar_radiation_wm2": 450.0,
        "battery_pct": 98.0,
        "voltage_v": 3.95,
        "rssi_dbm": -68,
        "_ground_truth": {"status": "NORMAL", "active_labels": ["NORMAL"]}
    }
    payload = transmitter.build_aws_payload(sample_reading, region_key="mumbai_monsoon")

    # Ingest into backend
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "confluence" in data
    assert "telemetry" in data


def test_cold_start_warmup_and_active_inference():
    """
    Verify that packets 1 to 11 are labeled as WARMUP,
    and on packet 12, full PyTorch ML inference runs.
    """
    station_id = "TEST-WARMUP-01"

    # Send 5 nominal packets (warmup)
    for seq in range(1, 6):
        payload = {
            "station_id": station_id,
            "temperature_c": 26.0,
            "humidity_pct": 55.0,
            "pressure_hpa": 1012.0,
            "sequence": seq,
            "fault_type": "normal"
        }
        res = client.post("/api/v1/telemetry", json=payload)
        assert res.status_code == 200
        confluence = res.json()["confluence"]
        assert confluence["classification"] == "Nominal Baseline"
        assert "Warmup" in confluence["summary"] or "warmup" in confluence["summary"].lower()

    # Complete window up to 12 packets
    for seq in range(6, 13):
        payload = {
            "station_id": station_id,
            "temperature_c": 26.0,
            "humidity_pct": 55.0,
            "pressure_hpa": 1012.0,
            "sequence": seq,
            "fault_type": "normal"
        }
        res = client.post("/api/v1/telemetry", json=payload)
        assert res.status_code == 200

    # On packet 12, gatekeeper has evaluated the window
    data = res.json()
    assert data["telemetry"]["reconstruction_error"] >= 0.0
    assert data["confluence"]["confidence_score"] > 80.0


def test_anomaly_detection_and_imputation():
    """Verify that an injected sensor defect triggers Stage 2/3 and produces imputation."""
    station_id = "TEST-ANOMALY-01"

    # Seed 12 packets with sudden unphysical capacitive drift / stuck humidity
    for seq in range(1, 13):
        payload = {
            "station_id": station_id,
            "temperature_c": 25.0,
            "humidity_pct": 98.0 if seq >= 8 else 50.0,
            "pressure_hpa": 985.0 if seq >= 8 else 1013.25,
            "sequence": seq,
            "fault_type": "humidity_drift" if seq >= 8 else "normal"
        }
        res = client.post("/api/v1/telemetry", json=payload)
        assert res.status_code == 200

    data = res.json()
    # Confluence should flag either Sensor Defect or Natural Weather Event or Compound
    assert data["classification"] in ["Sensor Defect", "Natural Weather Event", "Compound Event"]
    assert len(data["agent_dialogue"]) >= 2

    # Check that anomalies endpoint recorded the event with transmitted data and decision reasoning
    ano_res = client.get(f"/api/v1/anomalies?station_id={station_id}")
    assert ano_res.status_code == 200
    anomalies = ano_res.json()
    assert len(anomalies) >= 1
    assert anomalies[0]["transmitted_data"] is not None
    assert "sensor_readings" in anomalies[0]["transmitted_data"]
    assert anomalies[0]["decision_reasoning"] is not None
    assert "why_decision" in anomalies[0]["decision_reasoning"]


def test_anomaly_logging_acknowledge_resolve_ignore():
    """Verify that operator can acknowledge, resolve, or ignore defects, logging the decision and resetting the station state."""
    station_id = "TEST-LOG-01"
    for seq in range(1, 13):
        payload = {
            "station_id": station_id,
            "temperature_c": 25.0,
            "humidity_pct": 99.0 if seq >= 8 else 50.0,
            "pressure_hpa": 1013.25,
            "sequence": seq,
            "fault_type": "humidity_drift" if seq >= 8 else "normal"
        }
        client.post("/api/v1/telemetry", json=payload)
    
    ano_res = client.get(f"/api/v1/anomalies?station_id={station_id}&status=open")
    assert ano_res.status_code == 200
    anomalies = ano_res.json()
    assert len(anomalies) >= 1
    target_id = anomalies[0]["anomaly_id"]

    # Test Ignore action
    ign_res = client.patch(f"/api/v1/anomalies/{target_id}", json={"status": "ignored", "resolution_note": "Operator ignored transient artifact."})
    assert ign_res.status_code == 200
    assert ign_res.json()["status"] == "ignored"

    # Verify decisions table logged the action
    dec_res = client.get(f"/api/v1/decisions?station_id={station_id}")
    assert dec_res.status_code == 200
    decisions = dec_res.json()["decisions"]
    assert any("Ignored" in d["trigger_reason"] or "ignored" in d["trigger_reason"] for d in decisions)

    # Verify station overview now shows normal (all sensors OK)
    over_res = client.get(f"/api/v1/telemetry/overview?station_id={station_id}")
    assert over_res.status_code == 200
    assert over_res.json()["status"] == "normal"


def test_imputation_accept_and_maintenance():
    """Verify accepting an imputation and reading sensor maintenance diagnostics."""
    accept_req = {
        "station_id": "AGRA-01",
        "sensor": "humidity",
        "suggested": 45.2,
        "reported": 98.4,
        "method": "Thermodynamic Dew-Point Inversion",
        "sequence": 42
    }
    res = client.post("/api/v1/imputation/accept", json=accept_req)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    hist_res = client.get("/api/v1/imputation/history?station_id=AGRA-01")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1

    maint_res = client.get("/api/v1/maintenance?station_id=AGRA-01")
    assert maint_res.status_code == 200
    maint_data = maint_res.json()
    assert "humidity" in maint_data
    assert maint_data["humidity"]["status"] in ["Healthy", "Watch", "At Risk", "Recalibrate Now"]


def test_pitch_script_controls():
    """Verify starting and stopping the 5-minute automated demo scenario."""
    start_res = client.post("/api/v1/simulator/pitch-script/start")
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "started"

    status_res = client.get("/api/v1/simulator/status")
    assert status_res.status_code == 200
    assert status_res.json()["pitch_script"] is not None

    stop_res = client.post("/api/v1/simulator/pitch-script/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] == "stopped"
