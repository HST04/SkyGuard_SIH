'use client';

import React, { useState, useEffect } from 'react';
import { useSSE } from '@/hooks/useSSE';
import { WeatherStation3D } from '@/components/twin/WeatherStation3D';
import { TelemetryPanel } from '@/components/panels/TelemetryPanel';
import { LiveMLPipelinePanel } from '@/components/panels/LiveMLPipelinePanel';
import { ShapChart } from '@/components/panels/ShapChart';
import { AnomalyList } from '@/components/panels/AnomalyList';
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart';
import { ConfluenceAlertBanner } from '@/components/panels/ConfluenceAlertBanner';
import { PredictiveMaintenancePanel } from '@/components/panels/PredictiveMaintenancePanel';
import { ImputationPanel } from '@/components/panels/ImputationPanel';
import { useTelemetryStore, DashboardTab } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import {
  Flame,
  TrendingUp,
  RotateCcw,
  Play,
  CloudLightning,
  Activity,
  Layers,
  Sparkles,
  Wrench,
  Cpu,
  PanelRightClose,
  PanelRightOpen,
  Snowflake,
} from 'lucide-react';

export default function DashboardPage() {
  // Connect SSE real-time pipeline to Station AGRA-01
  useSSE('AGRA-01');

  const {
    activeFault,
    setSimulatorState,
    pitchScriptStatus,
    activeTab,
    setActiveTab,
    stationStatus,
    confluence,
    imputation,
  } = useTelemetryStore();

  const [isExpanded, setIsExpanded] = useState(false);
  const [showFloatingPanel, setShowFloatingPanel] = useState(false);

  // Quick Chaos Injection Trigger
  const handleQuickFault = async (fault: string) => {
    if (fault === 'normal') {
      await api.resetSimulator();
      setSimulatorState('normal', pitchScriptStatus);
    } else {
      await api.injectFault(fault, 1.0, 30);
      setSimulatorState(fault, pitchScriptStatus);
    }
  };

  // Keyboard shortcut listener to match Laptop 1 Chaos Keys (0, 1, 2, 3, 4)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input or textarea
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) return;

      if (e.key === '0') handleQuickFault('normal');
      if (e.key === '1') handleQuickFault('heat_spike');
      if (e.key === '2') {
        handleQuickFault('humidity_drift');
        setActiveTab('confluence');
      }
      if (e.key === '3') {
        handleQuickFault('valid_squall');
        setActiveTab('confluence');
      }
      if (e.key === '4') handleQuickFault('stuck_humidity');
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [pitchScriptStatus, setActiveTab]);

  const handleStartPitch = async () => {
    await api.startPitchScript();
    const st = await api.getSimulatorStatus();
    if (st) setSimulatorState(st.active_fault, st.pitch_script);
  };

  // Tab Definitions
  const tabs: { id: DashboardTab; label: string; icon: React.ComponentType<{ className?: string }>; badge?: string }[] = [
    {
      id: 'confluence',
      label: 'Live ML & Confluence',
      icon: Activity,
      badge: confluence?.classification === 'Sensor Defect' ? 'DEFECT' : undefined,
    },
    {
      id: 'explainability',
      label: 'Explainable AI (SHAP)',
      icon: Layers,
    },
    {
      id: 'maintenance',
      label: 'Maintenance',
      icon: Wrench,
      badge: activeFault === 'humidity_drift' ? '< 2 Wks' : undefined,
    },
    {
      id: 'imputation',
      label: 'Data Repair',
      icon: Cpu,
      badge: (imputation?.active || activeFault === 'humidity_drift') ? 'ACTION' : undefined,
    },
  ];

  return (
    <div className="flex-1 flex flex-col lg:flex-row h-[calc(100vh-4rem)] overflow-hidden relative min-h-0 bg-[#080c14]">
      {/* 3D Digital Twin Canvas — Flexible width, Expandable to 100% */}
      <div
        className={`relative border-b lg:border-b-0 border-white/10 flex flex-col flex-1 self-stretch min-h-0 h-full transition-all duration-300 ease-in-out ${
          isExpanded ? 'w-full lg:w-full' : 'w-full lg:flex-1 lg:border-r'
        }`}
      >
        {/* Quick Presenter Action Bar — Centered at Top with Terminal Key Shortcuts */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 hidden md:flex items-center gap-1.5 glass-panel px-3 py-1.5 rounded-xl border border-white/10 shadow-glass">
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-semibold mr-1">
            Quick Scenarios:
          </span>

          {/* Key 3: Thunderstorm Squall Line */}
          <button
            onClick={() => handleQuickFault('valid_squall')}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1.5 transition-all ${
              activeFault === 'valid_squall'
                ? 'bg-sky-500/30 text-sky-200 border border-sky-500/50 shadow-glow-cyan'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/5'
            }`}
            title="Press '3': Severe Thunderstorm (-11 hPa drop, 94% RH, -8°C). Zero False Alarm test."
          >
            <CloudLightning className="w-3.5 h-3.5 text-sky-400" />
            <span>[3] Thunderstorm</span>
          </button>

          {/* Key 2: Capacitive Drift */}
          <button
            onClick={() => handleQuickFault('humidity_drift')}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1.5 transition-all ${
              activeFault === 'humidity_drift'
                ? 'bg-rose-500/30 text-rose-200 border border-rose-500/50 shadow-glow-rose'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/5'
            }`}
            title="Press '2': Capacitive Drift (+15% RH bias). Auto-targets 3D humidity sensor."
          >
            <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
            <span>[2] Capacitive Drift</span>
          </button>

          {/* Key 1: Heat Spike */}
          <button
            onClick={() => handleQuickFault('heat_spike')}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1.5 transition-all ${
              activeFault === 'heat_spike'
                ? 'bg-amber-500/30 text-amber-200 border border-amber-500/50'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/5'
            }`}
            title="Press '1': Heat Spike (+8°C instant jump)"
          >
            <Flame className="w-3.5 h-3.5 text-amber-400" />
            <span>[1] Heat Spike</span>
          </button>

          {/* Key 4: Frozen Sensor */}
          <button
            onClick={() => handleQuickFault('stuck_humidity')}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium flex items-center gap-1.5 transition-all ${
              activeFault === 'stuck_humidity'
                ? 'bg-cyan-500/30 text-cyan-200 border border-cyan-500/50'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/5'
            }`}
            title="Press '4': Frozen Sensor flatline"
          >
            <Snowflake className="w-3.5 h-3.5 text-cyan-400" />
            <span>[4] Frozen</span>
          </button>

          {/* Key 0: Reset */}
          <button
            onClick={() => handleQuickFault('normal')}
            className="px-2.5 py-1 rounded-lg text-xs font-mono font-medium bg-white/5 hover:bg-white/10 border border-white/5 text-slate-300 flex items-center gap-1 transition-all"
            title="Press '0': Reset to clean baseline"
          >
            <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
            <span>[0] Reset</span>
          </button>

          {/* Pitch Script Auto-Demo */}
          <button
            onClick={handleStartPitch}
            className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-500/40 text-indigo-300 flex items-center gap-1.5 transition-all"
            title="Launch 5-minute automated pitch sequence"
          >
            <Play className="w-3 h-3 fill-indigo-400 text-indigo-400" />
            <span>Auto-Demo</span>
          </button>
        </div>

        {/* The 3D Digital Twin View */}
        <div className="flex-1 w-full h-full min-h-0 relative" style={{ height: '100%' }}>
          <WeatherStation3D isExpanded={isExpanded} onToggleExpand={() => setIsExpanded(!isExpanded)} />
        </div>

        {/* Floating Telemetry Drawer Toggle when in Fullscreen Mode */}
        {isExpanded && (
          <button
            onClick={() => setShowFloatingPanel(!showFloatingPanel)}
            className="absolute bottom-4 right-4 z-30 glass-panel-interactive px-3 py-2 rounded-xl text-xs font-mono text-cyan-300 border border-cyan-500/30 flex items-center gap-2 shadow-glass"
          >
            {showFloatingPanel ? <PanelRightClose className="w-4 h-4" /> : <PanelRightOpen className="w-4 h-4" />}
            <span>{showFloatingPanel ? 'Hide Drawer' : 'Show Inspection Drawer'}</span>
          </button>
        )}
      </div>

      {/* Floating Telemetry Drawer in Fullscreen Mode */}
      {isExpanded && showFloatingPanel && (
        <div className="absolute top-0 right-0 h-full w-full sm:w-[480px] z-30 glass-panel border-l border-white/10 p-4 overflow-y-auto space-y-4 shadow-2xl backdrop-blur-2xl bg-[#080c14]/95 animate-in slide-in-from-right duration-300">
          <div className="flex items-center justify-between pb-2 border-b border-white/10">
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
              Inspection Drawer
            </h2>
            <button onClick={() => setShowFloatingPanel(false)} className="text-slate-400 hover:text-white text-xs font-mono">
              ✕
            </button>
          </div>

          {/* Render Active Tab Content in Floating Drawer */}
          <div className="space-y-4">
            <ConfluenceAlertBanner />
            <LiveMLPipelinePanel />
            <TelemetryPanel />
            <PredictiveMaintenancePanel />
            <ImputationPanel />
            <ShapChart />
            <AnomalyList />
            <TimeSeriesChart />
          </div>
        </div>
      )}

      {/* Standard Split Layout 4-Tab Panel Stack (420px - 460px width) */}
      {!isExpanded && (
        <div className="w-full lg:w-[400px] xl:w-[450px] h-[50vh] lg:h-full min-h-0 flex flex-col bg-[#080c14]/95 border-t lg:border-t-0 flex-shrink-0">
          {/* 4-Tab Switcher Header */}
          <div className="p-3 border-b border-white/10 bg-black/40">
            <div className="grid grid-cols-4 gap-1 p-1 rounded-xl bg-slate-900/80 border border-white/10">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`relative py-2 px-1 rounded-lg text-[11px] font-mono font-medium flex flex-col items-center justify-center gap-1 transition-all ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/50 shadow-glow-cyan'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-300' : 'text-slate-400'}`} />
                    <span className="truncate max-w-full px-0.5 leading-tight text-center">
                      {tab.label.split(' ')[0]}
                    </span>

                    {/* Small Status Badge if active alert */}
                    {tab.badge && (
                      <span className="absolute -top-1 -right-1 px-1 py-0.2 rounded bg-rose-500 text-white text-[8px] font-bold font-mono uppercase shadow-glow-rose">
                        {tab.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Current Tab Title Sub-Strip */}
            <div className="flex items-center justify-between mt-2 px-1 text-[11px] font-mono">
              <span className="text-slate-400 font-semibold uppercase tracking-wider">
                {tabs.find((t) => t.id === activeTab)?.label}
              </span>
              <span className="text-[10px] text-cyan-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                1 Hz Real-Time
              </span>
            </div>
          </div>

          {/* Scrollable Tab Content Container */}
          <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
            {/* TAB 1: Live ML & Confluence Decision Matrix */}
            {activeTab === 'confluence' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                {/* Confluence Decision Banner */}
                <ConfluenceAlertBanner />

                {/* 1D-CNN Reconstruction Error Meter */}
                <LiveMLPipelinePanel />

                {/* Live Sensor Ingestion Tiles */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                      Live Telemetry (AGRA-01)
                    </h2>
                    <span className="text-[10px] font-mono text-slate-500">
                      Click tile to inspect in 3D
                    </span>
                  </div>
                  <TelemetryPanel />
                </div>

                {/* Multivariate Time Series Trend */}
                <div>
                  <TimeSeriesChart />
                </div>
              </div>
            )}

            {/* TAB 2: Explainable AI (SHAP & Diagnostics) */}
            {activeTab === 'explainability' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <ShapChart />
                <AnomalyList />
              </div>
            )}

            {/* TAB 3: Predictive Maintenance (EWMA Drift & Recalibration Horizon) */}
            {activeTab === 'maintenance' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <PredictiveMaintenancePanel />

                {/* Auxiliary Telemetry context */}
                <div>
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Current Sensor Stream
                  </div>
                  <TelemetryPanel />
                </div>
              </div>
            )}

            {/* TAB 4: Imputation & Data Repair ("Accept & Impute") */}
            {activeTab === 'imputation' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <ImputationPanel />

                {/* Auxiliary Context */}
                <ConfluenceAlertBanner />
                <LiveMLPipelinePanel />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}