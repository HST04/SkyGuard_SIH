'use client';

import React from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { ShieldCheck, AlertTriangle, CloudLightning, Activity, HelpCircle, ArrowRight } from 'lucide-react';

export function ConfluenceAlertBanner() {
  const { confluence, stationStatus, activeAnomaly, activeFault } = useTelemetryStore();

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
      statusLabel: 'STATION NOMINAL',
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
  const confidencePct = Math.round(conf.confidence * 1000) / 10;
  const pWeatherPct = Math.round(conf.p_weather * 100);
  const pDefectPct = Math.round(conf.p_defect * 100);

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
              Confluence Decision Engine (PRD Layer 2.3)
            </span>
          </div>
        </div>

        {/* Confidence Badge */}
        <div className="flex items-center gap-1.5 bg-black/40 px-3 py-1.5 rounded-xl border border-white/10 font-mono">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Confidence:</span>
          <span className="text-sm font-bold text-white tracking-tight">{confidencePct}%</span>
        </div>
      </div>

      {/* Decision Summary Text */}
      <div className="text-xs font-mono text-slate-300 mb-3 bg-black/20 p-2.5 rounded-xl border border-white/5">
        <div className="text-[10px] text-slate-400 uppercase font-semibold mb-0.5">Physical Analysis:</div>
        <div>{conf.summary}</div>
      </div>

      {/* Model A vs Model B Dual Probability Gauges */}
      <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white/10">
        {/* Model A Gauge: P(Weather) */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 flex items-center gap-1">
              <CloudLightning className="w-3.5 h-3.5 text-sky-400" />
              <span>Model A: P(Weather)</span>
            </span>
            <span className={`font-bold ${isNatural ? 'text-emerald-400' : 'text-slate-300'}`}>
              {pWeatherPct}%
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-white/5">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                isNatural
                  ? 'bg-gradient-to-r from-teal-500 to-emerald-400 shadow-glow-emerald'
                  : 'bg-sky-500/60'
              }`}
              style={{ width: `${Math.max(4, pWeatherPct)}%` }}
            />
          </div>
          <div className="text-[9px] font-mono text-slate-500 flex justify-between">
            <span>Squall threshold: 70%</span>
            <span>{isNatural ? 'Met' : 'Unmet'}</span>
          </div>
        </div>

        {/* Model B Gauge: P(Defect) */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span>Model B: P(Defect)</span>
            </span>
            <span className={`font-bold ${isDefect ? 'text-rose-400' : 'text-slate-300'}`}>
              {pDefectPct}%
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-white/5">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                isDefect
                  ? 'bg-gradient-to-r from-amber-500 to-rose-500 shadow-glow-rose'
                  : 'bg-rose-500/40'
              }`}
              style={{ width: `${Math.max(4, pDefectPct)}%` }}
            />
          </div>
          <div className="text-[9px] font-mono text-slate-500 flex justify-between">
            <span>Defect threshold: 70%</span>
            <span>{isDefect ? 'Tripped' : 'Clear'}</span>
          </div>
        </div>
      </div>

      {/* Recommendation Footer */}
      {conf.action_recommended && (
        <div className="mt-3 pt-2 border-t border-white/5 flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
          <ArrowRight className="w-3 h-3 text-cyan-400 flex-shrink-0" />
          <span><strong className="text-slate-300">Action:</strong> {conf.action_recommended}</span>
        </div>
      )}
    </div>
  );
}
