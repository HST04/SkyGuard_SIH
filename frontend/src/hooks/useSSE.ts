'use client';

import { useEffect, useRef } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import { TelemetryPayload, AnomalyEvent } from '@/lib/types';

const STREAM_URL = process.env.NEXT_PUBLIC_STREAM_URL || 'http://localhost:8000/api/v1/telemetry/stream';

export function useSSE(stationId = 'AGRA-01') {
  const {
    setLatestTelemetry,
    setTelemetryHistory,
    addAnomaly,
    setConnectionStatus,
    setSimulatorState,
    markImputationAccepted,
  } = useTelemetryStore();

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const backoffDelayRef = useRef<number>(1000);

  useEffect(() => {
    let isMounted = true;

    // 1. Initial REST Hydration
    async function hydrate() {
      try {
        const [history, anomaliesList, simStatus] = await Promise.all([
          api.getTelemetryHistory(stationId, 60),
          api.getAnomalies('open', 10),
          api.getSimulatorStatus(),
        ]);

        if (!isMounted) return;

        if (history.length > 0) {
          setTelemetryHistory(history);
          setLatestTelemetry(history[history.length - 1]);
        }

        if (anomaliesList.length > 0) {
          anomaliesList.forEach((ano) => addAnomaly(ano));
        }

        if (simStatus) {
          setSimulatorState(simStatus.active_fault, simStatus.pitch_script);
        }
      } catch (err) {
        console.warn('[Hydration] Initial state load warning:', err);
      }
    }

    hydrate();

    // 2. Setup Real-time SSE Connection
    function connect() {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      setConnectionStatus('connecting');
      const es = new EventSource(`${STREAM_URL}?station_id=${stationId}`);
      eventSourceRef.current = es;

      es.onopen = () => {
        if (!isMounted) return;
        setConnectionStatus('connected');
        backoffDelayRef.current = 1000; // Reset backoff
      };

      // Listen for telemetry events
      es.addEventListener('telemetry', (event: MessageEvent) => {
        if (!isMounted) return;
        try {
          const payload: TelemetryPayload = JSON.parse(event.data);
          setLatestTelemetry(payload);
        } catch (e) {
          console.error('[SSE] Failed to parse telemetry event:', e);
        }
      });

      // Listen for anomaly events
      es.addEventListener('anomaly', (event: MessageEvent) => {
        if (!isMounted) return;
        try {
          const anomaly: AnomalyEvent = JSON.parse(event.data);
          addAnomaly(anomaly);
        } catch (e) {
          console.error('[SSE] Failed to parse anomaly event:', e);
        }
      });

      // Listen for imputation accepted broadcast
      es.addEventListener('imputation_accepted', () => {
        if (!isMounted) return;
        markImputationAccepted(true);
      });

      // Listen for heartbeats
      es.addEventListener('heartbeat', () => {
        if (!isMounted) return;
        setConnectionStatus('connected');
      });

      es.onerror = () => {
        if (!isMounted) return;
        setConnectionStatus('disconnected');
        es.close();

        // Exponential backoff reconnect (max 10s)
        const delay = Math.min(backoffDelayRef.current * 1.5, 10000);
        backoffDelayRef.current = delay;

        if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          if (isMounted) connect();
        }, delay);
      };
    }

    connect();

    // Poll simulator status periodically for pitch script sync
    const pollInterval = setInterval(async () => {
      if (!isMounted) return;
      const status = await api.getSimulatorStatus();
      if (status) {
        setSimulatorState(status.active_fault, status.pitch_script);
      }
    }, 2000);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [
    stationId,
    setLatestTelemetry,
    setTelemetryHistory,
    addAnomaly,
    setConnectionStatus,
    setSimulatorState,
    markImputationAccepted,
  ]);
}
