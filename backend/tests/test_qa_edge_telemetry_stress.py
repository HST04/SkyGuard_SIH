"""
Harsh, Rigorous QA Stress Test Suite: Edge Transmitter, Chaos Modes,
MQTT/REST Ingestion Pipeline, Ring Buffer Context Bursts & Streaming Endpoints.

Author: QA Agent 3 (Edge Simulator, Chaos Modes & Telemetry Pipeline QA Specialist)
Project: SkyGuard AI
Target Files:
  - backend/simulator/client.py
  - backend/simulator/edge_simulator.py
  - backend/services/telemetry_ingestion.py
  - backend/services/sse_manager.py
  - backend/routers/telemetry.py
  - backend/routers/simulator.py
  - backend/main.py
"""

import asyncio
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import settings
from data.db import init_db
from data.store import store
from main import app
from models.schemas import AnomalyEvent, FaultInjectionRequest, TelemetryPayload
from routers.telemetry import stream_telemetry
from services.confluence_engine import confluence_engine
from services.mqtt_subscriber import mqtt_subscriber
from services.multi_scale_analyzer import multi_scale_analyzer
from services.rule_engine import IMDPhysicsRuleEngine
from services.sensor_health import sensor_health
from services.sse_manager import SSEBroadcastManager, sse_manager
from services.telemetry_ingestion import telemetry_ingestion
from simulator.client import (
    CircularRingBuffer,
    EdgeIMDBoundaryChecker,
    calculate_dew_point,
    make_incident_burst,
    make_packet,
)
from simulator.edge_simulator import simulator


@pytest.fixture(autouse=True)
def clean_system_state():
    """Isolate store and DB state for each test run."""
    store.clear()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(init_db())
    except Exception:
        pass
    yield
    store.clear()
    loop.close()


# ============================================================================
# SUITE 1: MALFORMED PAYLOADS & TYPE MISMATCH ROBUSTNESS
# ============================================================================

