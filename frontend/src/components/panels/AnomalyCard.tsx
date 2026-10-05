'use client';

import React, { useState } from 'react';
import { AnomalyEvent } from '@/lib/types';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import {
  AlertTriangle,
  CheckCircle2,
  Check,
  EyeOff,
  ThumbsDown,
  Clock,
  ShieldAlert,
  FileText,
  Activity,
  Layers,
  ChevronDown,
  ChevronUp,
  Radio,
  Sparkles,
  ArrowRight
} from 'lucide-react';

interface AnomalyCardProps {
  anomaly: AnomalyEvent;
}

export function AnomalyCard({ anomaly }: AnomalyCardProps) {
  const { updateAnomalyStatus, setSelectedSensor } = useTelemetryStore();
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<'summary' | 'actual_readings'>('summary');

  const isRule = anomaly.anomaly_type === 'rule_flag';
  const severityNormalized = anomaly.severity_score > 1 ? anomaly.severity_score / 100.0 : anomaly.severity_score;
  const severityPct = Math.min(100, Math.max(0, Math.round(severityNormalized * 100)));
  const isCritical = severityNormalized >= 0.70;

  // Actions: Acknowledge, Resolve, Ignore
  const handleAcknowledge = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoadingAction('ack');
    try {
      await api.updateAnomaly(anomaly.anomaly_id, 'acknowledged', 'Acknowledged by operator console.');
      updateAnomalyStatus(anomaly.anomaly_id, 'acknowledged', 'Acknowledged by operator console.');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleResolve = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoadingAction('resolve');
    try {
      await api.updateAnomaly(anomaly.anomaly_id, 'resolved', 'Resolved by operator review.');
      updateAnomalyStatus(anomaly.anomaly_id, 'resolved', 'Resolved by operator review.');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleIgnore = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoadingAction('ignore');
    try {
      await api.updateAnomaly(anomaly.anomaly_id, 'ignored', 'Ignored by operator discretion.');
      updateAnomalyStatus(anomaly.anomaly_id, 'ignored', 'Ignored by operator discretion.');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleFalseAlarm = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoadingAction('feedback');
    try {
      await api.submitFeedback(anomaly.anomaly_id, 'false_alarm', 'Flagged as localized natural event by operator.');
      updateAnomalyStatus(anomaly.anomaly_id, 'false_alarm', 'Flagged as localized natural event.');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleFocus = () => {
    if (anomaly.culprit_sensors && anomaly.culprit_sensors.length > 0) {
      setSelectedSensor(anomaly.culprit_sensors[0]);
    }
  };

  // Format timestamp
  const dateObj = new Date(anomaly.detected_at);
  const timeStr = dateObj.toLocaleTimeString();

  // Extract transmitted data snapshot & decision reasoning
  const transmitted = anomaly.transmitted_data;
  const reasoning = anomaly.decision_reasoning;
  const readings = transmitted?.sensor_readings;
  const primaryCulprit = transmitted?.culprit_sensor || (anomaly.culprit_sensors?.[0] || 'sensor');
  const reportedVal = transmitted?.reported_value ?? (readings ? (primaryCulprit.includes('temp') ? readings.temperature_c : readings.humidity_pct) : undefined);
  const expectedVal = transmitted?.expected_baseline ?? (primaryCulprit.includes('temp') ? 25.0 : 42.6);
  const deviation = transmitted?.deviation_delta ?? (reportedVal !== undefined ? Math.round((reportedVal - expectedVal) * 10) / 10 : undefined);
  const unit = transmitted?.unit || (primaryCulprit.includes('temp') ? '°C' : '%');

  return (
    <div
      onClick={handleFocus}
      className={`rounded-xl p-3.5 border transition-all cursor-pointer ${
        anomaly.status === 'open'
          ? isCritical
            ? 'bg-rose-950/30 border-rose-500/50 shadow-glow-rose/20 hover:border-rose-400'
            : 'bg-amber-950/20 border-amber-500/40 hover:border-amber-400'
          : anomaly.status === 'resolved'
          ? 'bg-emerald-950/20 border-emerald-500/30 opacity-80'
          : anomaly.status === 'acknowledged'
          ? 'bg-sky-950/20 border-sky-500/30 opacity-80'
          : 'bg-slate-900/40 border-white/5 opacity-70'
      }`}
    >
      {/* Header: Type, Status, Severity, and Toggle */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          {isRule ? (
            <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          )}
          <span className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wide">
            {isRule ? 'IMD Physics Rule' : anomaly.classification || 'Sensor Defect'}
          </span>
          <span className="text-[10px] font-mono text-slate-500">
            #{anomaly.anomaly_id.slice(-6)}
          </span>
          {anomaly.status !== 'open' && (
            <span
              className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded uppercase ${
                anomaly.status === 'resolved'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : anomaly.status === 'acknowledged'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                  : 'bg-slate-500/20 text-slate-300 border border-slate-500/30'
              }`}
            >
              LOGGED ({anomaly.status})
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <span
            className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full ${
              anomaly.status !== 'open'
                ? 'bg-slate-800 text-slate-400 border border-white/5'
                : isCritical
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
            }`}
          >
            Confidence: {severityPct}%
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="p-1 text-slate-400 hover:text-white rounded"
            title={isExpanded ? 'Collapse card' : 'Expand card'}
          >
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Culprit Sensors Strip */}
      <div className="flex flex-wrap items-center gap-1.5 mb-2.5">
        <span className="text-[10px] font-mono text-slate-400">Target Sensor:</span>
        {anomaly.culprit_sensors.map((c) => (
          <span
            key={c}
            className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-rose-500/20 text-rose-200 border border-rose-500/30 capitalize"
          >
            {c}
          </span>
        ))}
        {reportedVal !== undefined && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black/40 text-amber-300 border border-amber-500/30 font-semibold">
            Reported: {reportedVal}{unit}
          </span>
        )}
        <span className="text-[10px] font-mono text-slate-500 ml-auto flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {timeStr}
        </span>
      </div>

      {/* Requirement 1: Option to toggle between Summary and Actual Readings of Why Decision Taken */}
      <div className="flex items-center gap-1 mb-2.5 bg-black/40 p-1 rounded-lg border border-white/10">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setViewMode('summary');
            setIsExpanded(true);
          }}
          className={`flex-1 py-1 px-2 rounded text-[10px] font-mono font-medium flex items-center justify-center gap-1.5 transition-all ${
            viewMode === 'summary'
              ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/40 shadow-glow-cyan/20'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-3 h-3" />
          <span>Summarize Content</span>
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            setViewMode('actual_readings');
            setIsExpanded(true);
          }}
          className={`flex-1 py-1 px-2 rounded text-[10px] font-mono font-medium flex items-center justify-center gap-1.5 transition-all ${
            viewMode === 'actual_readings'
              ? 'bg-purple-500/20 text-purple-200 border border-purple-500/40 shadow-glow-indigo/20'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Activity className="w-3 h-3" />
          <span>Actual Readings & Why</span>
        </button>
      </div>

      {/* Expanded Content Section */}
      {isExpanded && (
        <div className="space-y-2 mb-3 animate-in fade-in duration-150">
          {viewMode === 'summary' ? (
            /* Tab 1: Executive Content Summary */
            <div className="p-2.5 rounded-lg bg-black/30 border border-white/5 space-y-2">
              <div className="text-[10px] font-mono uppercase font-bold text-cyan-400 flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-cyan-400" />
                <span>Defect Decision Summary</span>
              </div>
              <p className="text-xs font-sans text-slate-200 leading-relaxed">
                {reasoning?.summary || anomaly.summary || anomaly.diagnostic_message}
              </p>
              {reasoning?.scientific_rationale && (
                <div className="text-[11px] font-sans text-slate-300/90 pt-1 border-t border-white/5 leading-relaxed">
                  <strong className="text-slate-400 font-mono text-[10px]">Arbiter Rationale: </strong>
                  {reasoning.scientific_rationale}
                </div>
              )}
              {anomaly.confluence?.action_recommended && (
                <div className="text-[10px] font-mono text-cyan-300 pt-1 flex items-center gap-1">
                  <ArrowRight className="w-3 h-3 text-cyan-400 shrink-0" />
                  <span>Action: {anomaly.confluence.action_recommended}</span>
                </div>
              )}
            </div>
          ) : (
            /* Tab 2: Actual Readings Transmitted & Why Decision Taken */
            <div className="space-y-2">
              {/* Actual Transmitted Readings Grid */}
              <div className="p-2.5 rounded-lg bg-black/40 border border-purple-500/20 space-y-1.5">
                <div className="text-[10px] font-mono uppercase font-bold text-purple-300 flex items-center justify-between">
                  <span className="flex items-center gap-1">
                    <Radio className="w-3 h-3 text-purple-400" />
                    <span>Actual Telemetry Transmitted</span>
                  </span>
                  {transmitted?.sequence && (
                    <span className="text-[9px] text-slate-500">Seq #{transmitted.sequence}</span>
                  )}
                </div>

                {readings ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-[11px] font-mono pt-1">
                    <div className="p-1.5 rounded bg-white/5 border border-white/5">
                      <span className="text-[9px] text-slate-400 block">Temperature:</span>
                      <span className="text-slate-200 font-bold">{readings.temperature_c}°C</span>
                    </div>
                    <div className={`p-1.5 rounded border ${
                      primaryCulprit.includes('humid')
                        ? 'bg-rose-500/20 border-rose-500/40 text-rose-200'
                        : 'bg-white/5 border-white/5 text-slate-200'
                    }`}>
                      <span className="text-[9px] text-slate-400 block">Humidity (RH):</span>
                      <span className="font-bold">{readings.humidity_pct}%</span>
                      {primaryCulprit.includes('humid') && deviation !== undefined && (
                        <span className="text-[9px] block text-rose-300 font-sans">
                          (Exp: {expectedVal}%, Δ{deviation > 0 ? `+${deviation}` : deviation}%)
                        </span>
                      )}
                    </div>
                    <div className="p-1.5 rounded bg-white/5 border border-white/5">
                      <span className="text-[9px] text-slate-400 block">Pressure:</span>
                      <span className="text-slate-200 font-bold">{readings.pressure_hpa} hPa</span>
                    </div>
                    <div className="p-1.5 rounded bg-white/5 border border-white/5">
                      <span className="text-[9px] text-slate-400 block">Dew Point:</span>
                      <span className="text-slate-200 font-bold">{readings.dew_point_c}°C</span>
                    </div>
                    <div className="p-1.5 rounded bg-white/5 border border-white/5">
                      <span className="text-[9px] text-slate-400 block">Wind Speed:</span>
                      <span className="text-slate-200 font-bold">{readings.wind_speed_ms} m/s</span>
                    </div>
                    <div className="p-1.5 rounded bg-white/5 border border-white/5">
                      <span className="text-[9px] text-slate-400 block">Solar Radiation:</span>
                      <span className="text-slate-200 font-bold">{readings.solar_radiation_wm2} W/m²</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-[11px] font-mono text-slate-400 italic py-1">
                    Telemetry snapshot captured on packet #{anomaly.anomaly_id.slice(-6)}
                  </div>
                )}
              </div>

              {/* Why It Took That Decision */}
              <div className="p-2.5 rounded-lg bg-black/40 border border-white/10 space-y-1.5 text-xs">
                <div className="text-[10px] font-mono uppercase font-bold text-amber-300 flex items-center gap-1">
                  <Layers className="w-3 h-3 text-amber-400" />
                  <span>Why Decision Was Taken</span>
                </div>
                <p className="text-[11px] font-sans text-slate-200 leading-relaxed">
                  {reasoning?.why_decision || reasoning?.physics_inconsistency || anomaly.diagnostic_message}
                </p>

                {/* Score breakdown chips */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1.5 border-t border-white/5 text-[9px] font-mono">
                  {reasoning?.gatekeeper_outlier_prob !== undefined && (
                    <span className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                      CNN Outlier: {(reasoning.gatekeeper_outlier_prob * 100).toFixed(1)}%
                    </span>
                  )}
                  {reasoning?.p_sensor !== undefined && (
                    <span className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                      Model B Defect P: {(reasoning.p_sensor * 100).toFixed(1)}%
                    </span>
                  )}
                  {reasoning?.p_weather !== undefined && (
                    <span className="px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-300 border border-sky-500/20">
                      Model A Weather P: {(reasoning.p_weather * 100).toFixed(1)}%
                    </span>
                  )}
                  {anomaly.reconstruction_error > 0 && (
                    <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                      Reconstruction MSE: {anomaly.reconstruction_error.toFixed(4)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Requirement 2: Three buttons: Acknowledge, Resolve, Ignore */}
      {anomaly.status === 'open' ? (
        <div className="flex items-center gap-2 pt-2 border-t border-white/10 flex-wrap sm:flex-nowrap">
          {/* Button 1: Acknowledge */}
          <button
            onClick={handleAcknowledge}
            disabled={loadingAction !== null}
            title="Acknowledge sensor defect and log operator review"
            className="flex-1 py-1.5 px-2 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-[11px] font-mono text-sky-300 flex items-center justify-center gap-1 transition-all active:scale-95"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />
            <span>{loadingAction === 'ack' ? 'Logging...' : 'Acknowledge'}</span>
          </button>

          {/* Button 2: Resolve */}
          <button
            onClick={handleResolve}
            disabled={loadingAction !== null}
            title="Resolve defect, log incident, and return system state to Nominal"
            className="flex-1 py-1.5 px-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-[11px] font-mono text-emerald-300 flex items-center justify-center gap-1 transition-all active:scale-95 font-semibold"
          >
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span>{loadingAction === 'resolve' ? 'Resolving...' : 'Resolve'}</span>
          </button>

          {/* Button 3: Ignore */}
          <button
            onClick={handleIgnore}
            disabled={loadingAction !== null}
            title="Ignore transient defect, log as ignored, and assume all sensors OK"
            className="flex-1 py-1.5 px-2 rounded-lg bg-slate-800 hover:bg-slate-700/80 border border-white/10 text-[11px] font-mono text-slate-300 flex items-center justify-center gap-1 transition-all active:scale-95"
          >
            <EyeOff className="w-3.5 h-3.5 text-slate-400" />
            <span>{loadingAction === 'ignore' ? 'Logging...' : 'Ignore'}</span>
          </button>

          {/* False Alarm Feedback Button */}
          <button
            onClick={handleFalseAlarm}
            disabled={loadingAction !== null}
            title="Flag as false alarm to retrain model thresholds"
            className="py-1.5 px-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-[11px] font-mono text-rose-400 flex items-center justify-center transition-all"
          >
            <ThumbsDown className="w-3 h-3" />
          </button>
        </div>
      ) : (
        /* Logged State Bar */
        <div className="flex items-center justify-between pt-2 border-t border-white/5 text-[11px] font-mono">
          <div className="flex items-center gap-1.5 text-slate-400">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>
              Status: <strong className="capitalize text-slate-200">{anomaly.status}</strong>
            </span>
          </div>
          {anomaly.resolution_note && (
            <span className="text-slate-500 text-[10px] truncate max-w-[220px]" title={anomaly.resolution_note}>
              {anomaly.resolution_note}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
