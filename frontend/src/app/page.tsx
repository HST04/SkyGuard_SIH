'use client';

import React, { useState } from 'react';
import { useSSE } from '@/hooks/useSSE';
import { WeatherStation3D } from '@/components/twin/WeatherStation3D';
import { TelemetryPanel } from '@/components/panels/TelemetryPanel';
import { ShapChart } from '@/components/panels/ShapChart';
import { AnomalyList } from '@/components/panels/AnomalyList';
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import { Flame, TrendingUp, RotateCcw, Play, Zap, PanelRightClose, PanelRightOpen } from 'lucide-react';

export default function DashboardPage() {
  // Connect SSE real-time pipeline to Station AGRA-01
  useSSE('AGRA-01');

  const { activeFault, setSimulatorState, pitchScriptStatus } = useTelemetryStore();
  const [isExpanded, setIsExpanded] = useState(false);
  const [showFloatingPanel, setShowFloatingPanel] = useState(false);

  const handleQuickFault = async (fault: string) => {
    if (fault === 'normal') {
      await api.resetSimulator();
      setSimulatorState('normal', pitchScriptStatus);
    } else {
      await api.injectFault(fault, 1.0, 30);
      setSimulatorState(fault, pitchScriptStatus);
    }
  };

  const handleStartPitch = async () => {
    await api.startPitchScript();
    const st = await api.getSimulatorStatus();
    if (st) setSimulatorState(st.active_fault, st.pitch_script);
  };

  return (
    // FIX 1: Added min-h-0 to the root container to allow proper flex shrinking
    <div className="flex-1 flex flex-col lg:flex-row h-[calc(100vh-4rem)] overflow-hidden relative min-h-0">
      
      {/* 3D Digital Twin Canvas — Default 72% width, Expandable to 100% */}
      <div
        className={`relative border-b lg:border-b-0 border-white/10 flex flex-col flex-1 self-stretch min-h-0 transition-all duration-300 ease-in-out ${
          isExpanded
            ? 'w-full lg:w-full'
            : 'w-full lg:w-[68%] xl:w-[72%] lg:border-r'
        }`}
        style={{ height: 'calc(100vh - 4rem)', minHeight: 'calc(100vh - 4rem)' }}
      >
        {/* Quick Presenter Action Bar — Centered at Top with clean spacing */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 hidden md:flex items-center gap-1.5 glass-panel px-3 py-1.5 rounded-xl border border-white/10 shadow-glass">
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-semibold mr-1">
            Chaos Test:
          </span>

          <button
            onClick={() => handleQuickFault('humidity_drift')}
            className={`px-2 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1 transition-all ${
              activeFault === 'humidity_drift'
                ? 'bg-rose-500/30 text-rose-200 border border-rose-500/50 shadow-glow-rose'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/5'
            }`}
            title="Inject subtle +15% capacitive drift to test 1D-CNN autoencoder"
          >
            <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
            <span>Capacitive Drift</span>
          </button>

          <button
            onClick={() => handleQuickFault('heat_spike')}
            className={`px-2 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1 transition-all ${
              activeFault === 'heat_spike'
                ? 'bg-amber-500/30 text-amber-200 border border-amber-500/50'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/5'
            }`}
            title="Inject +8°C instant transient to test IMD rule engine"
          >
            <Flame className="w-3.5 h-3.5 text-amber-400" />
            <span>Heat Spike</span>
          </button>

          <button
            onClick={() => handleQuickFault('normal')}
            className="px-2 py-1 rounded-lg text-xs font-mono font-medium bg-white/5 hover:bg-white/10 border border-white/5 text-slate-300 flex items-center gap-1 transition-all"
            title="Reset to clean baseline"
          >
            <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
            <span>Reset</span>
          </button>

          <button
            onClick={handleStartPitch}
            className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-500/40 text-indigo-300 flex items-center gap-1.5 transition-all"
            title="Launch 5-minute automated pitch script"
          >
            <Play className="w-3 h-3 fill-indigo-400 text-indigo-400" />
            <span>Auto-Demo</span>
          </button>
        </div>

        {/* The 3D Digital Twin View */}
        {/* FIX 3: Added min-h-0 and relative. This ensures the canvas fills this exact box. */}
        <div className="flex-1 w-full h-full min-h-0 relative" style={{ height: '100%' }}>
          <WeatherStation3D
            isExpanded={isExpanded}
            onToggleExpand={() => setIsExpanded(!isExpanded)}
          />
        </div>

        {/* Floating Telemetry Drawer Toggle when in Fullscreen / Maximize Mode */}
        {isExpanded && (
          <button
            onClick={() => setShowFloatingPanel(!showFloatingPanel)}
            className="absolute bottom-4 right-4 z-30 glass-panel-interactive px-3 py-2 rounded-xl text-xs font-mono text-cyan-300 border border-cyan-500/30 flex items-center gap-2 shadow-glass"
          >
            {showFloatingPanel ? <PanelRightClose className="w-4 h-4" /> : <PanelRightOpen className="w-4 h-4" />}
            <span>{showFloatingPanel ? 'Hide Drawer' : 'Show Telemetry & Alerts'}</span>
          </button>
        )}
      </div>

      {/* Floating Telemetry Drawer in Fullscreen Mode */}
      {isExpanded && showFloatingPanel && (
        <div className="absolute top-0 right-0 h-full w-full sm:w-[420px] z-20 glass-panel border-l border-white/10 p-4 overflow-y-auto space-y-4 shadow-2xl backdrop-blur-2xl bg-[#080c14]/90 animate-in slide-in-from-right duration-300">
          <div className="flex items-center justify-between pb-2 border-b border-white/10">
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
              Live Station Telemetry & Alerts
            </h2>
            <button
              onClick={() => setShowFloatingPanel(false)}
              className="text-slate-400 hover:text-white text-xs font-mono"
            >
              ✕
            </button>
          </div>
          <TelemetryPanel />
          <ShapChart />
          <AnomalyList />
          <TimeSeriesChart />
        </div>
      )}

      {/* Standard Split Layout Panel Stack (30% width) */}
      {!isExpanded && (
        // FIX 4: Added min-h-0 here so the scrolling panel doesn't break the parent layout
        <div className="w-full lg:w-[32%] xl:w-[28%] h-[50vh] lg:h-full min-h-0 overflow-y-auto p-4 space-y-4 bg-[#080c14]/90">
          {/* Section 1: Live Telemetry Cards */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                Live Sensor Ingestion (1 Hz)
              </h2>
              <span className="text-[10px] font-mono text-cyan-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                Click card to focus 3D
              </span>
            </div>
            <TelemetryPanel />
          </div>

          {/* Section 2: SHAP Explainability Breakdown */}
          <div>
            <ShapChart />
          </div>

          {/* Section 3: Active Anomaly Triage & Feedback Loop */}
          <div>
            <AnomalyList />
          </div>

          {/* Section 4: Real-Time Multivariate Telemetry Graph */}
          <div>
            <TimeSeriesChart />
          </div>
        </div>
      )}
    </div>
  );
}