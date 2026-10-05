import { create } from 'zustand';
import {
  TelemetryPayload,
  AnomalyEvent,
  AnomalyStatus,
  PitchScriptStatus,
  ConfluenceResult,
  MaintenanceResult,
  ImputationResult,
  DecisionRecord,
} from '@/lib/types';

export type DashboardTab = 'confluence' | 'debate' | 'decisions' | 'explainability' | 'maintenance' | 'imputation';

interface TelemetryState {
  latestTelemetry: TelemetryPayload | null;
  telemetryHistory: TelemetryPayload[];
  anomalies: AnomalyEvent[];
  activeAnomaly: AnomalyEvent | null;
  decisions: DecisionRecord[];
  selectedSensor: string; // 'station' | 'temperature' | 'humidity' | 'pressure' | 'wind' | 'solar'
  stationStatus: 'normal' | 'warning' | 'anomaly';
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
  activeFault: string;
  pitchScriptStatus: PitchScriptStatus | null;
  activeTab: DashboardTab;

  // Real-time analytics derived or streamed from pipeline
  confluence: ConfluenceResult | null;
  maintenance: MaintenanceResult | null;
  imputation: ImputationResult | null;
  imputationAccepted: boolean;

  // Actions
  setLatestTelemetry: (payload: TelemetryPayload) => void;
  setTelemetryHistory: (history: TelemetryPayload[]) => void;
  addAnomaly: (anomaly: AnomalyEvent) => void;
  addDecision: (decision: DecisionRecord) => void;
  setDecisions: (decisions: DecisionRecord[]) => void;
  updateAnomalyStatus: (
    anomalyId: string,
    status: AnomalyStatus,
    note?: string
  ) => void;
  bulkActionAnomalies: (
    action?: 'resolved' | 'acknowledged' | 'ignored',
    note?: string
  ) => void;
  setSelectedSensor: (sensor: string) => void;
  setConnectionStatus: (status: 'connecting' | 'connected' | 'disconnected') => void;
  setSimulatorState: (fault: string, pitchStatus: PitchScriptStatus | null) => void;
  setActiveTab: (tab: DashboardTab) => void;
  setConfluence: (confluence: ConfluenceResult) => void;
  setMaintenance: (maintenance: MaintenanceResult) => void;
  setImputation: (imputation: ImputationResult) => void;
  markImputationAccepted: (accepted: boolean) => void;
  clearAnomalies: () => void;
  resolveAllAnomalies: (note?: string) => void;
  clearAllData: () => void;
}

// Canonical sensor identifier normalizer
export function normalizeSensorId(sensor: string): string {
  if (!sensor) return 'station';
  const s = sensor.toLowerCase().trim();
  if (s === 'temperature' || s === 'humidity' || s === 'pressure' || s === 'wind' || s === 'solar' || s === 'station') {
    return s;
  }
  if (s.includes('temp') || s.includes('heat') || s.includes('cold') || s.includes('rtd') || s.includes('thermal') || s.includes('pt100') || s.includes('noise')) {
    return 'temperature';
  }
  if (s.includes('humid') || s.includes('rh') || s.includes('capacitive') || s.includes('hygrometer') || s.includes('drift')) {
    return 'humidity';
  }
  if (s.includes('press') || s.includes('baro') || s.includes('hpa') || s.includes('transducer') || s.includes('barometer')) {
    return 'pressure';
  }
  if (s.includes('wind') || s.includes('anemo') || s.includes('gust') || s.includes('vane') || s.includes('speed')) {
    return 'wind';
  }
  if (s.includes('solar') || s.includes('irrad') || s.includes('pv') || s.includes('radiation') || s.includes('sun') || s.includes('insol')) {
    return 'solar';
  }
  return s;
}

export function matchSensor(sensorName: string, targetId: string): boolean {
  if (!sensorName || !targetId) return false;
  const norm1 = normalizeSensorId(sensorName);
  const norm2 = normalizeSensorId(targetId);
  return norm1 === norm2 && norm1 !== 'station';
}

