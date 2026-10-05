from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

# --- Agent Conversation Schemas ---

class AgentTurnLog(BaseModel):
    sender: str  # e.g., "Model A (Atmospheric Specialist)", "Model B (Hardware Diagnostician)"
    role: Literal["model_a", "model_b", "arbiter"]
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ShapAttribution(BaseModel):
    feature: str
    importance: float = 0.0
    direction: Literal["positive", "negative"] = "positive"
    message: str = ""

# --- Imputation & Maintenance Schemas ---

class ImputationResult(BaseModel):
    active: bool = False
    sensor: Optional[Literal["humidity", "temperature", "pressure"]] = None
    reported: Optional[float] = None
    suggested: Optional[float] = None
    method: Optional[str] = None
    uncertainty: Optional[float] = None
    mae: Optional[float] = None
    reason: Optional[Literal["anomaly", "drift"]] = None

class ImputationAcceptRequest(BaseModel):
    station_id: str = "AGRA-01"
    sensor: str = "humidity"
    suggested: float
    reported: Optional[float] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None
    method: Optional[str] = None

class MaintenanceSensorStatus(BaseModel):
    status: str = "Healthy"
    drift_sigma: Optional[float] = 0.42
    progress: Optional[float] = 14.0
    days_to_recalibration: Optional[int] = 48
    trend: Optional[str] = "Stable"
    warmup: Optional[str] = "Calibrated"
    note: Optional[str] = None

class MaintenanceResult(BaseModel):
    humidity: MaintenanceSensorStatus = Field(default_factory=MaintenanceSensorStatus)
    temperature: Optional[MaintenanceSensorStatus] = None
    pressure: Optional[MaintenanceSensorStatus] = None

class PitchScriptStatus(BaseModel):
    active: bool = False
    phase_id: str = "BASELINE"
    phase_title: str = "Baseline Diurnal"
    phase_description: str = "Normal weather cycles. 3D Twin Green."
    elapsed_seconds: int = 0

# --- Confluence & Classification Schemas ---

ConfluenceClassification = Literal[
    "Natural Weather Event",
    "Sensor Defect",
    "Compound Event",
    "Uncertain Anomaly",
    "Nominal Baseline"
]

class ConfluenceResult(BaseModel):
    classification: ConfluenceClassification = "Nominal Baseline"
    confidence: float = 0.95
    confidence_score: float = 95.0
    p_weather: float = 0.05
    p_defect: float = 0.05
    defect_class: str = "none"
    defect_type: Optional[str] = "none"
    summary: str = "Nominal atmospheric telemetry within baseline IMD thresholds."
    action_recommended: str = "Continuous 1 Hz nominal monitoring."
    action_taken: Optional[str] = None
    severity: str = "low"
    operator_alert: bool = False
    api_fallback: bool = False
    agent_dialogue: List[AgentTurnLog] = Field(default_factory=list)

# --- Telemetry Payload Schema ---

class TelemetryPayload(BaseModel):
    station_id: str = "AGRA-01"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    temperature_c: float = 24.5
    pressure_hpa: float = 1013.25
    humidity_pct: float = 65.0
    dew_point_c: float = 17.5
    wind_speed_ms: float = 2.5
    wind_dir_deg: float = 180.0
    solar_radiation_wm2: float = 450.0
    sequence: int = 1
    source: str = "edge_simulator"
    drop_flag: int = 0
    reconstruction_error: float = 0.015
    inference_time_ms: float = 4.2
    live_attributions: List[ShapAttribution] = Field(default_factory=list)
    imd_passed: bool = True
    imd_violation: Optional[str] = None
    confluence: Optional[ConfluenceResult] = None
    imputation: Optional[ImputationResult] = None
    maintenance: Optional[MaintenanceResult] = None
    fault_type: Optional[str] = "normal"
    extra_data: Optional[Dict[str, Any]] = None

# --- Anomaly Event Schema ---

AnomalyType = Literal["rule_flag", "ai_anomaly", "compound", "sensor_health"]
AnomalyStatus = Literal["open", "acknowledged", "resolved", "ignored", "false_alarm"]

class AnomalyEvent(BaseModel):
    anomaly_id: str
    detected_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    station_id: str = "AGRA-01"
    anomaly_type: AnomalyType = "ai_anomaly"
    severity_score: float = 0.0
    classification: str = "Sensor Defect"
    culprit_sensors: List[str] = Field(default_factory=list)
    diagnostic_message: str = ""
    shap_values: List[ShapAttribution] = Field(default_factory=list)
    status: AnomalyStatus = "open"
    resolution_note: Optional[str] = None
    resolved_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    ignored_at: Optional[str] = None
    action_taken: Optional[str] = None
    action_timestamp: Optional[str] = None
    reconstruction_error: float = 0.0
    confluence: Optional[ConfluenceResult] = None
    transmitted_data: Optional[Dict[str, Any]] = None
    decision_reasoning: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None

# --- Ingestion & Simulator Control Schemas ---

class TelemetryIngestResponse(BaseModel):
    status: str = "success"
    classification: ConfluenceClassification
    reasoning: str
    agent_dialogue: List[AgentTurnLog]
    confluence: ConfluenceResult
    telemetry: TelemetryPayload

class FaultInjectionRequest(BaseModel):
    fault_type: str = "normal"
    intensity: float = 1.0
    duration_seconds: int = 30

class SimulatorStatusResponse(BaseModel):
    active_fault: str = "normal"
    pitch_script: Optional[Dict[str, Any]] = None

class StationOverview(BaseModel):
    station_id: str = "AGRA-01"
    station_name: str = "Agra Central Weather Observatory"
    latitude: float = 27.1767
    longitude: float = 78.0081
    elevation_m: float = 171.0
    status: Literal["normal", "warning", "anomaly"] = "normal"
    latest_telemetry: Optional[TelemetryPayload] = None
    active_anomalies: List[AnomalyEvent] = Field(default_factory=list)
    total_anomalies_detected: int = 0
    connection_status: str = "connected"

# --- Decision Audit Trail Schemas ---

class DecisionRecord(BaseModel):
    decision_id: str
    station_id: str = "AGRA-01"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    classification: ConfluenceClassification = "Nominal Baseline"
    confidence_score: float = 95.0
    trigger_reason: str = ""
    culprit_sensors: List[str] = Field(default_factory=list)
    action_recommended: str = ""
    dialogue: List[AgentTurnLog] = Field(default_factory=list)
    reconstruction_error: float = 0.0
    transmitted_data: Optional[Dict[str, Any]] = None
    decision_reasoning: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None

class DecisionListResponse(BaseModel):
    status: str = "success"
    total: int
    decisions: List[DecisionRecord]

