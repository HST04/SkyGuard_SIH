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
import { DebatePanel } from '@/components/panels/DebatePanel';
import { DecisionAuditPanel } from '@/components/panels/DecisionAuditPanel';
import { FloatingDebateWidget } from '@/components/panels/FloatingDebateWidget';
import { useTelemetryStore, DashboardTab } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import {
  Activity,
  Layers,
  Wrench,
  Cpu,
  PanelRightClose,
  PanelRightOpen,
  Radio,
  MessageSquare,
  History,
} from 'lucide-react';

export default function DashboardPage() {
  // Connect SSE real-time pipeline to Station AGRA-01
  useSSE('AGRA-01');

  const {
    activeFault,
    activeTab,
    setActiveTab,
    stationStatus,
    confluence,
    imputation,
    decisions,
    telemetryHistory,
    latestTelemetry,
  } = useTelemetryStore();

  const [isExpanded, setIsExpanded] = useState(false);
  const [showFloatingPanel, setShowFloatingPanel] = useState(false);

  const isStandby = !latestTelemetry || telemetryHistory.length === 0;

  // Tab Definitions (6 Tabs for comprehensive operator overview)
  const tabs: { id: DashboardTab; label: string; icon: React.ComponentType<{ className?: string }>; badge?: string }[] = [
    {
      id: 'confluence',
      label: 'Live ML & Status',
      icon: Activity,
      badge: confluence?.classification === 'Sensor Defect' ? 'DEFECT' : undefined,
    },
    {
      id: 'debate',
      label: 'AI Debate Arena',
      icon: MessageSquare,
      badge: confluence?.agent_dialogue && confluence.agent_dialogue.length > 0 ? `${confluence.agent_dialogue.length}` : undefined,
    },
    {
      id: 'decisions',
      label: 'Decision Log',
      icon: History,
      badge: decisions.length > 0 ? `${decisions.length}` : undefined,
    },
    {
      id: 'explainability',
      label: 'SHAP Explainability',
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
        {/* Clean Standby State Indicator over 3D Digital Twin Canvas */}
        {isStandby && (
          <div className="absolute bottom-4 left-4 z-20 pointer-events-none">
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-700/60 shadow-glass backdrop-blur-md">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
              </span>
              <span className="text-[11px] text-slate-300 font-mono">
                Awaiting edge stream • Launch simulator via terminal
              </span>
            </div>
          </div>
        )}

        {/* The 3D Digital Twin View */}
        <div className="flex-1 w-full h-full min-h-0 relative" style={{ height: '100%' }}>
          <WeatherStation3D isExpanded={isExpanded} onToggleExpand={() => setIsExpanded(!isExpanded)} />
          <FloatingDebateWidget />
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
        <div className="absolute top-0 right-0 h-full w-full sm:w-[500px] z-30 glass-panel border-l border-white/10 p-4 overflow-y-auto space-y-4 shadow-2xl backdrop-blur-2xl bg-[#080c14]/95 animate-in slide-in-from-right duration-300">
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
            <DebatePanel />
            <DecisionAuditPanel />
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

      {/* Standard Split Layout 6-Tab Panel Stack (440px - 490px width) */}
      {!isExpanded && (
        <div className="w-full lg:w-[440px] xl:w-[490px] h-[50vh] lg:h-full min-h-0 flex flex-col bg-[#080c14]/95 border-t lg:border-t-0 flex-shrink-0">
          {/* 6-Tab Switcher Header */}
          <div className="p-3 border-b border-white/10 bg-black/40">
            <div className="grid grid-cols-6 gap-1 p-1 rounded-xl bg-slate-900/80 border border-white/10">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                const shortLabel =
                  tab.id === 'confluence'
                    ? 'Overview'
                    : tab.id === 'debate'
                    ? 'Debate'
                    : tab.id === 'decisions'
                    ? 'Decisions'
                    : tab.id === 'explainability'
                    ? 'SHAP'
                    : tab.id === 'maintenance'
                    ? 'Maint'
                    : 'Repair';

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`relative py-2 px-0.5 rounded-lg text-[10px] font-mono font-medium flex flex-col items-center justify-center gap-1 transition-all ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/50 shadow-glow-cyan'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-300' : 'text-slate-400'}`} />
                    <span className="truncate max-w-full leading-tight text-center">
                      {shortLabel}
                    </span>

                    {/* Small Status Badge if active alert */}
                    {tab.badge && (
                      <span className="absolute -top-1 -right-0.5 px-1 py-0.2 rounded bg-rose-500 text-white text-[7px] font-bold font-mono uppercase shadow-glow-rose">
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

            {/* TAB 2: AI Multi-Agent Adversarial Debate Arena */}
            {activeTab === 'debate' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <DebatePanel />
              </div>
            )}

            {/* TAB 3: AI Decisions Audit Trail */}
            {activeTab === 'decisions' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <DecisionAuditPanel />
              </div>
            )}

            {/* TAB 4: Explainable AI (SHAP & Diagnostics) */}
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