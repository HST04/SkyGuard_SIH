'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { Shield, Radio, Activity, Play, Sparkles, Terminal } from 'lucide-react';

export function Header() {
  const pathname = usePathname();
  const { connectionStatus, activeFault, pitchScriptStatus, stationStatus } = useTelemetryStore();

  return (
    <header className="h-16 border-b border-white/10 glass-panel sticky top-0 z-40 px-5 flex items-center justify-between">
      {/* Brand & Station Info */}
      <div className="flex items-center gap-3.5">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 p-0.5 flex items-center justify-center shadow-glow-cyan group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-[#080c14] rounded-[10px] flex items-center justify-center">
              <Shield className="w-4 h-4 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5 font-mono font-bold text-sm tracking-wide text-white">
              <span>SkyGuard</span>
              <span className="text-cyan-400">AI</span>
              <span className="text-[10px] font-sans px-1.5 py-0.2 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                MVP v1.0
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
              <span>Station: <strong>AGRA-01</strong></span>
              <span className="text-slate-600">•</span>
              <span className="text-slate-400">IMD Physics + 1D-CNN</span>
            </div>
          </div>
        </Link>
      </div>

      {/* Middle Status Indicator */}
      <div className="hidden md:flex items-center gap-3">
        {pitchScriptStatus && pitchScriptStatus.active && (
          <div className="glass-pill px-3 py-1 rounded-full border border-indigo-500/40 text-xs font-mono text-indigo-300 flex items-center gap-2 animate-pulse">
            <Play className="w-3 h-3 text-indigo-400 fill-indigo-400" />
            <span>Pitch Script Active: <strong>{pitchScriptStatus.phase_title}</strong></span>
          </div>
        )}

        {activeFault !== 'normal' && !pitchScriptStatus?.active && (
          <div className="glass-pill px-3 py-1 rounded-full border border-rose-500/40 text-xs font-mono text-rose-300 flex items-center gap-2">
            <Activity className="w-3 h-3 text-rose-400 animate-bounce" />
            <span>Injected Fault: <strong className="uppercase">{activeFault.replace('_', ' ')}</strong></span>
          </div>
        )}
      </div>

      {/* Right Controls: Live SSE pill & Link to Virtual Edge Simulator */}
      <div className="flex items-center gap-3">
        {/* SSE Status Pill */}
        <div className="glass-pill px-3 py-1.5 rounded-full flex items-center gap-2 text-xs font-mono border border-white/10">
          <div
            className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected'
                ? 'bg-emerald-400 shadow-glow-emerald animate-pulse'
                : connectionStatus === 'connecting'
                ? 'bg-amber-400 animate-ping'
                : 'bg-rose-500'
            }`}
          />
          <span className="text-slate-300 text-[11px]">
            {connectionStatus === 'connected' ? 'LIVE 1 Hz SSE' : connectionStatus.toUpperCase()}
          </span>
        </div>

        {/* Virtual Edge Simulator Nav Pill */}
        <Link
          href={pathname === '/edge-simulator' ? '/' : '/edge-simulator'}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-medium flex items-center gap-2 transition-all border ${
            pathname === '/edge-simulator'
              ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-glow-cyan'
              : 'glass-panel-interactive text-slate-200 border-white/10 hover:border-cyan-500/40'
          }`}
        >
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span>{pathname === '/edge-simulator' ? 'Back to 3D Twin' : 'Edge Simulator'}</span>
          {pathname !== '/edge-simulator' && (
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          )}
        </Link>
      </div>
    </header>
  );
}
