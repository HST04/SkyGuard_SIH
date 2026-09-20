import threading
from collections import deque
from typing import List, Dict, Optional
from datetime import datetime, timezone
from models.schemas import TelemetryPayload, AnomalyEvent, OperatorFeedback

class InMemoryStore:
    def __init__(self, max_history: int = 1000):
        self._lock = threading.Lock()
        self._telemetry_history: deque = deque(maxlen=max_history)
        self._anomalies: Dict[str, AnomalyEvent] = {}
        self._feedback_logs: List[OperatorFeedback] = []
        self._active_fault: str = "normal"
        self._fault_expires_at: Optional[float] = None
        self._fault_intensity: float = 1.0

    def add_telemetry(self, payload: TelemetryPayload) -> None:
        with self._lock:
            self._telemetry_history.append(payload)

    def get_latest_telemetry(self) -> Optional[TelemetryPayload]:
        with self._lock:
            if not self._telemetry_history:
                return None
            return self._telemetry_history[-1]

    def get_telemetry_history(self, limit: int = 100) -> List[TelemetryPayload]:
        with self._lock:
            history = list(self._telemetry_history)
            return history[-limit:]

    def add_anomaly(self, anomaly: AnomalyEvent) -> None:
        with self._lock:
            self._anomalies[anomaly.anomaly_id] = anomaly

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

    def update_anomaly(self, anomaly_id: str, status: str, note: Optional[str] = None) -> Optional[AnomalyEvent]:
        with self._lock:
            if anomaly_id in self._anomalies:
                anomaly = self._anomalies[anomaly_id]
                anomaly.status = status
                if note:
                    anomaly.resolution_note = note
                if status in ["resolved", "false_alarm"]:
                    anomaly.resolved_at = datetime.now(timezone.utc).isoformat()
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

store = InMemoryStore()
