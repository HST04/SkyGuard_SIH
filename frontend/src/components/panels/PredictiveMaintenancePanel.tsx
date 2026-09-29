'use client';

import React from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { Wrench, AlertTriangle, ShieldCheck, Clock, Gauge, TrendingUp, Info } from 'lucide-react';

export function PredictiveMaintenancePanel() {
  const { maintenance, activeFault } = useTelemetryStore();

  const hum = maintenance?.humidity || {
    status: activeFault === 'humidity_drift' ? 'At Risk' : 'Healthy',
    drift_sigma: activeFault === 'humidity_drift' ? 2.45 : 0.42,
    progress: activeFault === 'humidity_drift' ? 82 : 14,
    days_to_recalibration: activeFault === 'humidity_drift' ? 12 : 48,
    trend: activeFault === 'humidity_drift' ? '+0.65%/day (Capacitive bias)' : 'Stable (< 0.1%/day)',
    warmup: 'Calibrated (10-min baseline locked)',
  };

  const isAtRisk = hum.status === 'At Risk' || hum.status === 'Recalibrate Now';
  const isWatch = hum.status === 'Watch';

  const sigmaVal = hum.drift_sigma !== null && hum.drift_sigma !== undefined ? hum.drift_sigma.toFixed(2) : '--';
  const daysVal = hum.days_to_recalibration !== null && hum.days_to_recalibration !== undefined
    ? `${hum.days_to_recalibration} Days`
    : 'Unknown';

  return (
    <div
      className={`glass-panel rounded-2xl p-4 border transition-all duration-300 ${
        isAtRisk
          ? 'border-rose-500/40 bg-rose-950/20 shadow-glow-rose/20'
          : isWatch
          ? 'border-amber-500/40 bg-amber-950/20 shadow-glow-amber/20'
          : 'border-white/10 shadow-glass'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Wrench className={`w-4 h-4 ${isAtRisk ? 'text-rose-400 animate-bounce' : 'text-cyan-400'}`} />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Predictive Maintenance Engine (Layer 3.4)
          </h3>
        </div>

        {/* Status Pill */}
        <span
          className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full border flex items-center gap-1.5 ${
            isAtRisk
              ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse'
              : isWatch
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
              : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
          }`}
        >
          {isAtRisk ? (
            <AlertTriangle className="w-3 h-3 text-rose-400" />
          ) : (
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
          )}
          {hum.status.toUpperCase()}
        </span>
      </div>

      {/* Key Metric Tiles */}
      <div className="grid grid-cols-2 gap-2.5 mb-3">
        {/* Metric 1: Drift Sigma */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 flex flex-col justify-between">
          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Gauge className="w-3 h-3 text-cyan-400" />
            Cumulative Drift (EWMA)
          </div>
          <div className="flex items-baseline gap-1.5 mt-1">
            <span
              className={`text-2xl font-mono font-bold tracking-tight ${
                isAtRisk ? 'text-rose-400' : isWatch ? 'text-amber-400' : 'text-emerald-400'
              }`}
            >
              {sigmaVal}σ
            </span>
            <span className="text-[10px] font-mono text-slate-500">/ 2.0σ limit</span>
          </div>
          <div className="text-[10px] font-mono text-slate-400 mt-1">
            λ = 0.20 smoothing factor
          </div>
        </div>

        {/* Metric 2: Calibration Horizon */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 flex flex-col justify-between">
          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Clock className="w-3 h-3 text-amber-400" />
            Calibration Horizon
          </div>
          <div className="flex items-baseline gap-1.5 mt-1">
            <span
              className={`text-2xl font-mono font-bold tracking-tight ${
                isAtRisk ? 'text-rose-400' : 'text-cyan-300'
              }`}
            >
              {daysVal}
            </span>
          </div>
          <div className="text-[10px] font-mono text-slate-400 mt-1">
            {isAtRisk ? 'Calibration due in < 2 Weeks' : 'Nominal degradation curve'}
          </div>
        </div>
      </div>

      {/* Drift Meter Progress Bar */}
      <div className="p-3 rounded-xl bg-slate-900/40 border border-white/5 mb-3 space-y-2">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-slate-300 flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
            <span>Humidity Capacitive Drift:</span>
          </span>
          <span className="text-[11px] text-slate-400 font-mono">{hum.trend}</span>
        </div>

        <div className="relative w-full h-3 rounded-full bg-slate-950 overflow-hidden border border-white/10">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              isAtRisk
                ? 'bg-gradient-to-r from-amber-500 via-rose-500 to-rose-600 shadow-glow-rose'
                : isWatch
                ? 'bg-gradient-to-r from-teal-500 to-amber-400'
                : 'bg-gradient-to-r from-cyan-500 to-emerald-400'
            }`}
            style={{ width: `${Math.min(100, Math.max(5, hum.progress || 10))}%` }}
          />
          {/* 2.0 Sigma Reference Marker (at 66% width) */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-rose-400/80 z-10"
            style={{ left: '66.6%' }}
            title="2.0σ Warning Threshold"
          />
        </div>

        <div className="flex items-center justify-between text-[9px] font-mono text-slate-500">
          <span>0.0σ Baseline</span>
          <span className="text-rose-400 font-semibold">2.0σ Threshold (Warning)</span>
          <span>3.0σ Failure</span>
        </div>
      </div>

      {/* Sensor Channels Maintenance Table */}
      <div className="space-y-1.5 font-mono text-xs">
        <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-semibold">
          Sensor Channel Drift Horizons
        </div>

        {/* Humidity Sensor */}
        <div className="p-2 rounded-lg bg-black/20 border border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span className="text-slate-200 font-semibold">Humidity (RH-84)</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] text-slate-400">{sigmaVal}σ residual</span>
            <span
              className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                isAtRisk
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
              }`}
            >
              {hum.status}
            </span>
          </div>
        </div>

        {/* Temperature Sensor */}
        <div className="p-2 rounded-lg bg-black/20 border border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-500" />
            <span className="text-slate-400">Temperature (PT-100)</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] text-slate-500">0.08σ residual</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-400 border border-white/10">
              Healthy
            </span>
          </div>
        </div>

        {/* Pressure Sensor */}
        <div className="p-2 rounded-lg bg-black/20 border border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-500" />
            <span className="text-slate-400">Barometer (P-1010)</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] text-slate-500">0.04σ residual</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-400 border border-white/10">
              Healthy
            </span>
          </div>
        </div>
      </div>

      {/* Info footer */}
      <div className="mt-3 pt-2 border-t border-white/5 flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
        <Info className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
        <span>Tracks cumulative degradation weeks before failure corrupts numerical weather models.</span>
      </div>
    </div>
  );
}
