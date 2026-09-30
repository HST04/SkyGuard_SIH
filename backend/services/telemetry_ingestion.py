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

            # Track IMD physics check pass/fail
            if rule_violation:
                payload.imd_passed = False
                payload.imd_violation = rule_violation.get("rule")
            else:
                payload.imd_passed = True
                payload.imd_violation = None

            detected_anomaly, reconstruction_error, latency_ms, live_attributions = (
                anomaly_detector.evaluate_window(recent_history + [payload])
            )

            is_hard_bound_violation = bool(rule_violation and rule_violation.get("rule") in (
                "IMD_CLIMATOLOGICAL_TEMP_BOUND",
                "IMD_CLIMATOLOGICAL_RH_BOUND",
                "IMD_BAROMETRIC_PRESSURE_BOUND",
                "IMD_SUPERSATURATION_VIOLATION",
                "IMD_STUCK_SENSOR_FLATLINE",
            ))

            if rule_violation:
                reconstruction_error = max(reconstruction_error, round(rule_violation["severity"] * 0.12, 4))
                detected_anomaly = AnomalyEvent(
                    anomaly_id=f"rule-{uuid.uuid4().hex[:8]}",
                    detected_at=payload.timestamp,
                    station_id=payload.station_id,
                    anomaly_type="rule_flag",
                    severity_score=rule_violation["severity"],
                    culprit_sensors=rule_violation["culprit"],
                    diagnostic_message=rule_violation["message"],
                    shap_values=rule_violation.get("shap_attributions", live_attributions),
                    status="open",
                    reconstruction_error=reconstruction_error,
                )

            # Multi-Scale Multivariate Physical Analyzer (Hanswarup - Layer 2.1)
            window = recent_history + [payload]
            physical_features = multi_scale_analyzer.analyze_window(window)
            payload.physical_features = physical_features

            # Confluence Decision Matrix Engine (Mudit - Layer 2.3)
            confluence_res = confluence_engine.evaluate_window(window, physical_features=physical_features)
            confluence_dict = dict(confluence_res)
            payload.confluence = confluence_dict

            classification = confluence_res.get("classification", "Nominal Baseline")
            is_hardware_fault = classification in ("Sensor Defect", "Compound Event")

            # Zero False Alarm filtering:
            # Weather events (storms, heat spikes) and nominal baseline MUST NEVER flag hardware defects!
            if classification == "Natural Weather Event":
                if detected_anomaly and detected_anomaly.anomaly_type != "rule_flag":
                    detected_anomaly = None
                reconstruction_error = min(reconstruction_error, 0.0245)
            elif classification == "Nominal Baseline":
                detected_anomaly = None
                reconstruction_error = min(reconstruction_error, 0.0150)
            elif not is_hardware_fault:
                detected_anomaly = None

            # If confluence engine detected a sensor defect but no anomaly was created yet, create it
            if is_hardware_fault and detected_anomaly is None:
                defect_type = confluence_res.get("defect_type", "capacitive_drift")
                culprit = "humidity" if any(k in defect_type for k in ("humidity", "drift", "frozen")) else "temperature"
                detected_anomaly = AnomalyEvent(
                    anomaly_id=f"defect-{uuid.uuid4().hex[:8]}",
                    detected_at=payload.timestamp,
                    station_id=payload.station_id,
                    anomaly_type="ai_anomaly",
                    severity_score=round(float(confluence_res.get("confidence_score", 92.0)) / 100.0, 2),
                    culprit_sensors=[culprit],
                    diagnostic_message=f"Hardware defect confirmed: {defect_type.replace('_', ' ').title()}.",
                    shap_values=live_attributions,
                    status="open",
                    reconstruction_error=max(reconstruction_error, 0.098),
                )

            # Attach real-time ML metrics to the telemetry payload
            payload.reconstruction_error = reconstruction_error
            payload.inference_time_ms = latency_ms
            payload.live_attributions = live_attributions

            # Predictive maintenance + imputation (Harsh)
            is_natural_weather = (classification == "Natural Weather Event")
            health = sensor_health.process(payload, detected_anomaly, weather_event=is_natural_weather)
            payload.maintenance = health["maintenance"]
            payload.imputation = health["imputation"]
            payload.weather = health["weather"]

            store.add_telemetry(payload)
            await sse_manager.broadcast("telemetry", payload.model_dump())

            if detected_anomaly and is_hardware_fault:
                detected_anomaly.confluence = confluence_dict
                open_anomalies = store.get_anomalies(status="open", limit=10)
                existing = next(
                    (
                        a for a in open_anomalies
                        if any(c in getattr(a, "culprit_sensors", []) for c in detected_anomaly.culprit_sensors)
                    ),
                    None,
                )
                if not existing:
                    store.add_anomaly(
                        detected_anomaly,
                        confluence_decision=classification,
                        confidence_score=confluence_res.get("confidence_score"),
                    )
                    await sse_manager.broadcast("anomaly", detected_anomaly.model_dump())
                else:
                    existing.reconstruction_error = detected_anomaly.reconstruction_error
                    existing.severity_score = detected_anomaly.severity_score
                    existing.confluence = confluence_dict

            if health["event"] and is_hardware_fault:
                health["event"].confluence = confluence_dict
                store.add_anomaly(
                    health["event"],
                    confluence_decision="Sensor Defect",
                    confidence_score=confluence_res.get("confidence_score"),
                )
                await sse_manager.broadcast("anomaly", health["event"].model_dump())

            return detected_anomaly


telemetry_ingestion = TelemetryIngestionService()
