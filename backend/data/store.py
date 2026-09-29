import asyncio
import logging
import queue
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from models.schemas import AnomalyEvent, OperatorFeedback, TelemetryPayload
logger = logging.getLogger("skyguard.store")

try:
    from data.db import (
        init_db,
        insert_telemetry,
        insert_anomaly,
        update_anomaly_status,
        insert_feedback,
        insert_maintenance_prediction,
        get_recent_telemetry,
    )
    DB_AVAILABLE = True
except Exception as exc:
    logger.warning("Database persistence layer unavailable (%s). Running in memory-only mode.", exc)
    DB_AVAILABLE = False
    init_db = None
    insert_telemetry = None
    insert_anomaly = None
    update_anomaly_status = None
    insert_feedback = None
    insert_maintenance_prediction = None
    get_recent_telemetry = None


class InMemoryStore:
    """
    In-memory operational store paired with non-blocking asynchronous persistence.
    All in-memory reads and writes execute with zero latency under memory locks,
    while a dedicated background persistence engine drains records to the database
    (Supabase PostgreSQL with automatic local SQLite fallback).
    """

    def __init__(self, max_history: int = 1000):
        self._lock = threading.Lock()
        self._telemetry_history: deque = deque(maxlen=max_history)
        self._anomalies: Dict[str, AnomalyEvent] = {}
        self._feedback_logs: List[OperatorFeedback] = []
        self._active_fault: str = "normal"
        self._fault_expires_at: Optional[float] = None
        self._fault_intensity: float = 1.0

        # Non-blocking async persistence queue
        self._persist_queue: queue.Queue = queue.Queue(maxsize=10000)
        self._worker_running = True
        self._worker_thread = threading.Thread(
            target=self._persistence_worker,
            name="DBPersistenceWorker",
            daemon=True,
        )
        self._worker_thread.start()

    def _persistence_worker(self) -> None:
        """
        Background daemon thread that creates its own asyncio loop and
        drains persistence events without blocking active 1 Hz telemetry or SSE streams.
        """
        if not DB_AVAILABLE or init_db is None:
            while self._worker_running:
                try:
                    self._persist_queue.get(timeout=0.5)
                    self._persist_queue.task_done()
                except queue.Empty:
                    continue
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Ensure database tables exist
        try:
            loop.run_until_complete(init_db())
        except Exception as exc:
            logger.warning(f"Background worker init_db note: {exc}")

        while self._worker_running:
            try:
                task_type, data = self._persist_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                if task_type == "telemetry":
                    loop.run_until_complete(insert_telemetry(data))
                elif task_type == "anomaly":
                    loop.run_until_complete(
                        insert_anomaly(
                            data["anomaly"],
                            confluence_decision=data.get("confluence_decision"),
                            confidence_score=data.get("confidence_score"),
                        )
                    )
                elif task_type == "anomaly_update":
                    loop.run_until_complete(
                        update_anomaly_status(
                            data["anomaly_id"],
                            data["status"],
                            resolution_note=data.get("resolution_note"),
                            resolved_at=data.get("resolved_at"),
                        )
                    )
                elif task_type == "feedback":
                    loop.run_until_complete(insert_feedback(data))
                elif task_type == "maintenance":
                    loop.run_until_complete(insert_maintenance_prediction(data))
            except Exception as exc:
                logger.error(f"Error persisting {task_type} in background worker: {exc}")
            finally:
                self._persist_queue.task_done()

    def _enqueue_persistence(self, task_type: str, data: Any) -> None:
        """Non-blocking enqueue for database persistence."""
        try:
            self._persist_queue.put_nowait((task_type, data))
        except queue.Full:
            logger.warning(f"Persistence queue full, dropping {task_type} write to prevent memory pressure.")

    def add_telemetry(self, payload: TelemetryPayload) -> None:
        """Adds telemetry to in-memory history and enqueues async DB write without blocking."""
        with self._lock:
            self._telemetry_history.append(payload)

        # Enqueue non-blocking persistence
        data = payload.model_dump() if hasattr(payload, "model_dump") else payload.__dict__.copy()
        self._enqueue_persistence("telemetry", data)

    def get_latest_telemetry(self) -> Optional[TelemetryPayload]:
        with self._lock:
            if not self._telemetry_history:
                return None
            return self._telemetry_history[-1]

    def get_telemetry_history(self, limit: int = 100) -> List[TelemetryPayload]:
        with self._lock:
            history = list(self._telemetry_history)
            return history[-limit:]

    def add_anomaly(
        self,
        anomaly: AnomalyEvent,
        confluence_decision: Optional[str] = None,
        confidence_score: Optional[float] = None,
    ) -> None:
        """Adds anomaly to in-memory state and enqueues async DB write."""
        with self._lock:
            self._anomalies[anomaly.anomaly_id] = anomaly

        data = {
            "anomaly": anomaly.model_dump() if hasattr(anomaly, "model_dump") else anomaly.__dict__.copy(),
            "confluence_decision": confluence_decision,
            "confidence_score": confidence_score,
        }
        self._enqueue_persistence("anomaly", data)

    def get_anomalies(self, status: Optional[str] = None, limit: int = 50) -> List[AnomalyEvent]:
        with self._lock:
            items = list(self._anomalies.values())
            if status:
                items = [a for a in items if a.status == status]
            # Most recent first
            items.sort(key=lambda x: x.detected_at, reverse=True)
            return items[:limit]

    def get_anomaly_by_id(self, anomaly_id: str) -> Optional[AnomalyEvent]:
        with self._lock:
            return self._anomalies.get(anomaly_id)

    def update_anomaly(
        self, anomaly_id: str, status: str, note: Optional[str] = None
    ) -> Optional[AnomalyEvent]:
        resolved_at = None
        with self._lock:
            if anomaly_id in self._anomalies:
                anomaly = self._anomalies[anomaly_id]
                anomaly.status = status
                if note:
                    anomaly.resolution_note = note
                if status in ["resolved", "false_alarm"]:
                    resolved_at = datetime.now(timezone.utc).isoformat()
                    anomaly.resolved_at = resolved_at

                # Enqueue DB update
                self._enqueue_persistence(
                    "anomaly_update",
                    {
                        "anomaly_id": anomaly_id,
                        "status": status,
                        "resolution_note": note,
                        "resolved_at": resolved_at,
                    },
                )
                return anomaly
            return None

    def log_feedback(self, feedback: OperatorFeedback) -> None:
        with self._lock:
            self._feedback_logs.append(feedback)
            if feedback.anomaly_id in self._anomalies:
                status = "false_alarm" if feedback.label == "false_alarm" else "acknowledged"
                self._anomalies[feedback.anomaly_id].status = status
                if feedback.note:
                    self._anomalies[feedback.anomaly_id].resolution_note = feedback.note

        data = feedback.model_dump() if hasattr(feedback, "model_dump") else feedback.__dict__.copy()
        self._enqueue_persistence("feedback", data)

    def add_maintenance_prediction(self, prediction_data: Dict[str, Any]) -> None:
        """Enqueues a predictive maintenance record for persistence."""
        self._enqueue_persistence("maintenance", prediction_data)

    def get_feedback_count(self) -> int:
        with self._lock:
            return len(self._feedback_logs)

    def set_fault(self, fault_type: str, intensity: float = 1.0, duration_seconds: int = 30) -> None:
        import time
        with self._lock:
            self._active_fault = fault_type
            self._fault_intensity = intensity
            if fault_type == "normal":
                self._fault_expires_at = None
            else:
                self._fault_expires_at = time.time() + duration_seconds

    def get_active_fault(self) -> str:
        import time
        with self._lock:
            if self._fault_expires_at and time.time() > self._fault_expires_at:
                self._active_fault = "normal"
                self._fault_expires_at = None
            return self._active_fault

    def get_fault_intensity(self) -> float:
        with self._lock:
            return self._fault_intensity

    def flush(self, timeout: float = 3.0) -> None:
        """Blocks until pending persistence tasks have finished (useful for testing)."""
        import time
        deadline = time.time() + timeout
        while (not self._persist_queue.empty() or self._persist_queue.unfinished_tasks > 0) and time.time() < deadline:
            time.sleep(0.05)


store = InMemoryStore()
