'use client';

import React, { useState } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import {
  Flame,
  ArrowDownCircle,
  Lock,
  TrendingUp,
  Unlink,
  Radio,
  CheckCircle,
  Zap,
} from 'lucide-react';

export function SimulatorControls() {
  const { activeFault, setSimulatorState, pitchScriptStatus } = useTelemetryStore();
  const [loadingFault, setLoadingFault] = useState<string | null>(null);
  const [duration, setDuration] = useState<number>(30);
  const [intensity, setIntensity] = useState<number>(1.0);

  const faults = [
    {
      id: 'normal',
      name: 'Clean Nominal Baseline',
      desc: 'Normal diurnal cycle. No faults. 3D Twin is Green.',
      icon: CheckCircle,
      color: 'emerald',
      detector: 'Nominal',
    },
    {
      id: 'humidity_drift',
      name: 'Subtle Capacitive Drift (+15%)',
      desc: 'Slow +15% bias. Stays <100% so IMD rules pass, but 1D-CNN autoencoder flags correlation collapse!',
      icon: TrendingUp,
      color: 'rose',
      detector: '1D-CNN Autoencoder',
      highlight: true,
    },
    {
      id: 'cross_decoupling',
      name: 'Cross-Channel Decoupling',
      desc: 'Simultaneous 38°C temp and 88% RH without barometric drop. Breaks multivariate manifold.',
      icon: Unlink,
      color: 'rose',
      detector: '1D-CNN Autoencoder',
      highlight: true,
    },
    {
      id: 'heat_spike',
      name: 'Thermal Spike (+8°C)',
      desc: 'Abrupt +8°C jump in 1 second. Exceeds physical thermal inertia limits.',
      icon: Flame,
      color: 'amber',
      detector: 'IMD Rate-of-Change Rule',
    },
    {
      id: 'pressure_drop',
      name: 'Barometric Drop (-7 hPa)',
      desc: 'Rapid barometric discontinuity. Simulates sudden pressure transducer dropout.',
      icon: ArrowDownCircle,
      color: 'amber',
      detector: 'IMD Pressure Step Rule',
    },
    {
      id: 'stuck_humidity',
      name: 'Stuck Sensor (100% RH Flatline)',
      desc: 'Humidity frozen flatlined at 100% physical saturation for consecutive steps.',
      icon: Lock,
      color: 'amber',
      detector: 'IMD Flatline Rule',
    },
    {
      id: 'sensor_noise',
      name: 'High-Frequency Noise',
      desc: 'Gaussian electrical noise injected across temperature, pressure, and humidity.',
      icon: Radio,
      color: 'slate',
      detector: 'Noise Filter',
    },
  ];

  const handleInject = async (faultId: string) => {
    setLoadingFault(faultId);
    if (faultId === 'normal') {
      await api.resetSimulator();
      setSimulatorState('normal', pitchScriptStatus);
    } else {
      await api.injectFault(faultId, intensity, duration);
      setSimulatorState(faultId, pitchScriptStatus);
    }
    setLoadingFault(null);
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
            Virtual Edge Fault Injector
          </h2>
        </div>
        <div className="text-[11px] font-mono text-slate-400">
          Target: <strong>AGRA-01</strong>
        </div>
      </div>

      {/* Config: Duration and Intensity */}
      <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-900/50 border border-white/5 text-xs font-mono">
        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">Fault Duration</label>
          <div className="flex gap-1.5">
            {[15, 30, 60].map((sec) => (
              <button
                key={sec}
                onClick={() => setDuration(sec)}
                className={`flex-1 py-1 rounded text-[11px] font-semibold transition-all ${
                  duration === sec
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'bg-white/5 text-slate-400 hover:bg-white/10'
                }`}
              >
                {sec}s
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">
            Intensity: <strong>{intensity.toFixed(1)}x</strong>
          </label>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={intensity}
            onChange={(e) => setIntensity(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 mt-2"
          />
        </div>
      </div>

      {/* Fault Injection Button Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {faults.map((f) => {
          const Icon = f.icon;
          const isActive = activeFault === f.id;
          const isLoading = loadingFault === f.id;

          return (
            <button
              key={f.id}
              onClick={() => handleInject(f.id)}
              disabled={isLoading}
              className={`text-left p-3 rounded-xl border transition-all relative overflow-hidden ${
                isActive
                  ? f.id === 'normal'
                    ? 'bg-emerald-950/40 border-emerald-500/60 shadow-glow-emerald'
                    : 'bg-rose-950/40 border-rose-500/60 shadow-glow-rose'
                  : f.highlight
                  ? 'glass-panel-interactive border-cyan-500/30 hover:border-cyan-400'
                  : 'glass-panel-interactive border-white/10'
              }`}
            >
              {f.highlight && !isActive && (
                <div className="absolute top-0 right-0 bg-cyan-500/20 text-cyan-300 text-[9px] font-mono px-2 py-0.5 rounded-bl font-bold">
                  AI MANIFOLD TEST
                </div>
              )}

              <div className="flex items-center gap-2 mb-1">
                <Icon
                  className={`w-4 h-4 ${
                    isActive
                      ? f.id === 'normal'
                        ? 'text-emerald-400'
                        : 'text-rose-400 animate-pulse'
                      : f.id === 'normal'
                      ? 'text-emerald-400'
                      : 'text-cyan-400'
                  }`}
                />
                <span className="font-mono text-xs font-bold text-white tracking-tight truncate">
                  {f.name}
                </span>
              </div>

              <p className="text-[11px] text-slate-400 line-clamp-2 mb-2 font-sans">
                {f.desc}
              </p>

              <div className="flex items-center justify-between text-[10px] font-mono pt-1.5 border-t border-white/5">
                <span className="text-slate-500">Detector: {f.detector}</span>
                {isActive && (
                  <span className="text-rose-400 font-bold animate-pulse">ACTIVE NOW</span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
