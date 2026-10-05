import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.config import settings
from backend.schemas import TelemetryPayload, AnomalyEvent, AgentTurnLog, DecisionRecord

class Database:
    def __init__(self, db_path: str = settings.DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Telemetry Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    temperature_c REAL,
                    humidity_pct REAL,
                    pressure_hpa REAL,
                    wind_speed_ms REAL,
                    payload_json TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_station ON telemetry(station_id, id DESC)")
            
            # Anomalies Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    anomaly_id TEXT PRIMARY KEY,
                    station_id TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    severity_score REAL NOT NULL,
                    classification TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    anomaly_json TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_station ON anomalies(station_id, detected_at DESC)")

            # AI Agent Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    dialogue_json TEXT NOT NULL
                )
            """)

            # AI Decisions Audit Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    station_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    trigger_reason TEXT NOT NULL,
                    culprit_sensors_json TEXT NOT NULL,
                    action_recommended TEXT NOT NULL,
                    dialogue_json TEXT NOT NULL,
                    reconstruction_error REAL DEFAULT 0.0,
                    transmitted_data_json TEXT,
                    decision_reasoning_json TEXT,
                    summary TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_station ON decisions(station_id, timestamp DESC)")

            # Backwards compatibility check for existing databases
            for col, col_type in [
                ("transmitted_data_json", "TEXT"),
                ("decision_reasoning_json", "TEXT"),
                ("summary", "TEXT")
            ]:
                try:
                    cursor.execute(f"ALTER TABLE decisions ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError:
                    pass

            # Imputations Accepted Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS imputations_accepted (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sensor TEXT NOT NULL,
                    reported REAL,
                    suggested REAL NOT NULL,
                    method TEXT,
                    sequence INTEGER
                )
            """)
            conn.commit()

    def insert_telemetry(self, payload: TelemetryPayload):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO telemetry (
                    station_id, sequence, timestamp,
                    temperature_c, humidity_pct, pressure_hpa, wind_speed_ms,
                    payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payload.station_id,
                payload.sequence,
                payload.timestamp,
                payload.temperature_c,
                payload.humidity_pct,
                payload.pressure_hpa,
                payload.wind_speed_ms,
                payload.model_dump_json()
            ))
            conn.commit()

    def get_latest_telemetry(self, station_id: str = "AGRA-01") -> Optional[TelemetryPayload]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payload_json FROM telemetry 
                WHERE station_id = ? 
                ORDER BY id DESC LIMIT 1
            """, (station_id,))
            row = cursor.fetchone()
            if row:
                return TelemetryPayload.model_validate_json(row["payload_json"])
            return None

    def get_telemetry_history(self, station_id: str = "AGRA-01", limit: int = 60) -> List[TelemetryPayload]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payload_json FROM telemetry 
                WHERE station_id = ? 
                ORDER BY id DESC LIMIT ?
            """, (station_id, limit))
            rows = cursor.fetchall()
            results = [TelemetryPayload.model_validate_json(r["payload_json"]) for r in reversed(rows)]
            return results

    def insert_anomaly(self, anomaly: AnomalyEvent):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO anomalies (
                    anomaly_id, station_id, detected_at, severity_score, classification, status, anomaly_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                anomaly.anomaly_id,
                anomaly.station_id,
                anomaly.detected_at,
                anomaly.severity_score,
                anomaly.classification,
                anomaly.status,
                anomaly.model_dump_json()
            ))
            conn.commit()

    def get_anomalies(self, station_id: str = "AGRA-01", status: Optional[str] = None, limit: int = 50) -> List[AnomalyEvent]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT anomaly_json FROM anomalies 
                    WHERE station_id = ? AND status = ?
                    ORDER BY detected_at DESC LIMIT ?
                """, (station_id, status, limit))
            else:
                cursor.execute("""
                    SELECT anomaly_json FROM anomalies 
                    WHERE station_id = ?
                    ORDER BY detected_at DESC LIMIT ?
                """, (station_id, limit))
            rows = cursor.fetchall()
            return [AnomalyEvent.model_validate_json(r["anomaly_json"]) for r in rows]

    def update_anomaly_status(self, anomaly_id: str, status: str, note: Optional[str] = None) -> Optional[AnomalyEvent]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT anomaly_json FROM anomalies WHERE anomaly_id = ?", (anomaly_id,))
            row = cursor.fetchone()
            if not row:
                return None
            ano = AnomalyEvent.model_validate_json(row["anomaly_json"])
            ano.status = status  # type: ignore
            now_iso = datetime.utcnow().isoformat()
            if note:
                ano.resolution_note = note
            if status == "resolved":
                ano.resolved_at = now_iso
            elif status == "acknowledged":
                ano.acknowledged_at = now_iso
            elif status == "ignored":
                ano.ignored_at = now_iso
            ano.action_taken = status
            ano.action_timestamp = now_iso
            
            cursor.execute("""
                UPDATE anomalies SET status = ?, anomaly_json = ? WHERE anomaly_id = ?
            """, (status, ano.model_dump_json(), anomaly_id))
            conn.commit()
            return ano

    def insert_agent_log(self, station_id: str, classification: str, reasoning: str, dialogue: List[AgentTurnLog]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_logs (
                    station_id, timestamp, classification, reasoning, dialogue_json
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                station_id,
                datetime.utcnow().isoformat(),
                classification,
                reasoning,
                json.dumps([turn.model_dump() for turn in dialogue])
            ))
    def insert_accepted_imputation(self, req: Dict[str, Any]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO imputations_accepted (
                    station_id, timestamp, sensor, reported, suggested, method, sequence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                req.get("station_id", "AGRA-01"),
                req.get("timestamp") or datetime.utcnow().isoformat(),
                req.get("sensor", "humidity"),
                req.get("reported"),
                req.get("suggested"),
                req.get("method"),
                req.get("sequence")
            ))
            conn.commit()

    def get_accepted_imputations(self, station_id: str = "AGRA-01", limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM imputations_accepted
                WHERE station_id = ?
                ORDER BY id DESC LIMIT ?
            """, (station_id, limit))
            return [dict(r) for r in cursor.fetchall()]

    def insert_decision(self, decision: DecisionRecord):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO decisions (
                    decision_id, station_id, timestamp, classification,
                    confidence_score, trigger_reason, culprit_sensors_json,
                    action_recommended, dialogue_json, reconstruction_error,
                    transmitted_data_json, decision_reasoning_json, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.decision_id,
                decision.station_id,
                decision.timestamp,
                decision.classification,
                decision.confidence_score,
                decision.trigger_reason,
                json.dumps(decision.culprit_sensors),
                decision.action_recommended,
                json.dumps([turn.model_dump() for turn in decision.dialogue]),
                decision.reconstruction_error,
                json.dumps(decision.transmitted_data) if decision.transmitted_data else None,
                json.dumps(decision.decision_reasoning) if decision.decision_reasoning else None,
                decision.summary
            ))
            conn.commit()

    def get_decisions(
        self,
        station_id: str = "AGRA-01",
        limit: int = 50,
        classification: Optional[str] = None
    ) -> List[DecisionRecord]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if classification and classification != "all":
                cursor.execute("""
                    SELECT * FROM decisions
                    WHERE station_id = ? AND classification = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (station_id, classification, limit))
            else:
                cursor.execute("""
                    SELECT * FROM decisions
                    WHERE station_id = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (station_id, limit))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                try:
                    dialogue_raw = json.loads(r["dialogue_json"])
                    dialogue = [AgentTurnLog.model_validate(t) for t in dialogue_raw]
                except Exception:
                    dialogue = []
                try:
                    culprits = json.loads(r["culprit_sensors_json"])
                except Exception:
                    culprits = []
                transmitted_data = None
                if "transmitted_data_json" in r.keys() and r["transmitted_data_json"]:
                    try:
                        transmitted_data = json.loads(r["transmitted_data_json"])
                    except Exception:
                        transmitted_data = None
                decision_reasoning = None
                if "decision_reasoning_json" in r.keys() and r["decision_reasoning_json"]:
                    try:
                        decision_reasoning = json.loads(r["decision_reasoning_json"])
                    except Exception:
                        decision_reasoning = None
                summary_val = r["summary"] if "summary" in r.keys() else None

                results.append(DecisionRecord(
                    decision_id=r["decision_id"],
                    station_id=r["station_id"],
                    timestamp=r["timestamp"],
                    classification=r["classification"],
                    confidence_score=r["confidence_score"],
                    trigger_reason=r["trigger_reason"],
                    culprit_sensors=culprits,
                    action_recommended=r["action_recommended"],
                    dialogue=dialogue,
                    reconstruction_error=r["reconstruction_error"],
                    transmitted_data=transmitted_data,
                    decision_reasoning=decision_reasoning,
                    summary=summary_val
                ))
            return results

    def reset_database(self):
        """Cleans all telemetry, anomalies, agent logs, decisions, and imputations for a fresh demo run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM telemetry")
            cursor.execute("DELETE FROM anomalies")
            cursor.execute("DELETE FROM agent_logs")
            cursor.execute("DELETE FROM decisions")
            cursor.execute("DELETE FROM imputations_accepted")
            conn.commit()

    def bulk_update_anomalies(self, station_id: str = "AGRA-01", status: str = "resolved", note: Optional[str] = None) -> int:
        """Updates all open anomalies for a station to the specified status (acknowledged, resolved, ignored)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT anomaly_id, anomaly_json FROM anomalies
                WHERE station_id = ? AND status = 'open'
            """, (station_id,))
            rows = cursor.fetchall()
            now_iso = datetime.utcnow().isoformat()
            default_notes = {
                "resolved": "Bulk resolved by operator.",
                "acknowledged": "Bulk acknowledged by operator.",
                "ignored": "Bulk ignored by operator."
            }
            eff_note = note or default_notes.get(status, f"Bulk {status} by operator.")
            for r in rows:
                ano_id = r["anomaly_id"]
                ano = AnomalyEvent.model_validate_json(r["anomaly_json"])
                ano.status = status  # type: ignore
                ano.resolution_note = eff_note
                ano.action_taken = status
                ano.action_timestamp = now_iso
                if status == "resolved":
                    ano.resolved_at = now_iso
                elif status == "acknowledged":
                    ano.acknowledged_at = now_iso
                elif status == "ignored":
                    ano.ignored_at = now_iso
                cursor.execute("""
                    UPDATE anomalies SET status = ?, anomaly_json = ? WHERE anomaly_id = ?
                """, (status, ano.model_dump_json(), ano_id))
            conn.commit()
            return len(rows)

    def resolve_all_anomalies(self, station_id: str = "AGRA-01", note: str = "Resolved by operator bulk action.") -> int:
        """Resolves all open anomalies for a station (convenience wrapper)."""
        return self.bulk_update_anomalies(station_id=station_id, status="resolved", note=note)

db = Database()

