'use client';

import React, { useState } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import { Play, Square, CheckCircle2, Clock, Sparkles } from 'lucide-react';

export function ScenarioRunner() {
  const { pitchScriptStatus, setSimulatorState } = useTelemetryStore();
  const [loading, setLoading] = useState(false);

  const isRunning = pitchScriptStatus?.active ?? false;
  const elapsed = pitchScriptStatus?.elapsed_seconds ?? 0;
  const total = 300;
  const progressPct = Math.min(100, Math.round((elapsed / total) * 100));

  const handleStart = async () => {
    setLoading(true);
    await api.startPitchScript();
    const st = await api.getSimulatorStatus();
    if (st) setSimulatorState(st.active_fault, st.pitch_script);
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    await api.stopPitchScript();
    const st = await api.getSimulatorStatus();
    if (st) setSimulatorState(st.active_fault, st.pitch_script);
    setLoading(false);
  };

  const phases = [
    {
      id: 'BASELINE',
      time: '0:00 – 1:30',
      title: 'Baseline Diurnal',
      desc: 'Normal weather cycles. 3D Twin Green.',
      range: [0, 90],
    },
    {
      id: 'TRUE_NEGATIVE_STORM',
      time: '1:30 – 3:00',
      title: 'Thunderstorm True-Negative',
      desc: 'Violent pressure drop & humidity surge. CNN respects natural physics. Zero false alarm (Stays Green).',
      range: [90, 180],
    },
    {
      id: 'CAPACITIVE_DRIFT',
      time: '3:00 – 3:45',
      title: 'Subtle Capacitive Drift',
      desc: 'Injected +15% humidity bias. Bypasses static rules. 1D-CNN accumulates error.',
      range: [180, 225],
    },
    {
      id: 'ANOMALY_TRIGGERED',
      time: '3:45 – 5:00',
      title: 'AI Anomaly & SHAP',
      desc: 'Autoencoder threshold trips! 3D twin pulses Red, camera auto-zooms, SHAP isolates sensor.',
      range: [225, 300],
    },
  ];

  return (
    <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <div>
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
              5-Minute Auto-Scenario Pitch Script
            </h2>
            <div className="text-[11px] text-slate-400 font-sans">
              Automated, hands-free demonstration sequence for judges & teammates.
            </div>
          </div>
        </div>

        {isRunning ? (
          <button
            onClick={handleStop}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 text-xs font-mono font-bold flex items-center gap-1.5 transition-all"
          >
            <Square className="w-3.5 h-3.5 fill-rose-400 text-rose-400" />
            <span>Stop Script</span>
          </button>
        ) : (
          <button
            onClick={handleStart}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-mono font-bold flex items-center gap-2 shadow-glow-cyan transition-all"
          >
            <Play className="w-3.5 h-3.5 fill-white text-white" />
            <span>Run Pitch Script</span>
          </button>
        )}
      </div>

      {/* Progress Track */}
      {isRunning && (
        <div className="p-3 rounded-xl bg-slate-900/60 border border-indigo-500/30 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-indigo-300 font-semibold flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 animate-spin" />
              {pitchScriptStatus?.phase_title}
            </span>
            <span className="text-slate-400">
              {Math.floor(elapsed / 60)}:{(elapsed % 60).toString().padStart(2, '0')} / 5:00 ({progressPct}%)
            </span>
          </div>

          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-400 via-indigo-500 to-rose-500 transition-all duration-1000"
              style={{ width: `${progressPct}%` }}
            />
          </div>

          <p className="text-[11px] text-slate-300 font-mono">
            {pitchScriptStatus?.phase_description}
          </p>
        </div>
      )}

      {/* Timeline Steps */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {phases.map((phase) => {
          const isCurrent = isRunning && elapsed >= phase.range[0] && elapsed < phase.range[1];
          const isCompleted = isRunning && elapsed >= phase.range[1];

          return (
            <div
              key={phase.id}
              className={`p-3 rounded-xl border transition-all ${
                isCurrent
                  ? 'bg-indigo-950/40 border-indigo-500/60 shadow-glow-cyan/20'
                  : isCompleted
                  ? 'bg-emerald-950/20 border-emerald-500/30 opacity-80'
                  : 'bg-slate-900/30 border-white/5 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-1 text-xs font-mono">
                <span className="text-slate-400 font-semibold">{phase.time}</span>
                {isCurrent && (
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-500/30 text-indigo-300 font-bold animate-pulse">
                    CURRENT
                  </span>
                )}
                {isCompleted && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                )}
              </div>
              <div className="text-xs font-mono font-bold text-white mb-1">
                {phase.title}
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                {phase.desc}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
