import os
import json
import logging
import threading
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Text, select, update, desc, text

# Load environment variables
base_dir = Path(__file__).resolve().parent
for p in [base_dir, base_dir.parent, base_dir.parent.parent]:
    env_file = p / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

logger = logging.getLogger("skyguard.db")

DEFAULT_SQLITE_URL = "sqlite+aiosqlite:///./skyguard.db"


class Base(DeclarativeBase):
    pass


class TelemetryRecord(Base):
    """Stores 1-second temperature, humidity, and pressure readings."""
    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(64), index=True, default="AGRA-01")
    timestamp: Mapped[str] = mapped_column(String(64), index=True)
    temperature_c: Mapped[float] = mapped_column(Float)
    pressure_hpa: Mapped[float] = mapped_column(Float)
    humidity_pct: Mapped[float] = mapped_column(Float)
    dew_point_c: Mapped[float] = mapped_column(Float)
    wind_speed_ms: Mapped[float] = mapped_column(Float, default=2.5)
    wind_dir_deg: Mapped[float] = mapped_column(Float, default=180.0)
    solar_radiation_wm2: Mapped[float] = mapped_column(Float, default=450.0)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(64), default="edge-simulator")
    drop_flag: Mapped[int] = mapped_column(Integer, default=0)
    reconstruction_error: Mapped[float] = mapped_column(Float, default=0.0142)
    inference_time_ms: Mapped[float] = mapped_column(Float, default=2.4)
    created_at: Mapped[str] = mapped_column(
        String(64), default=lambda: datetime.now(timezone.utc).isoformat()
    )


class AnomalyIncident(Base):
    """Stores detected anomalies, confluence decision, confidence score, culprit sensor, and justification."""
    __tablename__ = "anomaly_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anomaly_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    detected_at: Mapped[str] = mapped_column(String(64), index=True)
    station_id: Mapped[str] = mapped_column(String(64), default="AGRA-01")
    anomaly_type: Mapped[str] = mapped_column(String(64))
    severity_score: Mapped[float] = mapped_column(Float)
    culprit_sensors: Mapped[str] = mapped_column(Text)
    diagnostic_message: Mapped[str] = mapped_column(Text)
    shap_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reconstruction_error: Mapped[float] = mapped_column(Float, default=0.0)
    confluence_decision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[str] = mapped_column(
        String(64), default=lambda: datetime.now(timezone.utc).isoformat()
    )


class MaintenancePrediction(Base):
    """Stores long-term drift tracking and days-to-failure forecasts."""
    __tablename__ = "maintenance_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(64), default="AGRA-01")
    timestamp: Mapped[str] = mapped_column(String(64))
    sensor: Mapped[str] = mapped_column(String(64))
    drift_value: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="Healthy")
    days_to_recalibration: Mapped[int] = mapped_column(Integer, default=30)
    tolerance_threshold: Mapped[float] = mapped_column(Float, default=2.0)
    daily_drift_rate: Mapped[float] = mapped_column(Float, default=0.05)
    created_at: Mapped[str] = mapped_column(
        String(64), default=lambda: datetime.now(timezone.utc).isoformat()
    )


class OperatorFeedbackRecord(Base):
    """Stores whether the operator clicked 'false_alarm' or 'confirmed_fault'."""
    __tablename__ = "operator_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anomaly_id: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(32))
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    operator_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[str] = mapped_column(
        String(64), default=lambda: datetime.now(timezone.utc).isoformat()
    )


def format_db_url(url: str) -> str:
    """Ensures asyncpg driver is used for PostgreSQL and aiosqlite for SQLite."""
    if not url:
        return DEFAULT_SQLITE_URL
    url = url.strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite://") and not url.startswith("sqlite+"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url


# Engine and session maker singletons
engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
_db_lock = asyncio.Lock()
_active_db_type: str = "sqlite"


_init_lock = threading.Lock()
_initialized = False


