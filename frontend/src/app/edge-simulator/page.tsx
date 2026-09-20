'use client';

import React from 'react';
import Link from 'next/link';
import { useSSE } from '@/hooks/useSSE';
import { SimulatorControls } from '@/components/simulator/SimulatorControls';
import { ScenarioRunner } from '@/components/simulator/ScenarioRunner';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { ArrowLeft, Terminal, Cpu, Database, Activity } from 'lucide-react';

export default function EdgeSimulatorPage() {
  useSSE('AGRA-01');
  const { latestTelemetry } = useTelemetryStore();

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* Top Breadcrumb & Title */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to 3D Digital Twin</span>
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
              <Terminal className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-xl font-mono font-bold text-white tracking-tight">
                Virtual Edge Simulator & Chaos Harness
              </h1>
              <p className="text-xs text-slate-400 font-mono">
                Simulating station <strong>AGRA-01</strong> hardware telemetry with real-time fault injection.
              </p>
            </div>
          </div>
        </div>

        {/* Live Packet Telemetry Badge */}
        {latestTelemetry && (
          <div className="glass-panel px-4 py-2 rounded-xl border border-white/10 flex items-center gap-4 text-xs font-mono">
            <div>
              <div className="text-slate-400 text-[10px]">CURRENT SEQ</div>
              <div className="text-white font-bold">#{latestTelemetry.sequence}</div>
            </div>
            <div className="h-6 w-px bg-white/10" />
            <div>
              <div className="text-slate-400 text-[10px]">TEMPERATURE</div>
              <div className="text-cyan-300 font-bold">{latestTelemetry.temperature_c.toFixed(1)} °C</div>
            </div>
            <div className="h-6 w-px bg-white/10" />
            <div>
              <div className="text-slate-400 text-[10px]">HUMIDITY</div>
              <div className="text-emerald-300 font-bold">{latestTelemetry.humidity_pct.toFixed(1)} %</div>
            </div>
          </div>
        )}
      </div>

      {/* Grid: Pitch Script Runner & Manual Fault Injector */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Automated Pitch Script */}
        <div className="space-y-6">
          <ScenarioRunner />

          {/* Real-time MQTT Payload Inspector */}
          <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
                  MQTT Ingestion Payload Inspector
                </h3>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                Streaming 1 Hz
              </span>
            </div>

            <pre className="p-3.5 rounded-xl bg-slate-950/80 border border-white/5 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-56">
              {latestTelemetry
                ? JSON.stringify(latestTelemetry, null, 2)
                : '// Waiting for incoming telemetry packet...'}
            </pre>
          </div>
        </div>

        {/* Right Column: Manual Fault Injector */}
        <div>
          <SimulatorControls />
        </div>
      </div>
    </div>
  );
}