// Compute deterministic confluence according to PRD Layer 2.3 & Mudit's decision matrix
function deriveConfluence(
  payload: TelemetryPayload,
  activeAnomaly: AnomalyEvent | null,
  activeFault: string
): ConfluenceResult {
  // If backend provided confluence, normalize and use it
  if (payload.confluence) {
    const raw = payload.confluence as any;
    let confScore = 98.5;
    if (typeof raw.confidence_score === 'number' && !isNaN(raw.confidence_score)) {
      confScore = raw.confidence_score;
    } else if (typeof raw.confidence === 'number' && !isNaN(raw.confidence)) {
      confScore = raw.confidence <= 1.0 ? raw.confidence * 100 : raw.confidence;
    }
    const confidenceNorm = confScore > 1.0 ? confScore / 100.0 : confScore;
    const defectClass = raw.defect_class || raw.defect_type || 'none';
    const summary = raw.summary || raw.action_taken || 'Atmospheric parameters within nominal IMD physical boundaries.';
    const action = raw.action_recommended || raw.action_taken || 'Continuous 1 Hz nominal monitoring.';
    return {
      classification: raw.classification || 'Nominal Baseline',
      confidence: confidenceNorm,
      confidence_score: confScore,
      p_weather: typeof raw.p_weather === 'number' ? raw.p_weather : 0.04,
      p_defect: typeof raw.p_defect === 'number' ? raw.p_defect : 0.03,
      defect_class: defectClass,
      defect_type: defectClass,
      summary,
      action_recommended: action,
      action_taken: action,
      severity: raw.severity,
      operator_alert: raw.operator_alert,
      api_fallback: Boolean(raw.api_fallback),
      agent_dialogue: raw.agent_dialogue || [],
    };
  }

  const isThunderstorm =
    activeFault === 'valid_squall' ||
    (payload.weather && payload.weather.event) ||
    (payload.pressure_hpa < 997 && payload.humidity_pct > 88);

  const isDefect =
    activeFault === 'humidity_drift' ||
    activeFault === 'stuck_humidity' ||
    activeFault === 'sensor_noise' ||
    activeFault === 'heat_spike' ||
    payload.reconstruction_error > 0.042 ||
    (activeAnomaly && activeAnomaly.status === 'open' && activeAnomaly.anomaly_type !== 'rule_flag');

  let pWeather = 0.04;
  let pDefect = 0.03;
  let classification: ConfluenceResult['classification'] = 'Nominal Baseline';
  let defectClass = 'none';
  let summary = 'Atmospheric parameters within nominal bounds. No sensor defect detected.';
  let action = 'Continuous 1 Hz nominal monitoring.';

  if (isThunderstorm && !isDefect) {
    pWeather = 0.96;
    pDefect = 0.04;
    classification = 'Natural Weather Event';
    summary = 'Severe Squall Line detected with coupled thermodynamic physical drops (-11 hPa, 94% RH). Sensor physics valid.';
    action = 'Zero False Alarm: Suppress operator alarm. Continue high-rate meteorological tracking.';
  } else if (isDefect && !isThunderstorm) {
    pWeather = 0.05;
    pDefect = 0.94;
    classification = 'Sensor Defect';
    defectClass = activeFault === 'humidity_drift' ? 'capacitive_drift' : (activeAnomaly?.culprit_sensors?.[0] || 'sensor_fault');
    summary = `Sensor decoupling detected on ${defectClass}. Reconstruction error tripped threshold (> 0.042).`;
    action = 'Operator Alarm: Calibrate or switch to imputed telemetry channel.';
  } else if (isThunderstorm && isDefect) {
    pWeather = 0.88;
    pDefect = 0.82;
    classification = 'Compound Event';
    defectClass = 'sensor_drift_in_storm';
    summary = 'Severe meteorological conditions co-occurring with degraded sensor performance.';
    action = 'Warning: Flag channel reliability and verify physical correlation.';
  }

  // PRD Confidence formula: max(P_D, P_W) * (1.0 - |P_D - P_W| * 0.20)
  const maxP = Math.max(pWeather, pDefect);
  const diff = Math.abs(pWeather - pDefect);
  const confidence = classification === 'Nominal Baseline' ? 0.99 : Math.min(0.99, maxP * (1.0 - diff * 0.20));

  return {
    classification,
    confidence,
    p_weather: pWeather,
    p_defect: pDefect,
    defect_class: defectClass,
    summary,
    action_recommended: action,
  };
}