async def init_db() -> None:
    """
    Initializes the database schema.
    Attempts connection to Supabase PostgreSQL via DATABASE_URL if configured,
    falling back to local SQLite (skyguard.db) on connection error or absence.
    Safe against concurrent initialization.
    """
    global engine, async_session_maker, _active_db_type, _initialized

    with _init_lock:
        if _initialized and async_session_maker is not None:
            return

    raw_url = os.getenv("DATABASE_URL", "").strip()

    if raw_url:
        primary_url = format_db_url(raw_url)
        try:
            logger.info("Attempting connection to primary DATABASE_URL (Supabase PostgreSQL)...")
            temp_engine = create_async_engine(
                primary_url,
                echo=False,
                pool_pre_ping=True,
            )
            async with temp_engine.begin() as conn:
                try:
                    await conn.run_sync(Base.metadata.create_all)
                except Exception as ddl_err:
                    if "already exists" not in str(ddl_err).lower():
                        raise

            with _init_lock:
                engine = temp_engine
                async_session_maker = async_sessionmaker(
                    engine, expire_on_commit=False, class_=AsyncSession
                )
                _active_db_type = "supabase_postgresql"
                _initialized = True
            logger.info("Connected and initialized Supabase PostgreSQL schema successfully.")
            return
        except Exception as exc:
            logger.warning(
                f"Primary DATABASE_URL connection failed: {exc}. "
                f"Falling back to local SQLite ({DEFAULT_SQLITE_URL})."
            )

    # Fallback to local SQLite
    sqlite_url = DEFAULT_SQLITE_URL
    temp_sqlite_engine = create_async_engine(
        sqlite_url,
        echo=False,
        connect_args={"timeout": 30.0},
    )
    async with temp_sqlite_engine.begin() as conn:
        try:
            await conn.execute(text("PRAGMA journal_mode=WAL;"))
            await conn.execute(text("PRAGMA busy_timeout=30000;"))
            await conn.run_sync(Base.metadata.create_all)
        except Exception as ddl_err:
            if "already exists" not in str(ddl_err).lower():
                raise

    with _init_lock:
        engine = temp_sqlite_engine
        async_session_maker = async_sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        _active_db_type = "sqlite"
        _initialized = True
    logger.info(f"Initialized local SQLite schema at {sqlite_url}")


async def get_session() -> AsyncSession:
    """Returns a new async database session, initializing engine if necessary."""
    global async_session_maker
    if async_session_maker is None:
        await init_db()
    return async_session_maker()


