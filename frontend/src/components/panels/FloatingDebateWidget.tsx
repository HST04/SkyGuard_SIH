'use client';

import React, { useState } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { DebatePanel } from './DebatePanel';
import { MessageSquare, X, Maximize2, Minimize2 } from 'lucide-react';

export function FloatingDebateWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isFullWidth, setIsFullWidth] = useState(false);
  const { confluence } = useTelemetryStore();

  const dialogue = confluence?.agent_dialogue || [];
  const turnCount = dialogue.length;
  const isAnomaly = confluence && confluence.classification !== 'Nominal Baseline';

  return (
    <>
      {/* Floating Trigger Button on 3D Digital Twin Canvas */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={`absolute top-4 right-4 z-20 px-3.5 py-2 rounded-xl text-xs font-mono font-medium flex items-center gap-2 transition-all duration-300 shadow-glass border backdrop-blur-md ${
            isAnomaly
              ? 'bg-rose-950/80 border-rose-500/50 text-rose-200 hover:bg-rose-900 shadow-glow-rose/20 animate-pulse'
              : 'bg-slate-900/80 border-cyan-500/30 text-cyan-200 hover:bg-slate-850 hover:border-cyan-500/60'
          }`}
          title="Open AI Multi-Agent Debate Arena"
        >
          <div className="relative flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            {turnCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            )}
          </div>
          <span>AI Debate Arena</span>
          {turnCount > 0 ? (
            <span className="px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
              {turnCount} Turns
            </span>
          ) : (
            <span className="px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-slate-800 text-slate-400 border border-white/5">
              Standby
            </span>
          )}
        </button>
      )}

      {/* Floating Modal / Drawer */}
      {isOpen && (
        <div
          className={`absolute top-0 right-0 h-full z-30 glass-panel border-l border-white/10 p-4 overflow-y-auto shadow-2xl backdrop-blur-2xl bg-[#080c14]/95 animate-in slide-in-from-right duration-300 transition-all ${
            isFullWidth ? 'w-full' : 'w-full sm:w-[500px] xl:w-[540px]'
          }`}
        >
          {/* Header Bar */}
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-white/10">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                <MessageSquare className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
                  AI Debate Inspector
                </h3>
                <span className="text-[10px] font-mono text-slate-400">
                  Dual-Agent Real-time Consensus
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setIsFullWidth(!isFullWidth)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                title={isFullWidth ? 'Compact width' : 'Expand full width'}
              >
                {isFullWidth ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                title="Close drawer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Body Content */}
          <DebatePanel />
        </div>
      )}
    </>
  );
}