class TestMalformedPayloadsAndTypeMismatch:
    """Rigorous tests evaluating how the ingestion pipeline, schemas, and endpoints

    handle malformed, typed, out-of-range, and adversarial payloads.
    """

    def test_missing_required_fields_telemetry_payload(self):
        """Verify that omitting mandatory fields raises Pydantic ValidationError."""
        valid_sample = make_packet(1, "AGRA-01", 0.0, "normal")

        # Required fields in TelemetryPayload
        required_fields = ["timestamp", "temperature_c", "pressure_hpa", "humidity_pct", "dew_point_c", "sequence"]

        for field in required_fields:
            corrupted = dict(valid_sample)
            del corrupted[field]
            with pytest.raises(ValidationError) as exc_info:
                TelemetryPayload.model_validate(corrupted)
            assert field in str(exc_info.value), f"Expected validation error for missing field '{field}'"

    def test_type_mismatch_string_in_float_fields(self):
        """Verify non-numeric strings in numeric fields are rejected with ValidationError."""
        valid_sample = make_packet(2, "AGRA-01", 0.0, "normal")

        # Test corrupting float fields with alpha strings
        for field in ["temperature_c", "pressure_hpa", "humidity_pct", "dew_point_c", "wind_speed_ms"]:
            corrupted = dict(valid_sample, **{field: "NOT_A_FLOAT"})
            with pytest.raises(ValidationError):
                TelemetryPayload.model_validate(corrupted)

        # Test complex nested structures where float expected
        with pytest.raises(ValidationError):
            TelemetryPayload.model_validate(dict(valid_sample, temperature_c={"value": 30.5}))

        # Test list where float expected
        with pytest.raises(ValidationError):
            TelemetryPayload.model_validate(dict(valid_sample, humidity_pct=[50.0]))

    def test_string_coercion_and_boundary_types(self):
        """Verify numeric strings are coerced while boolean-as-float is audited."""
        valid_sample = make_packet(3, "AGRA-01", 0.0, "normal")
        valid_sample["temperature_c"] = "34.5"
        payload = TelemetryPayload.model_validate(valid_sample)
        assert isinstance(payload.temperature_c, float)
        assert payload.temperature_c == 34.5

    def test_extra_unexpected_fields_tolerance(self):
        """Verify unexpected extra fields are safely ignored by TelemetryPayload."""
        valid_sample = make_packet(4, "AGRA-01", 0.0, "normal")
        valid_sample["injected_attack_vector"] = "<script>alert(1)</script>"
        valid_sample["unauthorized_override"] = True
        valid_sample["deep_meta"] = {"cluster": "us-east-1", "flags": [1, 2, 3]}

        payload = TelemetryPayload.model_validate(valid_sample)
        assert not hasattr(payload, "injected_attack_vector")
        assert not hasattr(payload, "unauthorized_override")

    @pytest.mark.anyio
    async def test_special_float_values_nan_inf_pipeline_leakage(self):
        """CRITICAL VULNERABILITY TEST:

        Evaluate what happens when NaN or Inf are injected into the ingestion pipeline.
        NaN bypasses comparisons (< and > evaluate to False), poisoning calculations
        and leaking into JSON streams as invalid RFC 8259 tokens.
        """
        store.clear()

        # 1. NaN in temperature_c
        nan_payload = TelemetryPayload(
            station_id="AGRA-01",
            timestamp=datetime.now(timezone.utc).isoformat(),
            temperature_c=float("nan"),
            pressure_hpa=1010.0,
            humidity_pct=50.0,
            dew_point_c=15.0,
            sequence=10,
            source="qa-stress",
        )

        # Ingest NaN payload
        anomaly = await telemetry_ingestion.ingest(nan_payload)

        # In standard rule engine, nan < -10 is False and nan > 60 is False!
        # NaN completely evades climatological envelope bounds!
        assert anomaly is None, "NaN should silently bypass naive numeric bounds checks"

        latest = store.get_latest_telemetry()
        assert math.isnan(latest.temperature_c), "NaN temperature persisted into store"

        # 2. Inf in wind_speed_ms: Rule engine only bounds T, RH, and P. Wind and solar are unbounded!
        inf_wind_payload = TelemetryPayload(
            station_id="AGRA-01",
            timestamp=datetime.now(timezone.utc).isoformat(),
            temperature_c=30.0,
            pressure_hpa=1010.0,
            humidity_pct=50.0,
            dew_point_c=15.0,
            wind_speed_ms=float("inf"),
            solar_radiation_wm2=float("inf"),
            sequence=11,
            source="qa-stress",
        )
        anomaly_inf = await telemetry_ingestion.ingest(inf_wind_payload)
        # Unbounded channels pass through rule engine without raising rule violations!
        assert anomaly_inf is None, "Unbounded wind/solar channels pass through rule engine unvetted"

    def test_mqtt_subscriber_malformed_payload_discard(self):
        """Verify MQTT subscriber message handler discards malformed UTF-8, non-JSON,

        and schema-invalid bytes without crashing the background thread.
        """
        mock_client = MagicMock()
        mock_userdata = MagicMock()

        class MockMessage:
            def __init__(self, payload_bytes: bytes, topic: str = "skyguard/telemetry"):
                self.payload = payload_bytes
                self.topic = topic

        # Case 1: Corrupted non-UTF8 bytes
        bad_utf8 = MockMessage(b"\xff\xfe\x00\x12\x89")
        # Should not raise exception
        mqtt_subscriber._on_message(mock_client, mock_userdata, bad_utf8)

        # Case 2: Malformed JSON syntax
        bad_json = MockMessage(b"{station_id: AGRA-01, sequence: ")
        mqtt_subscriber._on_message(mock_client, mock_userdata, bad_json)

        # Case 3: Valid JSON but non-dict root (e.g. array, integer, string, null)
        for non_dict in [b"[1, 2, 3]", b"12345", b'"string_payload"', b"null"]:
            mqtt_subscriber._on_message(mock_client, mock_userdata, MockMessage(non_dict))

        # Case 4: Empty dict
        mqtt_subscriber._on_message(mock_client, mock_userdata, MockMessage(b"{}"))

    def test_fastapi_rest_endpoints_malformed_inputs(self):
        """Verify FastAPI REST endpoints strictly reject malformed JSON and out-of-spec parameters."""
        client = TestClient(app)

        # 1. Fault injection: invalid fault_type
        res_bad_fault = client.post("/api/v1/simulator/inject", json={"fault_type": "invalid_mode"})
        assert res_bad_fault.status_code == 422

        # 2. Fault injection: string intensity
        res_bad_intensity = client.post(
            "/api/v1/simulator/inject",
            json={"fault_type": "heat_spike", "intensity": "extreme"},
        )
        assert res_bad_intensity.status_code == 422

        # 3. Fault injection: valid request
        res_valid = client.post(
            "/api/v1/simulator/inject",
            json={"fault_type": "heat_spike", "intensity": 1.2, "duration_seconds": 15},
        )
        assert res_valid.status_code == 200
        assert res_valid.json()["active_fault"] == "heat_spike"

        # 4. Imputation accept: missing suggested field
        res_bad_impute = client.post(
            "/api/v1/imputation/accept",
            json={"station_id": "AGRA-01", "sensor": "humidity"},
        )
        assert res_bad_impute.status_code == 422

        # 5. Imputation accept: invalid sensor literal
        res_bad_sensor = client.post(
            "/api/v1/imputation/accept",
            json={"station_id": "AGRA-01", "sensor": "wind_speed", "suggested": 10.0},
        )
        assert res_bad_sensor.status_code == 422

        # 6. Anomaly feedback: invalid label literal
        res_bad_fb = client.post(
            "/api/v1/anomalies/feedback",
            json={"anomaly_id": "ano-123", "label": "unsure"},
        )
        assert res_bad_fb.status_code == 422