async def insert_telemetry(data: Dict[str, Any]) -> Optional[int]:
    """Asynchronously persists a single telemetry reading."""
    try:
        session = await get_session()
        async with session:
            async with session.begin():
                record = TelemetryRecord(
                    station_id=data.get("station_id", "AGRA-01"),
                    timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    temperature_c=float(data.get("temperature_c", 0.0)),
                    pressure_hpa=float(data.get("pressure_hpa", 0.0)),
                    humidity_pct=float(data.get("humidity_pct", 0.0)),
                    dew_point_c=float(data.get("dew_point_c", 0.0)),
                    wind_speed_ms=float(data.get("wind_speed_ms", 2.5)),
                    wind_dir_deg=float(data.get("wind_dir_deg", 180.0)),
                    solar_radiation_wm2=float(data.get("solar_radiation_wm2", 450.0)),
                    sequence=int(data.get("sequence", 0)),
                    source=data.get("source", "edge-simulator"),
                    drop_flag=int(data.get("drop_flag", 0)),
                    reconstruction_error=float(data.get("reconstruction_error", 0.0142)),
                    inference_time_ms=float(data.get("inference_time_ms", 2.4)),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                session.add(record)
            return record.id
    except Exception as e:
        logger.error(f"Failed to persist telemetry record: {e}")
        return None


async def insert_anomaly(
    data: Dict[str, Any],
    confluence_decision: Optional[str] = None,
    confidence_score: Optional[float] = None,
) -> Optional[int]:
    """Asynchronously persists an anomaly incident."""
    try:
        session = await get_session()
        async with session:
            async with session.begin():
                culprits = data.get("culprit_sensors", [])
                culprit_str = json.dumps(culprits) if isinstance(culprits, list) else str(culprits)

                shap_val = data.get("shap_values", [])
                if isinstance(shap_val, list):
                    shap_str = json.dumps([
                        s.model_dump() if hasattr(s, "model_dump") else (s if isinstance(s, dict) else str(s))
                        for s in shap_val
                    ])
                else:
                    shap_str = str(shap_val) if shap_val else None

                incident = AnomalyIncident(
                    anomaly_id=data.get("anomaly_id", ""),
                    detected_at=data.get("detected_at", datetime.now(timezone.utc).isoformat()),
                    station_id=data.get("station_id", "AGRA-01"),
                    anomaly_type=data.get("anomaly_type", "ai_anomaly"),
                    severity_score=float(data.get("severity_score", 0.5)),
                    culprit_sensors=culprit_str,
                    diagnostic_message=data.get("diagnostic_message", ""),
                    shap_values=shap_str,
                    status=data.get("status", "open"),
                    resolution_note=data.get("resolution_note"),
                    resolved_at=data.get("resolved_at"),
                    reconstruction_error=float(data.get("reconstruction_error", 0.0)),
                    confluence_decision=confluence_decision or data.get("confluence_decision"),
                    confidence_score=confidence_score or data.get("confidence_score"),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                session.add(incident)
            return incident.id
    except Exception as e:
        logger.error(f"Failed to persist anomaly incident: {e}")
        return None


async def update_anomaly_status(
    anomaly_id: str,
    status: str,
    resolution_note: Optional[str] = None,
    resolved_at: Optional[str] = None,
) -> bool:
    """Updates an existing anomaly status in the database."""
    try:
        session = await get_session()
        async with session:
            async with session.begin():
                values: Dict[str, Any] = {"status": status}
                if resolution_note is not None:
                    values["resolution_note"] = resolution_note
                if resolved_at is not None:
                    values["resolved_at"] = resolved_at
                stmt = (
                    update(AnomalyIncident)
                    .where(AnomalyIncident.anomaly_id == anomaly_id)
                    .values(**values)
                )
                await session.execute(stmt)
        return True
    except Exception as e:
        logger.error(f"Failed to update anomaly {anomaly_id}: {e}")
        return False


async def insert_maintenance_prediction(data: Dict[str, Any]) -> Optional[int]:
    """Persists a predictive maintenance drift assessment."""
    try:
        session = await get_session()
        async with session:
            async with session.begin():
                record = MaintenancePrediction(
                    station_id=data.get("station_id", "AGRA-01"),
                    timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    sensor=data.get("sensor", "humidity"),
                    drift_value=float(data.get("drift_value", 0.0)),
                    status=data.get("status", "Healthy"),
                    days_to_recalibration=int(data.get("days_to_recalibration", 30)),
                    tolerance_threshold=float(data.get("tolerance_threshold", 2.0)),
                    daily_drift_rate=float(data.get("daily_drift_rate", 0.05)),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                session.add(record)
            return record.id
    except Exception as e:
        logger.error(f"Failed to persist maintenance prediction: {e}")
        return None


async def insert_feedback(data: Dict[str, Any]) -> Optional[int]:
    """Persists operator feedback."""
    try:
        session = await get_session()
        async with session:
            async with session.begin():
                record = OperatorFeedbackRecord(
                    anomaly_id=data.get("anomaly_id", ""),
                    label=data.get("label", "false_alarm"),
                    note=data.get("note"),
                    operator_id=data.get("operator_id", "operator-1"),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                session.add(record)
            return record.id
    except Exception as e:
        logger.error(f"Failed to persist operator feedback: {e}")
        return None


async def get_recent_telemetry(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetches recent telemetry records from database."""
    try:
        session = await get_session()
        async with session:
            stmt = select(TelemetryRecord).order_by(desc(TelemetryRecord.id)).limit(limit)
            result = await session.execute(stmt)
            records = result.scalars().all()
            return [
                {
                    "station_id": r.station_id,
                    "timestamp": r.timestamp,
                    "temperature_c": r.temperature_c,
                    "pressure_hpa": r.pressure_hpa,
                    "humidity_pct": r.humidity_pct,
                    "dew_point_c": r.dew_point_c,
                    "wind_speed_ms": r.wind_speed_ms,
                    "wind_dir_deg": r.wind_dir_deg,
                    "solar_radiation_wm2": r.solar_radiation_wm2,
                    "sequence": r.sequence,
                    "reconstruction_error": r.reconstruction_error,
                }
                for r in reversed(records)
            ]
    except Exception as e:
        logger.error(f"Failed to query recent telemetry: {e}")
        return []
