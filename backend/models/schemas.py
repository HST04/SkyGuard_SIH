from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class ShapAttribution(BaseModel):
    feature: str
    importance: float
    direction: Literal["positive", "negative"]
    message: str

class TelemetryPayload(BaseModel):
    station_id: str = "AGRA-01"
    timestamp: str
    temperature_c: float
    pressure_hpa: float
    humidity_pct: float
    dew_point_c: float
    wind_speed_ms: float = 2.5
    wind_dir_deg: float = 180.0
    solar_radiation_wm2: float = 450.0
    sequence: int
    source: str = "edge-simulator"
    drop_flag: int = 0
    reconstruction_error: float = 0.0142
    inference_time_ms: float = 2.4
    live_attributions: List[ShapAttribution] = []

class AnomalyEvent(BaseModel):
    anomaly_id: str
    detected_at: str
    station_id: str
    anomaly_type: Literal["rule_flag", "ai_anomaly", "compound", "sensor_health"]
    severity_score: float = Field(..., ge=0.0, le=1.0)
    culprit_sensors: List[str]
    diagnostic_message: str
    shap_values: List[ShapAttribution] = []
    status: Literal["open", "acknowledged", "resolved", "false_alarm"] = "open"
    resolution_note: Optional[str] = None
    resolved_at: Optional[str] = None
    reconstruction_error: float = 0.0

class OperatorFeedback(BaseModel):
    anomaly_id: str
    label: Literal["false_alarm", "confirmed_fault"]
    note: Optional[str] = None

class AnomalyUpdateRequest(BaseModel):
    status: Literal["open", "acknowledged", "resolved", "false_alarm"]
    resolution_note: Optional[str] = None

class StationOverview(BaseModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    elevation_m: float
    status: Literal["normal", "warning", "anomaly"]
    latest_telemetry: Optional[TelemetryPayload] = None
    active_anomalies: List[AnomalyEvent] = []
    total_anomalies_detected: int = 0
    connection_status: str = "connected"

class FaultInjectionRequest(BaseModel):
    fault_type: Literal[
        "normal",
        "heat_spike",
        "pressure_drop",
        "stuck_humidity",
        "humidity_drift",
        "cross_decoupling",
        "sensor_noise",
        "valid_squall"
    ]
    intensity: float = 1.0
    duration_seconds: int = 30

class PitchScriptStatus(BaseModel):
    active: bool
    phase_id: str
    phase_title: str
    phase_description: str
    elapsed_seconds: int
    total_seconds: int = 300
    expected_status: str