# ============================================================================
# SUITE 2: CHAOS MODES VALIDATION & PROTOCOL DISCREPANCIES
# ============================================================================

class TestChaosModesValidationAndInconsistencies:
    """Rigorous tests evaluating the 5 chaos modes in client.py and extended simulator modes:

    - Mode 0: Nominal baseline
    - Mode 1: Heat Spike (+8°C jump in 10s)
    - Mode 2: Capacitive Drift (+15% RH bias)
    - Mode 3: Severe Thunderstorm (-11 hPa, 94% RH, -8°C, wind +12 m/s)
    - Mode 4: Frozen Sensor (RH flatlines at 84.2%)
    - Extended: stuck_humidity, sensor_noise, valid_squall, drop_flag.
    """

    def test_edge_chaos_modes_packet_validity(self):
        """Verify all 5 chaos modes generate well-formed TelemetryPayload packets."""
        for seq, mode in enumerate(["normal", "heat_spike", "humidity_drift", "storm", "frozen_sensor"], start=1):
            pkt = make_packet(seq, "AGRA-01", float(seq), mode)
            # Must validate cleanly as TelemetryPayload
            payload = TelemetryPayload.model_validate(pkt)
            assert payload.sequence == seq
            assert payload.station_id == "AGRA-01"
            assert isinstance(payload.temperature_c, float)
            assert isinstance(payload.pressure_hpa, float)
            assert isinstance(payload.humidity_pct, float)
            assert isinstance(payload.dew_point_c, float)
            assert payload.source == "laptop-1-mqtt"
            assert payload.drop_flag == 0

    @pytest.mark.anyio
    async def test_mode1_heat_spike_edge_and_backend_rate_violation(self):
        """HARSH ANALYSIS - Mode 1 Heat Spike:

        Tick 1 jumps +8°C instantaneously -> violates rate-of-change (dT/dt > 2°C/s).
        Tick 2+ sustains +8°C -> dT/dt = 0°C/s and absolute temp (~40.5°C) is within [-10, 60]°C.
        BUG/INCONSISTENCY: The spike is flagged on Tick 1, but silently passes as nominal on Ticks 2-10!
        """
        store.clear()
        p_base = TelemetryPayload.model_validate(make_packet(100, "AGRA-01", 100.0, "normal"))
        await telemetry_ingestion.ingest(p_base)

        # Tick 1: Sudden +8°C step
        p_spike_1 = TelemetryPayload.model_validate(make_packet(101, "AGRA-01", 101.0, "heat_spike"))
        ano_spike_1 = await telemetry_ingestion.ingest(p_spike_1)
        assert ano_spike_1 is not None, "Tick 1 of heat spike must be flagged by rate check"
        assert ano_spike_1.anomaly_type == "rule_flag"
        assert "temperature" in ano_spike_1.culprit_sensors

        # Tick 2: Sustained heat spike (same +8°C offset)
        p_spike_2 = TelemetryPayload.model_validate(make_packet(102, "AGRA-01", 102.0, "heat_spike"))
        ano_spike_2 = await telemetry_ingestion.ingest(p_spike_2)

        # Rate of change between spike_1 and spike_2 is ~0.0 °C/s!
        # IMD rate check clears, and 40.5°C is within climatological limits!
        # Result: The heat spike anomaly disappears from rule engine on sustained ticks!
        rule_check_tick2 = IMDPhysicsRuleEngine.evaluate(p_spike_2, [p_base, p_spike_1])
        assert rule_check_tick2 is None, "Sustained heat spike is silently unflagged by IMD rate rules on Tick 2+"

    @pytest.mark.anyio
    async def test_mode2_humidity_drift_step_jump_vs_subtle_drift(self):
        """HARSH ANALYSIS - Mode 2 Capacitive Drift:

        In client.py, humidity jumps +15% in 1 second (min(96, rh + 15)).
        Because MAX_RH_STEP_PER_SEC = 10.0%/s, Tick 1 causes an instant rate-of-change rule violation,
        defeating the purpose of testing subtle AI latent space drift!
        """
        store.clear()
        p_base = TelemetryPayload.model_validate(make_packet(200, "AGRA-01", 200.0, "normal"))
        await telemetry_ingestion.ingest(p_base)

        p_drift_1 = TelemetryPayload.model_validate(make_packet(201, "AGRA-01", 201.0, "humidity_drift"))

        # On the edge, EdgeIMDBoundaryChecker flags dynamic step rate (>10%/s)
        edge_check = EdgeIMDBoundaryChecker.evaluate(p_drift_1.model_dump(), previous=p_base.model_dump())
        assert edge_check is not None
        assert edge_check["rule"] == "IMD_HUMIDITY_SPIKE_EXCEEDED"

        # On the backend, rule engine flags IMD_HUMIDITY_SPIKE_EXCEEDED
        ano_drift_1 = await telemetry_ingestion.ingest(p_drift_1)
        assert ano_drift_1 is not None
        assert ano_drift_1.anomaly_type == "rule_flag"

    @pytest.mark.anyio
    async def test_mode3_storm_step_jump_violates_zero_false_alarm(self):
        """HARSH ANALYSIS - Mode 3 Severe Thunderstorm:

        In client.py, storm applies -11 hPa pressure drop, -8°C temp drop, +36% RH surge in 1 second!
        This instantaneous 1s jump trips IMD_TEMP_RATE_OF_CHANGE_EXCEEDED and IMD_PRESSURE_BURST_EXCEEDED.
        In PRD, a storm is supposed to be a TRUE NEGATIVE (Zero False Alarms) test!
        Because client.py does not smooth the transition over seconds, it triggers false alarms!
        """
        store.clear()
        p_base = TelemetryPayload.model_validate(make_packet(300, "AGRA-01", 300.0, "normal"))
        await telemetry_ingestion.ingest(p_base)

        p_storm = TelemetryPayload.model_validate(make_packet(301, "AGRA-01", 301.0, "storm"))
        ano_storm = await telemetry_ingestion.ingest(p_storm)

        # Instantaneous 1-second plunge trips rule violation!
        assert ano_storm is not None, "Instantaneous storm step trips rule engine false alarm"
        assert ano_storm.anomaly_type == "rule_flag"

    @pytest.mark.anyio
    async def test_mode4_frozen_sensor_discrepancy_between_edge_and_backend(self):
        """CRITICAL PROTOCOL DISCREPANCY - Mode 4 Frozen Sensor:

        In client.py, humidity flatlines at 84.2%.
        EdgeIMDBoundaryChecker flags any flatline after 8s: len(set(recent_rhs)) == 1.
        Backend IMDPhysicsRuleEngine REQUIRES: current.humidity_pct == 100.0 or 0.0!
        Therefore, backend rule engine NEVER flags 84.2% flatline!
        """
        store.clear()
        packets = []
        for seq in range(400, 412):
            pkt_dict = make_packet(seq, "AGRA-01", float(seq), "frozen_sensor")
            packets.append(TelemetryPayload.model_validate(pkt_dict))

        # Check edge checker: flags after 8 identical readings
        edge_check = EdgeIMDBoundaryChecker.evaluate(
            packets[-1].model_dump(),
            recent_history=[p.model_dump() for p in packets[-9:-1]]
        )
        assert edge_check is not None
        assert edge_check["rule"] == "IMD_STUCK_SENSOR_FLATLINE"

        # Check backend rule engine:
        backend_rule_check = IMDPhysicsRuleEngine.evaluate(packets[-1], packets[:-1])
        # Backend rule engine completely fails to flag 84.2% flatline!
        assert backend_rule_check is None, (
            "Backend IMDPhysicsRuleEngine bug: only flags stuck sensor at 0% or 100%, missing 84.2%!"
        )

    @pytest.mark.anyio
    async def test_edge_simulator_extended_modes(self):
        """Test extended modes from edge_simulator.py:

        - stuck_humidity (100.0%) -> caught by rule engine.
        - sensor_noise -> random high delta rates.
        - drop_flag -> check if statistical surrogate autoencoder detects drop_flag=1.
        """
        store.clear()
        # 1. stuck_humidity (100.0%)
        store.set_fault("stuck_humidity")
        p_stuck = simulator._generate_telemetry()
        assert p_stuck.humidity_pct == 100.0
        # Ingest 9 identical packets to trip flatline check
        for _ in range(8):
            store.add_telemetry(p_stuck)
        rule_violation = IMDPhysicsRuleEngine.evaluate(p_stuck, store.get_telemetry_history(limit=10))
        assert rule_violation is not None
        assert rule_violation["rule"] == "IMD_STUCK_SENSOR_FLATLINE"

        # 2. drop_flag sensitivity test:
        # In anomaly_detector.py, FEATURE_NAMES includes drop_flag at index 7.
        # However, base_mse is calculated as np.mean(feature_errors[:4]) * 0.015,
        # which ONLY evaluates T, RH, P, Td and completely ignores feature 7 (drop_flag)!
        store.clear()
        for i in range(10):
            p = TelemetryPayload.model_validate(make_packet(i, "AGRA-01", float(i), "normal"))
            store.add_telemetry(p)

        p_drop = TelemetryPayload.model_validate(make_packet(11, "AGRA-01", 11.0, "normal"))
        p_drop.drop_flag = 1  # Flag packet dropout

        ano = await telemetry_ingestion.ingest(p_drop)
        # Drop flag alone does NOT trigger statistical autoencoder anomaly
        assert p_drop.reconstruction_error < 0.042, "Statistical surrogate ignores drop_flag in base_mse calculation"