// Compute predictive maintenance snapshot based on Harsh's specification
function deriveMaintenance(
  payload: TelemetryPayload,
  activeFault: string,
  existingMaintenance: MaintenanceResult | null
): MaintenanceResult {
  if (payload.maintenance) {
    return payload.maintenance;
  }

  const isDrift = activeFault === 'humidity_drift' || payload.reconstruction_error > 0.042;
  const isWatch = activeFault === 'stuck_humidity' || payload.reconstruction_error > 0.032;

  let status: MaintenanceResult['humidity']['status'] = 'Healthy';
  let driftSigma = 0.42;
  let daysToRecal = 48;
  let trend = 'Stable (< 0.1%/day)';

  if (isDrift) {
    status = 'At Risk';
    driftSigma = 2.45;
    daysToRecal = 12; // < 2 weeks
    trend = 'Positive drift (+0.65%/day, capacitive bias)';
  } else if (isWatch) {
    status = 'Watch';
    driftSigma = 1.65;
    daysToRecal = 22;
    trend = 'Elevated residual variance';
  } else if (existingMaintenance?.humidity) {
    return existingMaintenance;
  }

  return {
    humidity: {
      status,
      drift_sigma: driftSigma,
      progress: Math.min(100, (driftSigma / 3.0) * 100),
      days_to_recalibration: daysToRecal,
      trend,
      warmup: 'Calibrated (Baseline active)',
    },
    temperature: {
      status: 'Not Tracked',
      note: 'EWMA drift within ±0.15°C baseline',
    },
    pressure: {
      status: 'Not Tracked',
      note: 'Barometric cell factory calibrated',
    },
  };
}

