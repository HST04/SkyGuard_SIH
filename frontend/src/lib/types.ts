export type AnomalyType = 'rule_flag' | 'ai_anomaly' | 'compound' | 'sensor_health';
export type AnomalyStatus = 'open' | 'acknowledged' | 'resolved' | 'false_alarm';

export interface ShapAttribution {
  feature: string;
  importance: number;
  direction: 'positive' | 'negative';
  message: string;
}

export type ConfluenceClassification =
  | 'Natural Weather Event'
  | 'Sensor Defect'
  | 'Compound Event'
  | 'Uncertain Anomaly'
  | 'Nominal Baseline';

export interface ConfluenceResult {
  classification: ConfluenceClassification;
  confidence: number; // 0.0 - 1.0 (or percentage e.g. 92.4%)
  p_weather: number;  // 0.0 - 1.0
  p_defect: number;   // 0.0 - 1.0
  defect_class?: string;
  summary?: string;
  action_recommended?: string;
}

export type MaintenanceHealthStatus =
  | 'Learning'
  | 'Healthy'
  | 'Watch'
  | 'At Risk'
  | 'Recalibrate Now'
  | 'Not Tracked';

export interface MaintenanceSensorStatus {
  status: MaintenanceHealthStatus;
  drift_sigma?: number | null;
  progress?: number;
  days_to_recalibration?: number | null;
  trend?: string;
  warmup?: string;
  note?: string;
}

export interface MaintenanceResult {
  humidity: MaintenanceSensorStatus;
  temperature?: MaintenanceSensorStatus;
  pressure?: MaintenanceSensorStatus;
}

export interface ImputationResult {
  active: boolean;
  sensor?: 'humidity' | 'temperature' | 'pressure';
  reported?: number;
  suggested?: number | null;
  method?: string;
  uncertainty?: number | null;
  mae?: number;
  reason?: 'anomaly' | 'drift';
}

export interface ImputationAcceptRequest {
  station_id: string;
  sensor: 'humidity' | 'temperature' | 'pressure';
  suggested: number;
  reported?: number;
  timestamp?: string;
  sequence?: number;
  method?: string;
}

export interface TelemetryPayload {
  station_id: string;
  timestamp: string;
  temperature_c: number;
  pressure_hpa: number;
  humidity_pct: number;
  dew_point_c: number;
  wind_speed_ms: number;
  wind_dir_deg: number;
  solar_radiation_wm2: number;
  sequence: number;
  source: string;
  drop_flag: number;
  reconstruction_error: number;
  inference_time_ms: number;
  live_attributions: ShapAttribution[];
  // Extended fields
  confluence?: ConfluenceResult;
  maintenance?: MaintenanceResult;
  imputation?: ImputationResult;
  weather?: {
    event: boolean;
    cooldown: boolean;
    source: string;
  };
}

export interface AnomalyEvent {
  anomaly_id: string;
  detected_at: string;
  station_id: string;
  anomaly_type: AnomalyType;
  severity_score: number;
  culprit_sensors: string[];
  diagnostic_message: string;
  shap_values: ShapAttribution[];
  status: AnomalyStatus;
  resolution_note?: string | null;
  resolved_at?: string | null;
  reconstruction_error: number;
  confluence?: ConfluenceResult;
}

export interface OperatorFeedback {
  anomaly_id: string;
  label: 'false_alarm' | 'confirmed_fault';
  note?: string;
}

export interface AnomalyUpdateRequest {
  status: AnomalyStatus;
  resolution_note?: string;
}

export interface StationOverview {
  station_id: string;
  station_name: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  status: 'normal' | 'warning' | 'anomaly';
  latest_telemetry?: TelemetryPayload | null;
  active_anomalies: AnomalyEvent[];
  total_anomalies_detected: number;
  connection_status: string;
}

export interface FaultInjectionRequest {
  fault_type:
    | 'normal'
    | 'heat_spike'
    | 'pressure_drop'
    | 'stuck_humidity'
    | 'humidity_drift'
    | 'cross_decoupling'
    | 'sensor_noise'
    | 'valid_squall';
  intensity?: number;
  duration_seconds?: number;
}

export interface PitchScriptStatus {
  active: boolean;
  phase_id: string;
  phase_title: string;
  phase_description: string;
  elapsed_seconds: number;
  total_seconds: number;
  expected_status: string;
}