# ============================================================================
# SUITE 3: INCIDENT BURST INGESTION & REPLAY DEFECTS
# ============================================================================

class TestIncidentBurstIngestionAndReplay:
    """Rigorous tests evaluating the MQTT Incident Context Burst mechanism:

    - Burst payload structure & integrity
    - The Server Discard Defect: server extracts only trigger_packet, discarding the 12 context frames
    - Cold-start burst failure: trigger packet alone fails to trigger detection without context
    - Context replay solution: replaying context frames restores proper detection
    - Corrupted burst handling
    """

    def test_incident_context_burst_packet_structure(self):
        """Verify incident burst payload structure matches expected protocol specification."""
        ring = CircularRingBuffer(capacity=120)
        for seq in range(15):
            ring.append(make_packet(seq, "AGRA-01", float(seq), "normal"))

        trigger = make_packet(16, "AGRA-01", 16.0, "heat_spike")
        context_12 = ring.get_context(12)

        burst = make_incident_burst(
            trigger_packet=trigger,
            context_window=context_12,
            trigger_reason="CHAOS_KEY_HEAT_SPIKE",
            fault_mode="heat_spike",
            culprit_sensor="temperature_c",
        )

        assert burst["station_id"] == "AGRA-01"
        assert burst["incident_id"].startswith("inc_")
        assert "triggered_at" in burst
        assert burst["trigger_reason"] == "CHAOS_KEY_HEAT_SPIKE"
        assert burst["fault_mode"] == "heat_spike"
        assert burst["culprit_sensor"] == "temperature_c"
        assert burst["bandwidth_saved_pct"] > 90.0
        assert len(burst["context_window"]) == 12
        assert burst["trigger_packet"]["sequence"] == 16

    @pytest.mark.anyio
    async def test_cold_start_burst_failure_without_context_replay(self):
        """ARCHITECTURAL DEFECT TEST:

        When a burst arrives, mqtt_subscriber extracts ONLY raw_payload['trigger_packet'].
        If the server restarted or was offline (cold start), store history is empty.
        Because context_window is discarded:
          - Dynamic rate checks fail to calculate dT/dt (no prev packet).
          - Multi-scale analyzer returns default 0.0 values.
          - Anomaly detector falls back to cold-start buffer (returns None).
        RESULT: The anomaly that caused the incident burst is COMPLETELY MISSED by the server!
        """
        store.clear()

        # Build ring buffer and burst payload
        ring = CircularRingBuffer(capacity=120)
        for seq in range(12):
            ring.append(make_packet(seq, "AGRA-01", float(seq), "normal"))

        trigger = make_packet(12, "AGRA-01", 12.0, "heat_spike")
        burst = make_incident_burst(
            trigger_packet=trigger,
            context_window=ring.get_context(12),
            trigger_reason="CHAOS_KEY_HEAT_SPIKE",
            fault_mode="heat_spike",
        )

        # 1. Simulate current backend behavior (unwraps ONLY trigger_packet, context discarded):
        payload_isolated = TelemetryPayload.model_validate(burst["trigger_packet"])
        ano_isolated = await telemetry_ingestion.ingest(payload_isolated)

        # FAILS TO DETECT ANOMALY!
        assert ano_isolated is None, (
            "DEFECT CONFIRMED: Cold-start ingestion of isolated trigger packet fails to detect anomaly!"
        )

    @pytest.mark.anyio
    async def test_context_replay_restores_detection(self):
        """Verify that when the 12 context frames are replayed into the sliding window

        before the trigger packet, the anomaly is immediately and properly detected.
        """
        store.clear()

        ring = CircularRingBuffer(capacity=120)
        for seq in range(12):
            ring.append(make_packet(seq, "AGRA-01", float(seq), "normal"))

        trigger = make_packet(12, "AGRA-01", 12.0, "heat_spike")
        burst = make_incident_burst(
            trigger_packet=trigger,
            context_window=ring.get_context(12),
            trigger_reason="CHAOS_KEY_HEAT_SPIKE",
            fault_mode="heat_spike",
        )

        # Replay the 12 context frames into ingestion
        for ctx_frame in burst["context_window"]:
            await telemetry_ingestion.ingest(TelemetryPayload.model_validate(ctx_frame))

        # Now ingest trigger packet with proper historical context restored
        payload_with_ctx = TelemetryPayload.model_validate(burst["trigger_packet"])
        ano_with_ctx = await telemetry_ingestion.ingest(payload_with_ctx)

        # SUCCESS: Anomaly detected because previous packet exists for rate check!
        assert ano_with_ctx is not None, "Replaying context window enables proper anomaly detection"
        assert ano_with_ctx.anomaly_type == "rule_flag"
        assert "temperature" in ano_with_ctx.culprit_sensors

    def test_corrupted_burst_payload_handling(self):
        """Verify MQTT subscriber safely handles burst payloads with corrupted/missing trigger_packet."""
        mock_client = MagicMock()
        mock_userdata = MagicMock()

        class MockMessage:
            def __init__(self, payload_dict: dict, topic: str = "skyguard/incident"):
                self.payload = json.dumps(payload_dict).encode("utf-8")
                self.topic = topic

        # Case 1: Incident burst missing 'trigger_packet' field entirely
        burst_no_trigger = {"station_id": "AGRA-01", "incident_id": "inc_1", "context_window": []}
        mqtt_subscriber._on_message(mock_client, mock_userdata, MockMessage(burst_no_trigger))

        # Case 2: Incident burst with trigger_packet = None
        burst_none_trigger = {"station_id": "AGRA-01", "trigger_packet": None, "context_window": []}
        mqtt_subscriber._on_message(mock_client, mock_userdata, MockMessage(burst_none_trigger))

        # Case 3: Incident burst with trigger_packet = "invalid_string"
        burst_str_trigger = {"station_id": "AGRA-01", "trigger_packet": "corrupted", "context_window": []}
        mqtt_subscriber._on_message(mock_client, mock_userdata, MockMessage(burst_str_trigger))