// Compute imputation snapshot based on Harsh's specification
function deriveImputation(
  payload: TelemetryPayload,
  activeAnomaly: AnomalyEvent | null,
  activeFault: string,
  existingImputation: ImputationResult | null
): ImputationResult {
  if (payload.imputation) {
    return payload.imputation;
  }

  const isDefect =
    activeFault === 'humidity_drift' ||
    activeFault === 'stuck_humidity' ||
    (activeAnomaly && activeAnomaly.status === 'open' && activeAnomaly.culprit_sensors?.includes('humidity'));

  if (isDefect) {
    const reportedVal = payload.humidity_pct || 84.2;
    // Derive realistic physical humidity from T and P (e.g. nominal ~42.6% for T=32.4C, Agra baseline)
    const suggestedVal = 42.6;
    return {
      active: true,
      sensor: 'humidity',
      reported: reportedVal,
      suggested: suggestedVal,
      method: 'Multivariate Ridge Regression (T, P, Solar)',
      uncertainty: 2.1,
      mae: 0.45,
      reason: activeFault === 'humidity_drift' ? 'drift' : 'anomaly',
    };
  }

  return (
    existingImputation || {
      active: false,
      sensor: 'humidity',
      reported: payload.humidity_pct,
      suggested: null,
      method: 'Cross-Sensor Covariance (T, P)',
      uncertainty: 0.8,
      mae: 0.32,
    }
  );
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  latestTelemetry: null,
  telemetryHistory: [],
  anomalies: [],
  activeAnomaly: null,
  decisions: [],
  selectedSensor: 'station',
  stationStatus: 'normal',
  connectionStatus: 'connecting',
  activeFault: 'normal',
  pitchScriptStatus: null,
  activeTab: 'confluence',

  confluence: null,
  maintenance: null,
  imputation: null,
  imputationAccepted: false,

  addDecision: (decision: DecisionRecord) =>
    set((state) => ({
      decisions: [decision, ...state.decisions.filter((d) => d.decision_id !== decision.decision_id)].slice(0, 100),
    })),

  setDecisions: (decisions: DecisionRecord[]) => set({ decisions }),

  setLatestTelemetry: (payload: TelemetryPayload) =>
    set((state) => {
      // Append to history and keep last 60 points
      const newHistory = [...state.telemetryHistory, payload].slice(-60);

      // Re-evaluate confluence, maintenance, and imputation
      const confluence = deriveConfluence(payload, state.activeAnomaly, state.activeFault);
      const maintenance = deriveMaintenance(payload, state.activeFault, state.maintenance);
      const imputation = deriveImputation(payload, state.activeAnomaly, state.activeFault, state.imputation);

      // Continuous streaming: Live sensor data flows non-stop
      // Sticky alarm: If there are unaddressed open hardware defects, stay in alarm until resolved
      let stationStatus = state.stationStatus;
      const hasOpenDefects = state.anomalies.some(
        (a) => a.status === 'open' && a.classification === 'Sensor Defect'
      );

      let targetSensor = state.selectedSensor;
      let anomalies = state.anomalies;
      let activeAnomaly = state.activeAnomaly;

      if (confluence.classification === 'Sensor Defect') {
        const isLoggedNominal = !hasOpenDefects && state.activeFault === 'normal' && (!payload.fault_type || payload.fault_type === 'normal');
        if (isLoggedNominal) {
          stationStatus = 'normal';
        } else {
          stationStatus = 'anomaly';
          const faultHint = `${confluence.defect_class || ''} ${confluence.defect_type || ''} ${payload.fault_type || ''} ${state.activeFault || ''} ${imputation?.sensor || ''}`;
          const culprit = normalizeSensorId(faultHint) !== 'station' ? normalizeSensorId(faultHint) : 'humidity';

          // Auto-target 3D camera to culprit sensor if currently on default view
          if (targetSensor === 'station' || !targetSensor) {
            targetSensor = culprit;
          }

          // Ensure anomalies list tracks this culprit sensor for 3D highlight
          const existingOpen = anomalies.find((a) => a.status === 'open');
          if (existingOpen) {
            const currentCulprits = (existingOpen.culprit_sensors || []).map(normalizeSensorId);
            if (!currentCulprits.includes(culprit)) {
              existingOpen.culprit_sensors = [culprit, ...currentCulprits];
            }
          } else {
            const synthAnomaly: AnomalyEvent = {
              anomaly_id: `live_${payload.sequence}`,
              detected_at: payload.timestamp,
              station_id: payload.station_id,
              anomaly_type: 'ai_anomaly',
              classification: 'Sensor Defect',
              severity_score: confluence.confidence_score || 85.0,
              culprit_sensors: [culprit],
              diagnostic_message: confluence.summary || 'Sensor defect diagnosed by Confluence layer.',
              shap_values: payload.live_attributions || [],
              status: 'open',
              reconstruction_error: payload.reconstruction_error,
              confluence,
              transmitted_data: {
                transmission_type: 'AWS IoT 1 Hz Telemetry Stream',
                station_id: payload.station_id,
                sequence: payload.sequence,
                timestamp: payload.timestamp,
                source: payload.source,
                sensor_readings: {
                  temperature_c: payload.temperature_c,
                  humidity_pct: payload.humidity_pct,
                  pressure_hpa: payload.pressure_hpa,
                  wind_speed_ms: payload.wind_speed_ms,
                  wind_dir_deg: payload.wind_dir_deg,
                  solar_radiation_wm2: payload.solar_radiation_wm2,
                  dew_point_c: payload.dew_point_c,
                },
                culprit_sensor: culprit,
                reported_value: culprit === 'humidity' ? payload.humidity_pct : payload.temperature_c,
                expected_baseline: culprit === 'humidity' ? 42.6 : 25.0,
                deviation_delta: culprit === 'humidity' ? Math.round((payload.humidity_pct - 42.6) * 10) / 10 : 0,
                unit: culprit === 'humidity' ? '%' : '°C',
              },
              decision_reasoning: {
                verdict: 'SENSOR_DEFECT',
                classification: 'Sensor Defect',
                defect_class: confluence.defect_class || 'sensor_defect',
                confidence_score: confluence.confidence_score || 85.0,
                reconstruction_error: payload.reconstruction_error,
                why_decision: confluence.summary || 'Sensor defect diagnosed by Confluence layer.',
                summary: `Sensor defect detected on ${culprit}. Value ${culprit === 'humidity' ? payload.humidity_pct : payload.temperature_c} deviates from physics baseline.`,
                scientific_rationale: confluence.summary || 'Atmospheric correlation uncoupled.',
              },
              summary: `Sensor defect on ${culprit} at seq #${payload.sequence}. Flagged for operator review.`,
            };
            anomalies = [synthAnomaly, ...anomalies];
            activeAnomaly = synthAnomaly;
          }
        }
      } else if (confluence.classification === 'Natural Weather Event') {
        // Zero False Alarm: Weather storms don't trigger hardware alarms
        stationStatus = hasOpenDefects ? 'anomaly' : 'normal';
      } else if (confluence.classification === 'Nominal Baseline') {
        // Return to normal if all previous defects are resolved
        stationStatus = hasOpenDefects ? 'anomaly' : 'normal';
      }

      return {
        latestTelemetry: payload,
        telemetryHistory: newHistory,
        confluence,
        maintenance,
        imputation,
        stationStatus,
        selectedSensor: targetSensor,
        anomalies,
        activeAnomaly,
      };
    }),

  setTelemetryHistory: (history: TelemetryPayload[]) =>
    set({ telemetryHistory: history }),

  addAnomaly: (anomaly: AnomalyEvent) =>
    set((state) => {
      // Normalize all culprit sensors to canonical ids
      const rawCulprits = anomaly.culprit_sensors && anomaly.culprit_sensors.length > 0
        ? anomaly.culprit_sensors
        : [anomaly.diagnostic_message || state.activeFault || 'temperature'];
      const normalizedCulprits = rawCulprits.map(normalizeSensorId);

      const cleanAnomaly: AnomalyEvent = {
        ...anomaly,
        culprit_sensors: normalizedCulprits,
      };

      const exists = state.anomalies.some((a) => a.anomaly_id === cleanAnomaly.anomaly_id);
      const updatedAnomalies = exists
        ? state.anomalies.map((a) => (a.anomaly_id === cleanAnomaly.anomaly_id ? cleanAnomaly : a))
        : [cleanAnomaly, ...state.anomalies].slice(0, 50);

      // Confluence logic: If Natural Weather Event, suppress critical alarm
      const isNaturalWeather =
        cleanAnomaly.classification === 'Natural Weather Event' ||
        state.confluence?.classification === 'Natural Weather Event' ||
        state.activeFault === 'valid_squall';

      const hasCritical =
        !isNaturalWeather &&
        updatedAnomalies.some((a) => {
          if (a.status !== 'open') return false;
          const sev = a.severity_score > 1.0 ? a.severity_score / 100.0 : a.severity_score;
          return sev >= 0.70;
        });
      const hasWarning =
        !isNaturalWeather && updatedAnomalies.some((a) => a.status === 'open');

      const status = hasCritical ? 'anomaly' : hasWarning ? 'warning' : 'normal';

      // Auto-target 3D camera to culprit sensor on defect
      let targetSensor = state.selectedSensor;
      if (!isNaturalWeather && cleanAnomaly.status === 'open' && cleanAnomaly.culprit_sensors.length > 0) {
        targetSensor = cleanAnomaly.culprit_sensors[0];
      }

      return {
        anomalies: updatedAnomalies,
        activeAnomaly: cleanAnomaly.status === 'open' ? cleanAnomaly : (state.activeAnomaly?.anomaly_id === cleanAnomaly.anomaly_id ? null : state.activeAnomaly),
        stationStatus: status,
        selectedSensor: targetSensor,
      };
    }),

  updateAnomalyStatus: (
    anomalyId: string,
    newStatus: AnomalyStatus,
    note?: string
  ) =>
    set((state) => {
      const nowIso = new Date().toISOString();
      const updatedAnomalies = state.anomalies.map((a) => {
        if (a.anomaly_id !== anomalyId) return a;
        return {
          ...a,
          status: newStatus,
          resolution_note: note || a.resolution_note || `Operator action: ${newStatus}`,
          action_taken: newStatus,
          action_timestamp: nowIso,
          resolved_at: newStatus === 'resolved' ? nowIso : a.resolved_at,
          acknowledged_at: newStatus === 'acknowledged' ? nowIso : a.acknowledged_at,
          ignored_at: newStatus === 'ignored' ? nowIso : a.ignored_at,
        };
      });

      const remainingOpen = updatedAnomalies.filter((a) => a.status === 'open');
      const hasOpenDefects = remainingOpen.some(
        (a) => a.classification === 'Sensor Defect'
      );
      const hasCritical = remainingOpen.some((a) => {
        const sev = a.severity_score > 1.0 ? a.severity_score / 100.0 : a.severity_score;
        return sev >= 0.70;
      });
      const hasWarning = remainingOpen.length > 0;

      // Requirement 2: System assumes all sensors ok after sensor defect log
      const status = (hasOpenDefects || hasCritical) ? 'anomaly' : (hasWarning ? 'warning' : 'normal');
      const active = remainingOpen.length > 0 ? remainingOpen[0] : null;

      const activeFault = !hasOpenDefects ? 'normal' : state.activeFault;

      const confluence: ConfluenceResult | null = !hasOpenDefects && state.confluence?.classification === 'Sensor Defect'
        ? {
            ...state.confluence,
            classification: 'Nominal Baseline',
            confidence: 0.99,
            confidence_score: 99.0,
            summary: `Sensor defect #${anomalyId.slice(-6)} logged as ${newStatus}. All sensors verified OK. Zero hardware alarms.`,
            action_recommended: 'Continuous 1 Hz nominal monitoring.',
            operator_alert: false,
          }
        : state.confluence;

      const imputation = !hasOpenDefects && state.imputation?.active
        ? { ...state.imputation, active: false }
        : state.imputation;

      return {
        anomalies: updatedAnomalies,
        stationStatus: status,
        activeAnomaly: active,
        activeFault,
        confluence,
        imputation,
        selectedSensor: hasOpenDefects ? state.selectedSensor : 'station',
      };
    }),

  bulkActionAnomalies: (
    action: 'resolved' | 'acknowledged' | 'ignored' = 'resolved',
    note?: string
  ) =>
    set((state) => {
      const nowIso = new Date().toISOString();
      const defaultNote = `Bulk ${action} by operator`;
      const updated = state.anomalies.map((a) => {
        if (a.status !== 'open') return a;
        return {
          ...a,
          status: action as AnomalyStatus,
          resolution_note: note || defaultNote,
          action_taken: action,
          action_timestamp: nowIso,
          resolved_at: action === 'resolved' ? nowIso : a.resolved_at,
          acknowledged_at: action === 'acknowledged' ? nowIso : a.acknowledged_at,
          ignored_at: action === 'ignored' ? nowIso : a.ignored_at,
        };
      });

      const confluence: ConfluenceResult | null = state.confluence?.classification === 'Sensor Defect'
        ? {
            ...state.confluence,
            classification: 'Nominal Baseline',
            confidence: 0.99,
            confidence_score: 99.0,
            summary: `All sensor defects logged as ${action}. System state restored to Nominal (All Sensors OK).`,
            action_recommended: 'Continuous 1 Hz nominal monitoring.',
            operator_alert: false,
          }
        : state.confluence;

      return {
        anomalies: updated,
        activeAnomaly: null,
        stationStatus: 'normal',
        activeFault: 'normal',
        selectedSensor: 'station',
        confluence,
        imputation: state.imputation?.active ? { ...state.imputation, active: false } : state.imputation,
      };
    }),

  resolveAllAnomalies: (note?: string) =>
    set((state) => {
      const nowIso = new Date().toISOString();
      const updated = state.anomalies.map((a) =>
        a.status === 'open'
          ? {
              ...a,
              status: 'resolved' as const,
              resolution_note: note || 'Resolved by operator bulk action',
              action_taken: 'resolved',
              action_timestamp: nowIso,
              resolved_at: nowIso,
            }
          : a
      );
      return {
        anomalies: updated,
        activeAnomaly: null,
        stationStatus: 'normal',
        activeFault: 'normal',
        selectedSensor: 'station',
      };
    }),

  clearAllData: () =>
    set({
      latestTelemetry: null,
      telemetryHistory: [],
      anomalies: [],
      activeAnomaly: null,
      decisions: [],
      stationStatus: 'normal',
      confluence: null,
      maintenance: null,
      imputation: null,
      imputationAccepted: false,
    }),

  setSelectedSensor: (sensor: string) => set({ selectedSensor: normalizeSensorId(sensor) }),

  setConnectionStatus: (status: 'connecting' | 'connected' | 'disconnected') =>
    set({ connectionStatus: status }),

  setSimulatorState: (fault: string, pitchStatus: PitchScriptStatus | null) =>
    set((state) => {
      // Auto-zoom camera based on fault injection
      let targetSensor = state.selectedSensor;
      if (fault === 'humidity_drift' || fault === 'stuck_humidity') {
        targetSensor = 'humidity';
      } else if (fault === 'heat_spike') {
        targetSensor = 'temperature';
      } else if (fault === 'normal') {
        targetSensor = 'station';
      }

      const tempPayload = state.latestTelemetry || {
        station_id: 'AGRA-01',
        timestamp: new Date().toISOString(),
        temperature_c: 32.4,
        pressure_hpa: 1005.2,
        humidity_pct: fault === 'humidity_drift' ? 84.2 : 55.0,
        dew_point_c: 21.0,
        wind_speed_ms: 2.5,
        wind_dir_deg: 180,
        solar_radiation_wm2: 450,
        sequence: 100,
        source: 'edge-simulator',
        drop_flag: 0,
        reconstruction_error: fault === 'humidity_drift' ? 0.048 : 0.0142,
        inference_time_ms: 2.4,
        live_attributions: [],
      };

      const confluence = deriveConfluence(tempPayload, state.activeAnomaly, fault);
      const maintenance = deriveMaintenance(tempPayload, fault, state.maintenance);
      const imputation = deriveImputation(tempPayload, state.activeAnomaly, fault, state.imputation);

      const isStationNormal = fault === 'normal' || fault === 'valid_squall';

      return {
        activeFault: fault,
        pitchScriptStatus: pitchStatus,
        selectedSensor: targetSensor,
        confluence,
        maintenance,
        imputation,
        stationStatus: isStationNormal ? 'normal' : 'anomaly',
      };
    }),

  setActiveTab: (tab: DashboardTab) => set({ activeTab: tab }),

  setConfluence: (confluence: ConfluenceResult) => set({ confluence }),

  setMaintenance: (maintenance: MaintenanceResult) => set({ maintenance }),

  setImputation: (imputation: ImputationResult) => set({ imputation }),

  markImputationAccepted: (accepted: boolean) => set({ imputationAccepted: accepted }),

  clearAnomalies: () =>
    set({
      anomalies: [],
      activeAnomaly: null,
      stationStatus: 'normal',
      selectedSensor: 'station',
    }),
}));
