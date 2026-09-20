'use client';

import React, { useState } from 'react';
import { AnomalyEvent } from '@/lib/types';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import { AlertTriangle, CheckCircle2, ThumbsDown, Crosshair, Clock, ShieldAlert } from 'lucide-react';

interface AnomalyCardProps {
  anomaly: AnomalyEvent;
}

export function AnomalyCard({ anomaly }: AnomalyCardProps) {
  const { updateAnomalyStatus, setSelectedSensor } = useTelemetryStore();
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  const isRule = anomaly.anomaly_type === 'rule_flag';
  const isCritical = anomaly.severity_score >= 0.75;

  const handleAcknowledge = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoadingAction('ack');
    await api.updateAnomaly(anomaly.anomaly_id, 'acknowledged');
    updateAnomalyStatus(anomaly.anomaly_id, 'acknowledged');
    setLoadingAction(null);
  };

  const handleResolve = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoadingAction('resolve');
    await api.updateAnomaly(anomaly.anomaly_id, 'resolved', 'Resolved by operator review.');
    updateAnomalyStatus(anomaly.anomaly_id, 'resolved', 'Resolved by operator review.');
    setLoadingAction(null);
  };

  const handleFalseAlarm = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoadingAction('feedback');
    await api.submitFeedback(anomaly.anomaly_id, 'false_alarm', 'Flagged as localized natural event by operator.');
    updateAnomalyStatus(anomaly.anomaly_id, 'false_alarm', 'Flagged as localized natural event.');
    setLoadingAction(null);
  };

  const handleFocus = () => {
    if (anomaly.culprit_sensors && anomaly.culprit_sensors.length > 0) {
      setSelectedSensor(anomaly.culprit_sensors[0]);
    }
  };

  // Format relative timestamp
  const dateObj = new Date(anomaly.detected_at);
  const timeStr = dateObj.toLocaleTimeString();

  return (
    <div
      onClick={handleFocus}
      className={`rounded-xl p-3.5 border transition-all cursor-pointer ${
        anomaly.status === 'open'
          ? isCritical
            ? 'bg-rose-950/30 border-rose-500/50 shadow-glow-rose/20 hover:border-rose-400'
            : 'bg-amber-950/20 border-amber-500/40 hover:border-amber-400'
          : 'bg-slate-900/40 border-white/5 opacity-70'
      }`}
    >
      {/* Header: Type and Severity */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5">
          {isRule ? (
            <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          )}
          <span className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wide">
            {isRule ? 'IMD Physics Rule' : '1D-CNN Anomaly'}
          </span>
          <span className="text-[10px] font-mono text-slate-500">
            #{anomaly.anomaly_id.slice(-6)}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full ${
              isCritical
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
            }`}
          >
            Severity: {(anomaly.severity_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Culprit Sensors & Diagnostic Snippet */}
      <div className="text-xs font-mono text-slate-300 mb-2.5">
        {anomaly.diagnostic_message}
      </div>

      <div className="flex flex-wrap items-center gap-1.5 mb-3">
        <span className="text-[10px] font-mono text-slate-400">Culprits:</span>
        {anomaly.culprit_sensors.map((c) => (
          <span
            key={c}
            className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-rose-500/20 text-rose-200 border border-rose-500/30 capitalize"
          >
            {c}
          </span>
        ))}
        <span className="text-[10px] font-mono text-slate-500 ml-auto flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {timeStr}
        </span>
      </div>

      {/* Action Buttons for Active Learning Loop */}
      {anomaly.status === 'open' ? (
        <div className="flex items-center gap-2 pt-2 border-t border-white/10">
          <button
            onClick={handleAcknowledge}
            disabled={loadingAction !== null}
            className="flex-1 py-1.5 px-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-[11px] font-mono text-slate-200 flex items-center justify-center gap-1 transition-all"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Acknowledge</span>
          </button>

          <button
            onClick={handleFalseAlarm}
            disabled={loadingAction !== null}
            title="Feeds back into DBSCAN clustering to adapt thresholds"
            className="flex-1 py-1.5 px-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-[11px] font-mono text-rose-300 flex items-center justify-center gap-1 transition-all"
          >
            <ThumbsDown className="w-3.5 h-3.5 text-rose-400" />
            <span>False Alarm</span>
          </button>

          <button
            onClick={handleResolve}
            disabled={loadingAction !== null}
            className="py-1.5 px-3 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-[11px] font-mono text-emerald-300 flex items-center justify-center transition-all"
          >
            Resolve
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between pt-2 border-t border-white/5 text-[11px] font-mono">
          <span className="text-slate-400">
            Status: <strong className="capitalize text-slate-300">{anomaly.status.replace('_', ' ')}</strong>
          </span>
          {anomaly.resolution_note && (
            <span className="text-slate-500 truncate max-w-[200px]" title={anomaly.resolution_note}>
              {anomaly.resolution_note}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
