'use client';

import React, { useState } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import {
  ShieldCheck,
  AlertTriangle,
  CloudLightning,
  Activity,
  HelpCircle,
  ArrowRight,
  CheckCircle2,
  Check,
  EyeOff,
  FileText,
  Radio,
  Layers,
  Sparkles
} from 'lucide-react';

export function ConfluenceAlertBanner() {
  const {
    confluence,
    stationStatus,
    activeAnomaly,
    activeFault,
    anomalies,
    latestTelemetry,
    updateAnomalyStatus,
    bulkActionAnomalies,
  } = useTelemetryStore();

  const [bannerViewMode, setBannerViewMode] = useState<'summary' | 'actual_readings'>('summary');
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  // If no confluence yet, establish nominal fallback
  const conf = confluence || {
    classification: 'Nominal Baseline',
    confidence: 0.99,
    p_weather: 0.04,
    p_defect: 0.03,
    defect_class: 'none',
    summary: 'Atmospheric parameters within nominal IMD physical boundaries.',
    action_recommended: 'Continuous 1 Hz nominal monitoring.',
  };

  const isNatural = conf.classification === 'Natural Weather Event';
  const isDefect = conf.classification === 'Sensor Defect';
  const isCompound = conf.classification === 'Compound Event';
  const isNominal = conf.classification === 'Nominal Baseline';

  // Find target anomaly if open
  const openAnomaly = activeAnomaly?.status === 'open' ? activeAnomaly : anomalies.find((a) => a.status === 'open');

  const handleAction = async (action: 'acknowledged' | 'resolved' | 'ignored') => {
    setLoadingAction(action);
    try {
      if (openAnomaly) {
        await api.updateAnomaly(openAnomaly.anomaly_id, action, `${action.toUpperCase()} from Confluence Alert Banner`);
        updateAnomalyStatus(openAnomaly.anomaly_id, action, `${action.toUpperCase()} from Confluence Alert Banner`);
      } else {
        await api.bulkActionAnomalies('AGRA-01', action, `Bulk ${action} from Confluence Banner`);
        bulkActionAnomalies(action, `Bulk ${action} from Confluence Banner`);
      }
    } catch (err) {
      console.error(`Failed to execute ${action}:`, err);
    } finally {
      setLoadingAction(null);
    }
  };

  // Badge colors and icons based on PRD Section 5.5
  const badgeConfig = {
    'Natural Weather Event': {
      bg: 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300 shadow-glow-emerald',
      pill: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
      icon: CloudLightning,
      statusLabel: 'NATURAL STORM (ZERO FALSE ALARM)',
      accentColor: '#10b981',
    },
    'Sensor Defect': {
      bg: 'bg-rose-950/40 border-rose-500/60 text-rose-200 shadow-glow-rose',
      pill: 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse',
      icon: AlertTriangle,
      statusLabel: 'HARDWARE DEFECT CONFIRMED',
      accentColor: '#f43f5e',
    },
    'Compound Event': {
      bg: 'bg-amber-950/40 border-amber-500/50 text-amber-200 shadow-glow-amber',
      pill: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      icon: Activity,
      statusLabel: 'COMPOUND ANOMALY DETECTED',
      accentColor: '#f59e0b',
    },
    'Uncertain Anomaly': {
      bg: 'bg-indigo-950/40 border-indigo-500/50 text-indigo-200',
      pill: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
      icon: HelpCircle,
      statusLabel: 'TRIAGE REQUIRED',
      accentColor: '#6366f1',
    },
    'Nominal Baseline': {
      bg: 'glass-panel border-white/10 text-slate-200',
      pill: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      icon: ShieldCheck,
      statusLabel: 'STATION HEALTHY',
      accentColor: '#06b6d4',
    },
  }[conf.classification] || {
    bg: 'glass-panel border-white/10 text-slate-200',
    pill: 'bg-white/10 text-slate-300 border-white/20',
    icon: ShieldCheck,
    statusLabel: 'MONITORING',
    accentColor: '#94a3b8',
  };

  const Icon = badgeConfig.icon;
  const rawConfidence = (conf as any).confidence_score !== undefined
    ? (conf as any).confidence_score
    : (conf.confidence !== undefined ? (conf.confidence <= 1.0 ? conf.confidence * 100 : conf.confidence) : 98.5);
  const confidencePct = Math.min(100, Math.max(0, Math.round(Number(rawConfidence) * 10) / 10));
  const pWeatherPct = Math.round((conf.p_weather ?? 0.04) * 100);
  const pDefectPct = Math.round((conf.p_defect ?? 0.03) * 100);

  // Extracted telemetry for Actual Readings display
  const transmitted = openAnomaly?.transmitted_data;
  const reasoning = openAnomaly?.decision_reasoning;
  const telSource = transmitted?.sensor_readings || latestTelemetry;

  return (
    <div className={`rounded-2xl p-4 border transition-all duration-300 ${badgeConfig.bg}`}>
      {/* Top Banner Row: Classification Pill + Confidence */}
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-white/5 border border-white/10">
            <Icon className="w-5 h-5" style={{ color: badgeConfig.accentColor }} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-white">
                {conf.classification}
              </span>
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${badgeConfig.pill}`}>
                {badgeConfig.statusLabel}
              </span>
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              Atmospheric Arbiter • Physics & AI Confluence Validation
            </span>
          </div>
        </div>

        {/* Confidence & API Fallback Indicators */}
        <div className="flex items-center gap-2">
          {Boolean(conf.api_fallback) && (
            <div className="flex items-center gap-1 bg-amber-500/20 px-2.5 py-1 rounded-xl border border-amber-500/40 text-[10px] font-mono font-bold text-amber-300 animate-pulse">
              <AlertTriangle className="w-3 h-3 text-amber-400" />
              <span>LLM API Offline (Physics Fallback)</span>
            </div>
          )}
          <div className="flex items-center gap-1.5 bg-black/40 px-3 py-1.5 rounded-xl border border-white/10 font-mono">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider">Confidence:</span>
            <span className="text-sm font-bold text-white tracking-tight">{confidencePct}%</span>
          </div>
        </div>
      </div>

      {/* Requirement 1: Toggle between Content Summary and Actual Readings & Why */}
      <div className="flex items-center gap-1 mb-2.5 bg-black/40 p-1 rounded-xl border border-white/10">
        <button
          onClick={() => setBannerViewMode('summary')}
          className={`flex-1 py-1 px-2.5 rounded-lg text-[10px] font-mono font-semibold flex items-center justify-center gap-1.5 transition-all ${
            bannerViewMode === 'summary'
              ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/40 shadow-glow-cyan/20'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-3 h-3" />
          <span>Summarize Content</span>
        </button>

        <button
          onClick={() => setBannerViewMode('actual_readings')}
          className={`flex-1 py-1 px-2.5 rounded-lg text-[10px] font-mono font-semibold flex items-center justify-center gap-1.5 transition-all ${
            bannerViewMode === 'actual_readings'
              ? 'bg-purple-500/20 text-purple-200 border border-purple-500/40 shadow-glow-indigo/20'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Radio className="w-3 h-3" />
          <span>Actual Readings & Why Decision Taken</span>
        </button>
      </div>

      {/* Main Content Area: Summary vs Actual Readings */}
      <div className="text-xs font-mono text-slate-300 mb-3 bg-black/30 p-3 rounded-xl border border-white/5 space-y-3">
        {bannerViewMode === 'summary' ? (
          <div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold tracking-wider mb-1 flex items-center justify-between">
              <span className="flex items-center gap-1 text-cyan-400">
                <Sparkles className="w-3 h-3" />
                <span>Synthesis Reasoning & Summary</span>
              </span>
              <span className="text-slate-500 font-normal">Layer 3 Confluence Engine</span>
            </div>
            <div className="text-slate-200 text-xs leading-relaxed font-sans">
              {reasoning?.summary || conf.summary || conf.action_recommended || 'Atmospheric parameters within nominal IMD physical boundaries.'}
            </div>
          </div>
        ) : (
          <div className="space-y-2.5">
            {/* Actual Sensor Readings Grid */}
            <div className="space-y-1.5">
              <div className="text-[10px] text-purple-300 uppercase font-bold tracking-wider flex items-center justify-between">
                <span className="flex items-center gap-1">
                  <Radio className="w-3 h-3 text-purple-400" />
                  <span>Actual Transmitted Telemetry at Incident Moment</span>
                </span>
                {latestTelemetry?.sequence && (
                  <span className="text-[9px] text-slate-500">Packet #{latestTelemetry.sequence}</span>
                )}
              </div>

              {telSource && (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-[11px] font-mono">
                  <div className="p-1.5 rounded bg-white/5 border border-white/5">
                    <span className="text-[9px] text-slate-400 block">Temperature:</span>
                    <span className="text-slate-200 font-bold">{telSource.temperature_c}°C</span>
                  </div>
                  <div className={`p-1.5 rounded border ${
                    isDefect ? 'bg-rose-500/20 border-rose-500/40 text-rose-200' : 'bg-white/5 border-white/5 text-slate-200'
                  }`}>
                    <span className="text-[9px] text-slate-400 block">Humidity (RH):</span>
                    <span className="font-bold">{telSource.humidity_pct}%</span>
                    {isDefect && (
                      <span className="text-[9px] block text-rose-300 font-sans">
                        (Baseline: 42.6%, Δ+{(telSource.humidity_pct - 42.6).toFixed(1)}%)
                      </span>
                    )}
                  </div>
                  <div className="p-1.5 rounded bg-white/5 border border-white/5">
                    <span className="text-[9px] text-slate-400 block">Pressure:</span>
                    <span className="text-slate-200 font-bold">{telSource.pressure_hpa} hPa</span>
                  </div>
                  <div className="p-1.5 rounded bg-white/5 border border-white/5">
                    <span className="text-[9px] text-slate-400 block">Dew Point:</span>
                    <span className="text-slate-200 font-bold">{telSource.dew_point_c}°C</span>
                  </div>
                  <div className="p-1.5 rounded bg-white/5 border border-white/5">
                    <span className="text-[9px] text-slate-400 block">Wind Speed:</span>
                    <span className="text-slate-200 font-bold">{telSource.wind_speed_ms} m/s</span>
                  </div>
                  <div className="p-1.5 rounded bg-white/5 border border-white/5">
                    <span className="text-[9px] text-slate-400 block">Solar Radiation:</span>
                    <span className="text-slate-200 font-bold">{telSource.solar_radiation_wm2} W/m²</span>
                  </div>
                </div>
              )}
            </div>

            {/* Why Decision Was Taken */}
            <div className="p-2 rounded-lg bg-black/40 border border-white/10 space-y-1">
              <span className="text-[10px] uppercase font-bold text-amber-300 flex items-center gap-1">
                <Layers className="w-3 h-3 text-amber-400" />
                <span>Physical Inconsistency & Decision Trigger</span>
              </span>
              <p className="text-[11px] font-sans text-slate-200 leading-relaxed">
                {reasoning?.why_decision || reasoning?.physics_inconsistency || conf.summary}
              </p>
            </div>
          </div>
        )}

        {/* AI Multi-Agent Debate Dialogue Stream */}
        <div className="pt-2.5 border-t border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider font-semibold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              <span>Dual-Agent Neuro-Symbolic Deliberation</span>
            </div>
            <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-white/10">
              {conf.agent_dialogue && conf.agent_dialogue.length > 1
                ? `${conf.agent_dialogue.length} Turns • Consensus`
                : isNominal
                ? 'Standby • Gatekeeper Active'
                : '1 Turn • Fast Resolution'}
            </span>
          </div>

          <div className="space-y-2 max-h-48 overflow-y-auto pr-1 scrollbar-thin">
            {conf.agent_dialogue && conf.agent_dialogue.length > 0 ? (
              conf.agent_dialogue.map((turn, i) => {
                const isModelA = turn.role === 'model_a';
                const isModelB = turn.role === 'model_b';

                return (
                  <div
                    key={i}
                    className={`rounded-xl p-2.5 border transition-all ${
                      isModelA
                        ? 'bg-sky-950/30 border-sky-500/40 text-sky-100'
                        : isModelB
                        ? 'bg-rose-950/30 border-rose-500/40 text-rose-100'
                        : 'bg-purple-950/30 border-purple-500/40 text-purple-100'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1 pb-1 border-b border-white/5">
                      <span className="font-mono font-bold text-[10px] uppercase tracking-wider">
                        {turn.sender}
                      </span>
                      <span className="text-[9px] font-mono text-slate-400">Turn #{i + 1}</span>
                    </div>
                    <p className="text-[11px] leading-relaxed font-sans text-slate-200">
                      {turn.message}
                    </p>
                  </div>
                );
              })
            ) : (
              <div className="p-2.5 rounded-xl bg-slate-900/40 border border-white/5 text-center space-y-1">
                <span className="text-[11px] font-mono text-slate-300 font-medium">Gatekeeper Active</span>
                <p className="text-[10px] text-slate-500 font-mono">
                  Telemetry parameters nominal. Debate arena activates upon anomaly detection.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Model A vs Model B Dual Probability Gauges */}
      <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white/10">
        {/* Model A Gauge */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 flex items-center gap-1">
              <CloudLightning className="w-3.5 h-3.5 text-sky-400" />
              <span>Severe Weather Probability</span>
            </span>
            <span className={`font-bold ${isNatural ? 'text-emerald-400' : 'text-slate-300'}`}>
              {pWeatherPct}%
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-white/5">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                isNatural ? 'bg-gradient-to-r from-teal-500 to-emerald-400 shadow-glow-emerald' : 'bg-sky-500/60'
              }`}
              style={{ width: `${Math.max(4, pWeatherPct)}%` }}
            />
          </div>
        </div>

        {/* Model B Gauge */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span>Sensor Fault Probability</span>
            </span>
            <span className={`font-bold ${isDefect ? 'text-rose-400' : 'text-slate-300'}`}>
              {pDefectPct}%
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-white/5">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                isDefect ? 'bg-gradient-to-r from-amber-500 to-rose-500 shadow-glow-rose' : 'bg-rose-500/40'
              }`}
              style={{ width: `${Math.max(4, pDefectPct)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Requirement 2: Three buttons (Acknowledge, Resolve, Ignore) when defect is diagnosed */}
      {isDefect && (
        <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between gap-2 flex-wrap">
          <span className="text-[11px] font-mono text-slate-300 font-semibold flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
            <span>Operator Decision Action:</span>
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleAction('acknowledged')}
              disabled={loadingAction !== null}
              className="py-1.5 px-3 rounded-xl bg-sky-500/20 hover:bg-sky-500/30 text-sky-200 border border-sky-500/40 text-xs font-mono flex items-center gap-1.5 transition-all active:scale-95"
              title="Acknowledge defect and log into audit trail"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />
              <span>{loadingAction === 'acknowledged' ? 'Logging...' : 'Acknowledge'}</span>
            </button>

            <button
              onClick={() => handleAction('resolved')}
              disabled={loadingAction !== null}
              className="py-1.5 px-3 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-200 border border-emerald-500/40 text-xs font-mono flex items-center gap-1.5 transition-all active:scale-95 font-semibold"
              title="Resolve sensor defect and restore nominal healthy station state"
            >
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>{loadingAction === 'resolved' ? 'Resolving...' : 'Resolve'}</span>
            </button>

            <button
              onClick={() => handleAction('ignored')}
              disabled={loadingAction !== null}
              className="py-1.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 text-xs font-mono flex items-center gap-1.5 transition-all active:scale-95"
              title="Ignore transient defect and assume all sensors OK"
            >
              <EyeOff className="w-3.5 h-3.5 text-slate-400" />
              <span>{loadingAction === 'ignored' ? 'Logging...' : 'Ignore'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Recommendation Footer if Nominal */}
      {!isDefect && conf.action_recommended && (
        <div className="mt-3 pt-2 border-t border-white/5 flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
          <ArrowRight className="w-3 h-3 text-cyan-400 flex-shrink-0" />
          <span><strong className="text-slate-300">Action:</strong> {conf.action_recommended}</span>
        </div>
      )}
    </div>
  );
}
