'use client';

import React, { useState } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { AnomalyCard } from './AnomalyCard';
import { AlertCircle, Filter, Trash2 } from 'lucide-react';

export function AnomalyList() {
  const { anomalies, clearAnomalies } = useTelemetryStore();
  const [filter, setFilter] = useState<'all' | 'open' | 'resolved'>('open');

  const filtered = anomalies.filter((a) => {
    if (filter === 'open') return a.status === 'open';
    if (filter === 'resolved') return a.status === 'resolved' || a.status === 'false_alarm';
    return true;
  });

  const openCount = anomalies.filter((a) => a.status === 'open').length;

  return (
    <div className="glass-panel rounded-2xl p-4 border border-white/10 flex flex-col h-full max-h-[460px]">
      {/* Header with Filters */}
      <div className="flex items-center justify-between gap-2 mb-3 pb-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Detected Anomalies
          </h3>
          {openCount > 0 && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold animate-pulse">
              {openCount} ACTIVE
            </span>
          )}
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1">
          {(['open', 'resolved', 'all'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`text-[10px] font-mono px-2 py-1 rounded-md capitalize transition-all ${
                filter === f
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Scrollable Anomaly Cards List */}
      <div className="overflow-y-auto space-y-2.5 pr-1 flex-1">
        {filtered.length === 0 ? (
          <div className="h-32 flex flex-col items-center justify-center text-center p-4 rounded-xl bg-slate-900/30 border border-white/5">
            <span className="text-xs font-mono text-slate-400">
              {filter === 'open' ? 'No active alerts. System healthy.' : 'No anomalies logged.'}
            </span>
            <span className="text-[10px] font-mono text-slate-500 mt-1">
              Trigger faults from the Edge Simulator to test detection.
            </span>
          </div>
        ) : (
          filtered.map((anomaly) => (
            <AnomalyCard key={anomaly.anomaly_id} anomaly={anomaly} />
          ))
        )}
      </div>
    </div>
  );
}
