"""
End-to-End System Integration Test (Hanswarup — TASKS.md Task 1.4)

Verifies full packet flow across all architectural layers:
  Ingestion
    ➔ IMD Physics Rules
    ➔ Multi-Scale Multivariate Analyzer (Layer 2.1)
    ➔ Confluence Decision Matrix Engine (Layer 2.3)
    ➔ Predictive Maintenance & Drift Tracker (Layer 3.4)
    ➔ Imputation & Sensor Repair (Layer 3.5)
    ➔ Asynchronous Database Persistence (Supabase + SQLite fallback)
    ➔ FastAPI REST / Health endpoints
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from data.db import (
    init_db,
    get_session,
    TelemetryRecord,
    AnomalyIncident,
    get_recent_telemetry,
)
from data.store import store
from models.schemas import TelemetryPayload, ImputationAcceptRequest
from services.multi_scale_analyzer import multi_scale_analyzer, MultiScaleAnalyzer
from services.confluence_engine import confluence_engine
from services.telemetry_ingestion import telemetry_ingestion
from main import app
from sqlalchemy import select


@pytest.fixture(autouse=True)
def setup_test_db():
    """Ensure database schema is initialized and store is clean before each test."""
    store.clear()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())
    yield
    store.clear()
    loop.close()


def make_test_payload(
    seq: int,
    temp: float = 30.0,
    rh: float = 60.0,
    pres: float = 1010.0,
    dew: float = 21.0,
    wind: float = 2.5,
    recon_err: float = 0.0142,
) -> TelemetryPayload:
    """Helper to construct a valid TelemetryPayload."""
    return TelemetryPayload(
        station_id="AGRA-01",
        timestamp=datetime.now(timezone.utc).isoformat(),
        temperature_c=temp,
        pressure_hpa=pres,
        humidity_pct=rh,
        dew_point_c=dew,
        wind_speed_ms=wind,
        wind_dir_deg=180.0,
        solar_radiation_wm2=450.0,
        sequence=seq,
        source="e2e-test",
        reconstruction_error=recon_err,
    )


def test_multi_scale_analyzer_isolated():
    """Task 1.3: Verify isolated Multi-Scale Multivariate Analyzer functionality."""
    analyzer = MultiScaleAnalyzer()

    # 1. Empty window defaults
    res_empty = analyzer.analyze_window([])
    assert res_empty["dT_dt"] == 0.0
    assert res_empty["dP_dt"] == 0.0
    assert res_empty["dRH_dt"] == 0.0
    assert res_empty["d2P_dt2"] == 0.0
    assert res_empty["rho_t_rh"] == 0.0
    assert res_empty["decoupling_flag"] is False

    # 2. Synthetic normal diurnal window (Temp rises, RH falls -> negative correlation)
    normal_window = []
    for i in range(12):
        t = 25.0 + i * 0.5   # 25.0 -> 30.5
        rh = 70.0 - i * 1.5  # 70.0 -> 53.5
        p = 1013.0 - (i % 2) * 0.1
        normal_window.append({"temperature_c": t, "humidity_pct": rh, "pressure_hpa": p})

    res_normal = analyzer.analyze_window(normal_window)
    assert res_normal["dT_dt"] > 0.0
    assert res_normal["dRH_dt"] < 0.0
    assert res_normal["rho_t_rh"] < -0.70  # Strong negative thermodynamic correlation
    assert res_normal["decoupling_flag"] is False

    # 3. Decoupling anomaly window (Temp rises AND RH rises without pressure plunge)
    decoupled_window = []
    for i in range(12):
        t = 25.0 + i * 0.5
        rh = 50.0 + i * 1.5  # RH surging with T!
        p = 1012.0           # Static pressure (abs(dP/dt) < 2.0)
        decoupled_window.append({"temperature_c": t, "humidity_pct": rh, "pressure_hpa": p})

    res_decoupled = analyzer.analyze_window(decoupled_window)
    assert res_decoupled["rho_t_rh"] > 0.0
    assert res_decoupled["decoupling_flag"] is True
    assert len(res_decoupled["features_vector"]) == 10


@pytest.mark.anyio
async def test_e2e_nominal_weather_pipeline():
    """Verify nominal weather packet flow through ingestion, analyzer, confluence, maintenance, and DB."""
    store.clear()
    for i in range(5):
        p = make_test_payload(
            seq=100 + i,
            temp=28.0 + (i * 0.1),
            rh=65.0 - (i * 0.2),
            pres=1012.0,
            dew=20.5,
        )
        anomaly = await telemetry_ingestion.ingest(p)
        assert anomaly is None

        # Verify Layer 2.1 Multi-Scale Analyzer attached
        assert p.physical_features is not None
        assert "dT_dt" in p.physical_features
        assert "dP_dt" in p.physical_features
        assert "rho_t_rh" in p.physical_features
        assert p.physical_features["decoupling_flag"] is False

        # Verify Layer 2.3 Confluence attached
        assert p.confluence is not None
        assert p.confluence["operator_alert"] is False

        # Verify Layer 3.4 Maintenance & Imputation attached
        assert p.maintenance is not None
        assert p.imputation is not None
        assert p.imputation["active"] is False

    # Drain persistence queue to SQLite
    store.flush(timeout=3.0)

    # Verify DB persistence
    recent_db = await get_recent_telemetry(limit=10)
    assert len(recent_db) >= 5


@pytest.mark.anyio
async def test_e2e_squall_zero_false_alarm_pipeline():
    """
    Verify high-energy atmospheric event (severe thunderstorm / squall):
    - Plunging pressure, soaring humidity, cooling temperature
    - Multi-scale analyzer calculates steep derivatives
    - Confluence engine classifies as 'Natural Weather Event'
    - ZERO False Alarms raised to operator
    - Maintenance drift tracking automatically pauses
    """
    store.clear()
    p_base = make_test_payload(seq=200, temp=32.0, rh=50.0, pres=1012.0, wind=3.0)
    await telemetry_ingestion.ingest(p_base)

    # Squall packet: rapid pressure drop of -4.5 hPa, temp drop of -3.5 C, RH surge of +28%
    p_squall = make_test_payload(
        seq=201,
        temp=28.5,
        rh=78.0,
        pres=1007.5,
        dew=24.0,
        wind=13.5,
    )
    anomaly = await telemetry_ingestion.ingest(p_squall)

    # Check multi-scale physical features
    assert p_squall.physical_features is not None
    assert p_squall.physical_features["dP_dt"] <= -3.0
    assert p_squall.physical_features["dRH_dt"] >= 15.0

    # Check confluence decision
    assert p_squall.confluence is not None
    assert p_squall.confluence["classification"] == "Natural Weather Event"
    assert p_squall.confluence["operator_alert"] is False
    assert p_squall.confluence["p_weather"] >= 0.70

    # Check weather pause in sensor health
    assert p_squall.weather is not None
    assert p_squall.weather["event"] is True or p_squall.weather["cooldown"] is True

    # Check DB write
    store.flush(timeout=3.0)


@pytest.mark.anyio
async def test_e2e_capacitive_drift_defect_and_imputation():
    """
    Verify capacitive sensor drift failure:
    - Humidity increases without pressure change, causing thermodynamic decoupling
    - Multi-scale analyzer triggers decoupling_flag
    - Confluence engine flags 'Sensor Defect' with high confidence
    - Operator alert is RAISED
    - Imputation module generates corrected value for humidity
    - Anomaly incident recorded in DB
    """
    store.clear()
    # Feed 8 baseline packets with steadily warming temperature and rising humidity
    for i in range(8):
        pkt = make_test_payload(
            seq=300 + i,
            temp=32.0 + (i * 0.2),
            rh=55.0 + (i * 1.5),
            pres=1005.0,
            dew=22.0,
            recon_err=0.015,
        )
        await telemetry_ingestion.ingest(pkt)

    # Injected capacitive jump in RH (+12% jump in 1 second, exceeding MAX_RH_STEP_PER_SEC)
    fault_pkt = make_test_payload(
        seq=308,
        temp=33.6,
        rh=79.5,
        pres=1005.0,
        dew=24.0,
        recon_err=0.048,
    )
    anomaly = await telemetry_ingestion.ingest(fault_pkt)

    # Multi-scale analyzer detects decoupling
    assert fault_pkt.physical_features["decoupling_flag"] is True
    assert fault_pkt.physical_features["rho_t_rh"] > 0.0

    # Confluence Engine detects Sensor Defect
    assert fault_pkt.confluence["classification"] == "Sensor Defect"
    assert fault_pkt.confluence["operator_alert"] is True
    assert fault_pkt.confluence["confidence_score"] >= 80.0

    # Imputation module active for humidity sensor
    assert fault_pkt.imputation is not None
    assert fault_pkt.imputation["active"] is True
    assert fault_pkt.imputation["sensor"] == "humidity"
    assert fault_pkt.imputation["suggested"] is not None

    store.flush(timeout=3.0)

    # Verify incident persisted in DB
    session = await get_session()
    async with session:
        result = await session.execute(
            select(AnomalyIncident).order_by(AnomalyIncident.id.desc()).limit(5)
        )
        incidents = result.scalars().all()
        assert len(incidents) > 0
        defect_incidents = [inc for inc in incidents if inc.confluence_decision == "Sensor Defect"]
        assert len(defect_incidents) > 0


@pytest.mark.anyio
async def test_e2e_frozen_sensor_defect_pipeline():
    """
    Verify frozen sensor flatline:
    - 6 identical humidity readings while ambient temperature varies
    - Confluence engine flags defect_type == 'frozen_value' and 'Sensor Defect'
    """
    store.clear()
    for i in range(7):
        pkt = make_test_payload(
            seq=400 + i,
            temp=30.0 + (i * 0.4),
            rh=84.20,  # Exact flatline
            pres=1010.0,
            recon_err=0.045,
        )
        await telemetry_ingestion.ingest(pkt)

    assert pkt.confluence["classification"] == "Sensor Defect"
    assert pkt.confluence["defect_type"] == "frozen_value"
    assert pkt.confluence["operator_alert"] is True


def test_e2e_fastapi_rest_endpoints():
    """Verify FastAPI REST API endpoints using TestClient."""
    client = TestClient(app)

    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Latest telemetry
    res_telemetry = client.get("/api/v1/telemetry/latest")
    assert res_telemetry.status_code == 200

    # 3. Telemetry overview
    res_overview = client.get("/api/v1/telemetry/overview")
    assert res_overview.status_code == 200
    assert res_overview.json()["station_id"] == "AGRA-01"

    # 4. Maintenance state
    res_maint = client.get("/api/v1/maintenance")
    assert res_maint.status_code == 200
    assert "maintenance" in res_maint.json()
    assert "humidity" in res_maint.json()["maintenance"]

    # 5. Accept Imputation POST
    req_body = {
        "station_id": "AGRA-01",
        "sensor": "humidity",
        "suggested": 52.3,
        "reported": 84.2,
        "sequence": 501,
        "method": "e2e_test",
    }
    res_impute = client.post("/api/v1/imputation/accept", json=req_body)
    assert res_impute.status_code == 200
    assert res_impute.json()["status"] == "success"
    assert res_impute.json()["record"]["suggested"] == 52.3
