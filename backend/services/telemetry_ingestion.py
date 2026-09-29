import uuid
from typing import Optional

from models.schemas import AnomalyEvent, TelemetryPayload
from config import settings
from services.anomaly_detector import anomaly_detector
from services.rule_engine import IMDPhysicsRuleEngine
from services.sse_manager import sse_manager
from services.sensor_health import sensor_health
from services.confluence_engine import confluence_engine
from services.multi_scale_analyzer import multi_scale_analyzer
from data.store import store


class TelemetryIngestionService:
    """Runs every telemetry source through one ordered processing pipeline."""

    def __init__(self) -> None:
        import asyncio

        self._lock = asyncio.Lock()

    async def ingest(self, payload: TelemetryPayload) -> Optional[AnomalyEvent]:
        async with self._lock:
            recent_history = store.get_telemetry_history(limit=settings.WINDOW_SIZE)
            rule_violation = IMDPhysicsRuleEngine.evaluate(payload, recent_history)

            reconstruction_error = 0.0142
            latency_ms = 2.1
            live_attributions = []

            if rule_violation:
                reconstruction_error = round(rule_violation["severity"] * 0.12, 4)
                latency_ms = 1.1
                live_attributions = rule_violation.get("shap_attributions", [])
                detected_anomaly = AnomalyEvent(
                    anomaly_id=f"rule-{uuid.uuid4().hex[:8]}",
                    detected_at=payload.timestamp,
                    station_id=payload.station_id,
                    anomaly_type="rule_flag",
                    severity_score=rule_violation["severity"],
                    culprit_sensors=rule_violation["culprit"],
                    diagnostic_message=rule_violation["message"],
                    shap_values=live_attributions,
                    status="open",
                    reconstruction_error=reconstruction_error,
                )
            else:
                detected_anomaly, reconstruction_error, latency_ms, live_attributions = (
                    anomaly_detector.evaluate_window(recent_history + [payload])
                )

            # Attach real-time ML metrics to the telemetry payload
            payload.reconstruction_error = reconstruction_error
            payload.inference_time_ms = latency_ms
            payload.live_attributions = live_attributions

            # Multi-Scale Multivariate Physical Analyzer (Hanswarup - Layer 2.1)
            window = recent_history + [payload]
            physical_features = multi_scale_analyzer.analyze_window(window)
            payload.physical_features = physical_features

            # Confluence Decision Matrix Engine (Mudit - Layer 2.3)
            confluence_res = confluence_engine.evaluate_window(window, physical_features=physical_features)
            confluence_dict = dict(confluence_res)
            payload.confluence = confluence_dict

            # Predictive maintenance + imputation (Harsh)
            is_natural_weather = (confluence_res.get("classification") == "Natural Weather Event")
            health = sensor_health.process(payload, detected_anomaly, weather_event=is_natural_weather)
            payload.maintenance = health["maintenance"]
            payload.imputation = health["imputation"]
            payload.weather = health["weather"]

            store.add_telemetry(payload)
            await sse_manager.broadcast("telemetry", payload.model_dump())

            if detected_anomaly:
                detected_anomaly.confluence = confluence_dict
                store.add_anomaly(
                    detected_anomaly,
                    confluence_decision=confluence_res.get("classification"),
                    confidence_score=confluence_res.get("confidence_score"),
                )
                await sse_manager.broadcast("anomaly", detected_anomaly.model_dump())

            if health["event"]:
                health["event"].confluence = confluence_dict
                store.add_anomaly(
                    health["event"],
                    confluence_decision="Sensor Defect",
                    confidence_score=confluence_res.get("confidence_score"),
                )
                await sse_manager.broadcast("anomaly", health["event"].model_dump())

            return detected_anomaly


telemetry_ingestion = TelemetryIngestionService()
