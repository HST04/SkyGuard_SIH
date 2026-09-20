import { create } from 'zustand';
import { TelemetryPayload, AnomalyEvent, PitchScriptStatus } from '@/lib/types';

interface TelemetryState {
  latestTelemetry: TelemetryPayload | null;
  telemetryHistory: TelemetryPayload[];
  anomalies: AnomalyEvent[];
  activeAnomaly: AnomalyEvent | null;
  selectedSensor: string; // 'station' | 'temperature' | 'humidity' | 'pressure' | 'wind' | 'solar'
  stationStatus: 'normal' | 'warning' | 'anomaly';
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
  activeFault: string;
  pitchScriptStatus: PitchScriptStatus | null;
  
  // Actions
  setLatestTelemetry: (payload: TelemetryPayload) => void;
  setTelemetryHistory: (history: TelemetryPayload[]) => void;
  addAnomaly: (anomaly: AnomalyEvent) => void;
  updateAnomalyStatus: (anomalyId: string, status: 'open' | 'acknowledged' | 'resolved' | 'false_alarm', note?: string) => void;
  setSelectedSensor: (sensor: string) => void;
  setConnectionStatus: (status: 'connecting' | 'connected' | 'disconnected') => void;
  setSimulatorState: (fault: string, pitchStatus: PitchScriptStatus | null) => void;
  clearAnomalies: () => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  latestTelemetry: null,
  telemetryHistory: [],
  anomalies: [],
  activeAnomaly: null,
  selectedSensor: 'station',
  stationStatus: 'normal',
  connectionStatus: 'connecting',
  activeFault: 'normal',
  pitchScriptStatus: null,

  setLatestTelemetry: (payload: TelemetryPayload) =>
    set((state) => {
      // Append to history and keep last 60 points
      const newHistory = [...state.telemetryHistory, payload].slice(-60);
      return {
        latestTelemetry: payload,
        telemetryHistory: newHistory,
      };
    }),

  setTelemetryHistory: (history: TelemetryPayload[]) =>
    set({ telemetryHistory: history }),

  addAnomaly: (anomaly: AnomalyEvent) =>
    set((state) => {
      // Avoid duplicate IDs
      const exists = state.anomalies.some((a) => a.anomaly_id === anomaly.anomaly_id);
      const updatedAnomalies = exists
        ? state.anomalies.map((a) => (a.anomaly_id === anomaly.anomaly_id ? anomaly : a))
        : [anomaly, ...state.anomalies].slice(0, 50);

      // Highest severity determines station health status
      const hasCritical = updatedAnomalies.some((a) => a.status === 'open' && a.severity_score >= 0.75);
      const hasWarning = updatedAnomalies.some((a) => a.status === 'open');

      const status = hasCritical ? 'anomaly' : (hasWarning ? 'warning' : 'normal');

      // Auto-target 3D camera to culprit sensor
      const culprit = anomaly.culprit_sensors && anomaly.culprit_sensors.length > 0 
        ? anomaly.culprit_sensors[0] 
        : state.selectedSensor;

      return {
        anomalies: updatedAnomalies,
        activeAnomaly: anomaly,
        stationStatus: status,
        selectedSensor: culprit,
      };
    }),

  updateAnomalyStatus: (anomalyId: string, newStatus: 'open' | 'acknowledged' | 'resolved' | 'false_alarm', note?: string) =>
    set((state) => {
      const updatedAnomalies = state.anomalies.map((a) =>
        a.anomaly_id === anomalyId ? { ...a, status: newStatus, resolution_note: note || a.resolution_note } : a
      );

      const hasCritical = updatedAnomalies.some((a) => a.status === 'open' && a.severity_score >= 0.75);
      const hasWarning = updatedAnomalies.some((a) => a.status === 'open');
      const status = hasCritical ? 'anomaly' : (hasWarning ? 'warning' : 'normal');

      const active = updatedAnomalies.find((a) => a.status === 'open') || null;

      return {
        anomalies: updatedAnomalies,
        stationStatus: status,
        activeAnomaly: active,
      };
    }),

  setSelectedSensor: (sensor: string) => set({ selectedSensor: sensor }),

  setConnectionStatus: (status: 'connecting' | 'connected' | 'disconnected') =>
    set({ connectionStatus: status }),

  setSimulatorState: (fault: string, pitchStatus: PitchScriptStatus | null) =>
    set({ activeFault: fault, pitchScriptStatus: pitchStatus }),

  clearAnomalies: () =>
    set({
      anomalies: [],
      activeAnomaly: null,
      stationStatus: 'normal',
      selectedSensor: 'station',
    }),
}));