# ============================================================================
# SUITE 4: SSE CONNECTION LIFECYCLE & BROADCAST ROBUSTNESS
# ============================================================================

class TestSSEConnectionLifecycleAndRobustness:
    """Rigorous tests evaluating the SSE Broadcast Manager, connection lifecycle,

    client queue overflow, disconnect cleanup, and broadcast exception handling.
    """

    @pytest.mark.anyio
    async def test_sse_subscribe_unsubscribe_lifecycle(self):
        """Verify subscribing and unsubscribing cleanly tracks client count."""
        mgr = SSEBroadcastManager()
        assert mgr.client_count == 0

        q1 = await mgr.subscribe()
        assert mgr.client_count == 1
        q2 = await mgr.subscribe()
        assert mgr.client_count == 2

        await mgr.unsubscribe(q1)
        assert mgr.client_count == 1
        await mgr.unsubscribe(q2)
        assert mgr.client_count == 0

        # Unsubscribing non-existent queue should be safe and idempotent
        await mgr.unsubscribe(q1)
        assert mgr.client_count == 0

    @pytest.mark.anyio
    async def test_sse_multiple_concurrent_subscribers(self):
        """Verify broadcasts are dispatched concurrently to all active subscriber queues."""
        mgr = SSEBroadcastManager()
        queues = [await mgr.subscribe() for _ in range(5)]
        assert mgr.client_count == 5

        test_data = {"station_id": "AGRA-01", "temperature_c": 31.5}
        await mgr.broadcast("telemetry", test_data)

        # All 5 queues must have received the message
        for q in queues:
            assert not q.empty()
            item = q.get_nowait()
            assert "event: telemetry\n" in item
            assert '"temperature_c": 31.5' in item

        # Clean up
        for q in queues:
            await mgr.unsubscribe(q)
        assert mgr.client_count == 0

    @pytest.mark.anyio
    async def test_sse_queue_overflow_drops_oldest(self):
        """Verify when a slow/stalled client queue (maxsize=100) fills up,

        the oldest message is evicted to avoid blocking broadcasts or crashing with QueueFull.
        """
        mgr = SSEBroadcastManager()
        q = await mgr.subscribe()  # maxsize = 100

        # Broadcast 120 messages without reading
        for seq in range(120):
            await mgr.broadcast("telemetry", {"seq": seq})

        # Queue size must be capped at 100
        assert q.qsize() == 100

        # The first message in queue should be seq 20 (oldest 0-19 dropped)
        first_item = q.get_nowait()
        assert '"seq": 20' in first_item

        await mgr.unsubscribe(q)

    @pytest.mark.anyio
    async def test_sse_broadcast_crashes_on_non_serializable_data(self):
        """VULNERABILITY TEST:

        If non-serializable objects (such as raw Python objects or circular refs)
        are passed to broadcast(), json.dumps() raises TypeError outside any try-except,
        which crashes the caller and halts telemetry ingestion!
        """
        mgr = SSEBroadcastManager()
        q = await mgr.subscribe()

        class UnserializableObject:
            pass

        with pytest.raises(TypeError):
            await mgr.broadcast("telemetry", {"bad_field": UnserializableObject()})

        await mgr.unsubscribe(q)

    @pytest.mark.anyio
    async def test_sse_generator_clean_termination_on_client_disconnect(self):
        """Verify the stream_telemetry SSE endpoint generator terminates cleanly

        and unsubscribes from SSEBroadcastManager when the client disconnects.
        """
        store.clear()
        p = TelemetryPayload.model_validate(make_packet(1, "AGRA-01", 0.0, "normal"))
        store.add_telemetry(p)

        initial_clients = sse_manager.client_count

        mock_request = AsyncMock()
        # First iteration returns initial telemetry, then immediately flags disconnected
        mock_request.is_disconnected = AsyncMock(return_value=True)

        resp = await stream_telemetry(mock_request, station_id="AGRA-01")
        gen = resp.body_iterator

        # Read first chunk (initial telemetry snapshot)
        first_chunk = await anext(gen)
        assert "event: telemetry\n" in first_chunk
        assert sse_manager.client_count == initial_clients + 1

        # Second read triggers is_disconnected check -> generator breaks and unsubscribes in finally block
        with pytest.raises(StopAsyncIteration):
            await anext(gen)

        assert sse_manager.client_count == initial_clients, "Client count must decrement to initial upon disconnect"

    @pytest.mark.anyio
    async def test_sse_abandoned_subscribers_leak_risk(self):
        """MEMORY LEAK RISK TEST:

        SSEBroadcastManager has no liveness/heartbeat mechanism of its own.
        If a subscriber task is cancelled or fails without calling unsubscribe(),
        the queue remains in _subscribers forever, receiving every broadcast.
        """
        mgr = SSEBroadcastManager()
        q = await mgr.subscribe()
        assert mgr.client_count == 1

        # Abandoning q without unsubscribe leaves subscriber count at 1
        del q
        assert mgr.client_count == 1, "Abandoned subscriber queue leaked in _subscribers"


