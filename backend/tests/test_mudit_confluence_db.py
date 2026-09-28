import os
import sys
import asyncio
import time
from datetime import datetime, timezone

# Ensure backend is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from data.db import (
    init_db,
    insert_telemetry,
    insert_anomaly,
    insert_maintenance_prediction,
    insert_feedback,
    update_anomaly_status,
    get_recent_telemetry,
    get_session,
    TelemetryRecord,
    AnomalyIncident,
    MaintenancePrediction,
    OperatorFeedbackRecord,
)
from data.store import store
from models.schemas import TelemetryPayload, AnomalyEvent, OperatorFeedback
from services.confluence_engine import confluence_engine, ConfluenceEngine
from sqlalchemy import select


def test_confluence_decision_matrix_rules():
    """Verify deterministic 4-quadrant Confluence Decision Matrix rules."""
    engine = ConfluenceEngine()

    # Quadrant 1: High Weather (>=0.70), Low Defect (<0.30) -> Natural Weather Event
    res_weather = engine.evaluate_confluence(0.95, 0.05, "none")
    assert res_weather.classification == "Natural Weather Event"
    assert res_weather.operator_alert is False
    assert res_weather.severity == "Nominal"

    # Quadrant 2: Low Weather (<0.30), High Defect (>=0.70) -> Sensor Defect
    res_defect = engine.evaluate_confluence(0.05, 0.94, "capacitive_drift")
    assert res_defect.classification == "Sensor Defect"
    assert res_defect.operator_alert is True
    assert res_defect.severity == "High"
    assert res_defect.confidence_score == 92.1

    # Quadrant 3: High Weather (>=0.70), High Defect (>=0.70) -> Compound Event
    res_compound = engine.evaluate_confluence(0.85, 0.82, "sensor_noise")
    assert res_compound.classification == "Compound Event"
    assert res_compound.operator_alert is True
    assert res_compound.severity == "Warning"

    # Quadrant 4: Intermediate / Uncertain -> Uncertain Anomaly
    res_uncertain = engine.evaluate_confluence(0.45, 0.50, "none")
    assert res_uncertain.classification == "Uncertain Anomaly"
    assert res_uncertain.operator_alert is False
    assert res_uncertain.severity == "Moderate"

    print("PASS: Confluence Decision Matrix all 4 quadrants verified.")


def test_confluence_confidence_scoring():
    """Verify confidence scoring formula."""
    engine = ConfluenceEngine()

    # Clear separation
    conf_clear = engine.compute_confidence(0.05, 0.94)
    assert 90.0 <= conf_clear <= 95.0

    # Compound ambiguity: models clash
    conf_conflict = engine.compute_confidence(0.75, 0.75)
    assert conf_conflict < conf_clear

    print("PASS: Confluence confidence scoring formula verified.")


async def test_database_layer_async():
    """Verify SQLite/PostgreSQL schema initialization and asynchronous operations."""
    await init_db()

    # 1. Telemetry insert
    now_iso = datetime.now(timezone.utc).isoformat()
    t_id = await insert_telemetry({
        "station_id": "AGRA-01",
        "timestamp": now_iso,
        "temperature_c": 33.2,
        "pressure_hpa": 1004.8,
        "humidity_pct": 62.0,
        "dew_point_c": 21.0,
        "sequence": 101,
        "source": "unit-test",
    })
    assert t_id is not None

    # 2. Anomaly insert
    a_id = await insert_anomaly(
        {
            "anomaly_id": "test-ano-001",
            "detected_at": now_iso,
            "station_id": "AGRA-01",
            "anomaly_type": "ai_anomaly",
            "severity_score": 0.88,
            "culprit_sensors": ["humidity"],
            "diagnostic_message": "Capacitive drift test anomaly",
            "reconstruction_error": 0.052,
        },
        confluence_decision="Sensor Defect",
        confidence_score=92.1,
    )
    assert a_id is not None

    # 3. Anomaly update
    updated = await update_anomaly_status(
        "test-ano-001", "resolved", resolution_note="Recalibrated by technician"
    )
    assert updated is True

    # 4. Maintenance prediction insert
    m_id = await insert_maintenance_prediction({
        "station_id": "AGRA-01",
        "timestamp": now_iso,
        "sensor": "humidity",
        "drift_value": 2.4,
        "status": "At Risk",
        "days_to_recalibration": 12,
        "tolerance_threshold": 2.0,
        "daily_drift_rate": 0.08,
    })
    assert m_id is not None

    # 5. Operator feedback insert
    f_id = await insert_feedback({
        "anomaly_id": "test-ano-001",
        "label": "confirmed_fault",
        "note": "Verified sensor drift on site",
    })
    assert f_id is not None

    # Query verification
    session = await get_session()
    async with session:
        t_rows = (await session.execute(select(TelemetryRecord))).scalars().all()
        a_rows = (await session.execute(select(AnomalyIncident))).scalars().all()
        m_rows = (await session.execute(select(MaintenancePrediction))).scalars().all()
        f_rows = (await session.execute(select(OperatorFeedbackRecord))).scalars().all()

        assert len(t_rows) >= 1
        assert len(a_rows) >= 1
        assert len(m_rows) >= 1
        assert len(f_rows) >= 1

        # Check confluence fields
        ano = a_rows[-1]
        assert ano.confluence_decision == "Sensor Defect"
        assert ano.confidence_score == 92.1
        assert ano.status == "resolved"

    print("PASS: Database layer schema and CRUD operations verified.")


def test_store_non_blocking_persistence():
    """Verify that adding records to store never blocks in-memory state."""
    start_time = time.perf_counter()

    for i in range(20):
        p = TelemetryPayload(
            timestamp=datetime.now(timezone.utc).isoformat(),
            temperature_c=30.0 + i * 0.1,
            pressure_hpa=1005.0,
            humidity_pct=55.0,
            dew_point_c=20.0,
            sequence=1000 + i,
        )
        store.add_telemetry(p)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    # In-memory enqueue should be sub-50ms for 20 payloads
    assert elapsed_ms < 100.0, f"Memory operations took too long: {elapsed_ms}ms"

    assert store.get_latest_telemetry().sequence == 1019
    store.flush(2.0)
    print(f"PASS: Non-blocking store persistence verified (20 items enqueued in {elapsed_ms:.2f}ms).")


if __name__ == "__main__":
    test_confluence_decision_matrix_rules()
    test_confluence_confidence_scoring()
    asyncio.run(test_database_layer_async())
    test_store_non_blocking_persistence()
    print("\nALL MUDIT (Task 4.1 & Task 4.2) TESTS PASSED SUCCESSFULLY!")
