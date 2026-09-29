import {
  TelemetryPayload,
  AnomalyEvent,
  StationOverview,
  AnomalyStatus,
  OperatorFeedback,
  PitchScriptStatus,
  ImputationAcceptRequest,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => res.statusText);
    throw new Error(`API error ${res.status}: ${errorText}`);
  }

  return res.json();
}

export const api = {
  // Telemetry
  async getLatestTelemetry(stationId = 'AGRA-01'): Promise<TelemetryPayload | null> {
    try {
      return await fetchJson<TelemetryPayload>(`${API_BASE}/telemetry/latest?station_id=${stationId}`);
    } catch {
      return null;
    }
  },

  async getTelemetryHistory(stationId = 'AGRA-01', limit = 60): Promise<TelemetryPayload[]> {
    try {
      return await fetchJson<TelemetryPayload[]>(`${API_BASE}/telemetry/history?station_id=${stationId}&limit=${limit}`);
    } catch {
      return [];
    }
  },

  async getStationOverview(stationId = 'AGRA-01'): Promise<StationOverview | null> {
    try {
      return await fetchJson<StationOverview>(`${API_BASE}/telemetry/overview?station_id=${stationId}`);
    } catch {
      return null;
    }
  },

  // Anomalies & Feedback
  async getAnomalies(status?: AnomalyStatus, limit = 50): Promise<AnomalyEvent[]> {
    try {
      const q = status ? `?status=${status}&limit=${limit}` : `?limit=${limit}`;
      return await fetchJson<AnomalyEvent[]>(`${API_BASE}/anomalies${q}`);
    } catch {
      return [];
    }
  },

  async getAnomaly(anomalyId: string): Promise<AnomalyEvent | null> {
    try {
      return await fetchJson<AnomalyEvent>(`${API_BASE}/anomalies/${anomalyId}`);
    } catch {
      return null;
    }
  },

  async updateAnomalyStatus(
    anomalyId: string,
    status: AnomalyStatus,
    resolutionNote?: string
  ): Promise<AnomalyEvent | null> {
    try {
      return await fetchJson<AnomalyEvent>(`${API_BASE}/anomalies/${anomalyId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status, resolution_note: resolutionNote }),
      });
    } catch {
      return null;
    }
  },

  async updateAnomaly(
    anomalyId: string,
    status: AnomalyStatus,
    resolutionNote?: string
  ): Promise<AnomalyEvent | null> {
    return this.updateAnomalyStatus(anomalyId, status, resolutionNote);
  },

  async submitFeedback(
    feedbackOrId: OperatorFeedback | string,
    label?: 'false_alarm' | 'confirmed_fault',
    note?: string
  ): Promise<{ status: string; message: string } | null> {
    try {
      const body =
        typeof feedbackOrId === 'string'
          ? { anomaly_id: feedbackOrId, label: label || 'false_alarm', note }
          : feedbackOrId;

      return await fetchJson<{ status: string; message: string }>(`${API_BASE}/anomalies/feedback`, {
        method: 'POST',
        body: JSON.stringify(body),
      });
    } catch {
      return null;
    }
  },

  // Simulator & Faults
  async injectFault(faultType: string, intensity = 1.0, durationSeconds = 30) {
    try {
      return await fetchJson(`${API_BASE}/simulator/inject`, {
        method: 'POST',
        body: JSON.stringify({
          fault_type: faultType,
          intensity,
          duration_seconds: durationSeconds,
        }),
      });
    } catch (e) {
      console.warn('Fault injection error:', e);
      return null;
    }
  },

  async resetSimulator() {
    try {
      return await fetchJson(`${API_BASE}/simulator/reset`, { method: 'POST' });
    } catch (e) {
      console.warn('Reset simulator error:', e);
      return null;
    }
  },

  async startPitchScript() {
    try {
      return await fetchJson(`${API_BASE}/simulator/pitch-script/start`, { method: 'POST' });
    } catch (e) {
      console.warn('Start pitch script error:', e);
      return null;
    }
  },

  async stopPitchScript() {
    try {
      return await fetchJson(`${API_BASE}/simulator/pitch-script/stop`, { method: 'POST' });
    } catch (e) {
      console.warn('Stop pitch script error:', e);
      return null;
    }
  },

  async getSimulatorStatus(): Promise<{ active_fault: string; pitch_script: PitchScriptStatus | null } | null> {
    try {
      return await fetchJson<{ active_fault: string; pitch_script: PitchScriptStatus | null }>(
        `${API_BASE}/simulator/status`
      );
    } catch {
      return null;
    }
  },

  // Maintenance & Imputation (Harsh)
  async getMaintenance(stationId = 'AGRA-01') {
    try {
      return await fetchJson(`${API_BASE}/maintenance?station_id=${stationId}`);
    } catch {
      return null;
    }
  },

  async acceptImputation(req: ImputationAcceptRequest) {
    return await fetchJson<{ status: string; record: unknown }>(`${API_BASE}/imputation/accept`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },
};