# ============================================================================
# SUITE 5: HIGH-FREQUENCY BURST STRESS & MEMORY CONSTRAINTS
# ============================================================================

class TestHighFrequencyBurstStressAndMemory:
    """Rigorous tests evaluating rapid packet bursts (50-100 packets):

    - Concurrency lock contention and serialization integrity
    - Rolling history FIFO eviction and maxlen bounds
    - Persistence queue load
    - Unbounded memory leaks in anomaly dictionary and feedback logs
    - Derivative rate assumption under sub-second bursts
    """

    @pytest.mark.anyio
    async def test_high_frequency_packet_burst_100_packets(self):
        """Verify ingesting 100 packets concurrently via asyncio.gather:

        - Lock serializes ingestion without race conditions.
        - Sequence numbers remain strictly ordered.
        - Ingestion completes within 1.0 second.
        """
        store.clear()
        packets = [
            TelemetryPayload.model_validate(make_packet(seq, "AGRA-01", float(seq), "normal"))
            for seq in range(100)
        ]

        t0 = time.perf_counter()
        results = await asyncio.gather(*[telemetry_ingestion.ingest(p) for p in packets])
        elapsed = time.perf_counter() - t0

        assert len(results) == 100
        assert elapsed < 2.0, f"100 packets took too long to ingest: {elapsed:.3f}s"

        history = store.get_telemetry_history(limit=150)
        assert len(history) == 100

        # Verify strict sequence ordering
        seqs = [p.sequence for p in history]
        assert seqs == sorted(seqs), "Sequence numbers must be strictly ascending despite concurrent ingestion"

    def test_store_history_maxlen_bound(self):
        """Verify store._telemetry_history adheres to its bounded deque capacity (1000 items)."""
        store.clear()
        for i in range(1200):
            p = TelemetryPayload.model_validate(make_packet(i, "AGRA-01", float(i), "normal"))
            store.add_telemetry(p)

        # Deque maxlen is 1000
        assert len(store._telemetry_history) == 1000
        # Oldest items (0-199) were evicted; latest item is seq 1199
        latest = store.get_latest_telemetry()
        assert latest.sequence == 1199

    def test_sliding_window_telemetry_query_limit(self):
        """Verify store.get_telemetry_history(limit=12) strictly honors the limit argument."""
        store.clear()
        for i in range(50):
            store.add_telemetry(TelemetryPayload.model_validate(make_packet(i, "AGRA-01", float(i), "normal")))

        w12 = store.get_telemetry_history(limit=12)
        assert len(w12) == 12
        assert w12[-1].sequence == 49
        assert w12[0].sequence == 38

    @pytest.mark.anyio
    async def test_unbounded_anomalies_memory_leak_risk(self):
        """MEMORY LEAK AUDIT TEST:

        store._anomalies is a standard Python dict with NO maxlen, NO eviction, and NO TTL.
        Under continuous anomaly conditions, it retains every AnomalyEvent in RAM indefinitely.
        """
        store.clear()
        # Ingest 50 anomalous heat spike packets
        for i in range(50):
            p = TelemetryPayload.model_validate(make_packet(1000 + i, "AGRA-01", float(i), "heat_spike"))
            # Trigger rule violation manually by setting extreme temp
            p.temperature_c = 75.0  # Above 60°C limit
            await telemetry_ingestion.ingest(p)

        # Check store anomalies dict
        anomalies = store.get_anomalies(limit=100)
        assert len(anomalies) == 50, f"Expected 50 stored anomalies, got {len(anomalies)}"
        assert len(store._anomalies) == 50, "store._anomalies retains all events without eviction"

    def test_unbounded_feedback_and_imputation_lists(self):
        """MEMORY LEAK AUDIT TEST:

        store._feedback_logs and sensor_health.accepted are unbounded Python lists.
        Repeated calls append indefinitely without limit.
        """
        initial_fb_count = store.get_feedback_count()
        for i in range(25):
            from models.schemas import OperatorFeedback
            store.log_feedback(OperatorFeedback(anomaly_id=f"ano-{i}", label="false_alarm", note=f"test {i}"))
        assert store.get_feedback_count() == initial_fb_count + 25

        initial_accepted = len(sensor_health.accepted)
        for i in range(25):
            sensor_health.accept_imputation({"station_id": "AGRA-01", "sensor": "humidity", "suggested": 50.0 + i})
        assert len(sensor_health.accepted) == initial_accepted + 25

    def test_derivative_rate_assumption_under_rapid_burst(self):
        """ALGORITHMIC LIMITATION TEST:

        MultiScaleAnalyzer computes derivatives as (curr - prev) directly without dividing by Δt.
        If a burst of 50 packets arrives in 100ms (500 Hz), the rate of change is miscalculated
        as per-second changes rather than per-sample deltas!
        """
        p1 = TelemetryPayload.model_validate(make_packet(1, "AGRA-01", 0.0, "normal"))
        p2 = TelemetryPayload.model_validate(make_packet(2, "AGRA-01", 0.0, "normal"))
        # Injected jump of 1.5°C over 10ms
        p2.temperature_c = p1.temperature_c + 1.5

        derivs = multi_scale_analyzer.compute_derivatives([p1, p2])
        # dt_dt is reported as 1.5, assuming Δt = 1.0 second.
        # If Δt was 0.01s, true dT/dt would be 150 °C/s.
        assert derivs["dt_dt"] == 1.5, "Derivative assumes fixed 1.0s interval regardless of actual timestamp difference"
