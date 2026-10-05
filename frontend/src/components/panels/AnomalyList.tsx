'use client';

import React, { useState } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { AnomalyCard } from './AnomalyCard';
import { api } from '@/lib/api';
import { AlertCircle, CheckCircle2, Check, EyeOff, CheckCheck, ListFilter } from 'lucide-react';

export function AnomalyList() {
  const { anomalies, bulkActionAnomalies } = useTelemetryStore();
  const [filter, setFilter] = useState<'open' | 'logged' | 'all'>('open');
  const [loadingBulk, setLoadingBulk] = useState<string | null>(null);

  const filtered = anomalies.filter((a) => {
    if (filter === 'open') return a.status === 'open';
    if (filter === 'logged') return a.status !== 'open';
    return true;
  });

  const openCount = anomalies.filter((a) => a.status === 'open').length;
  const loggedCount = anomalies.filter((a) => a.status !== 'open').length;

  const handleBulkAction = async (action: 'resolved' | 'acknowledged' | 'ignored') => {
    setLoadingBulk(action);
    try {
      await api.bulkActionAnomalies('AGRA-01', action, `Bulk ${action} by operator console`);
      bulkActionAnomalies(action, `Bulk ${action} by operator console`);
    } catch (err) {
      console.error(`Failed to bulk ${action} anomalies:`, err);
    } finally {
      setLoadingBulk(null);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-white/10 flex flex-col h-full max-h-[500px]">
      {/* Header with Title & Active Count */}
      <div className="flex items-center justify-between gap-2 mb-3 pb-3 border-b border-white/5 flex-wrap">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Detected Sensor Defects
          </h3>
          {openCount > 0 ? (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold animate-pulse">
              {openCount} ACTIVE ALARMS
            </span>
          ) : (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-medium">
              ALL SENSORS OK
            </span>
          )}
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-0.5 bg-black/40 p-0.5 rounded-lg border border-white/5 text-[10px] font-mono">
          <button
            onClick={() => setFilter('open')}
            className={`px-2 py-0.5 rounded transition-all ${
              filter === 'open'
                ? 'bg-rose-500/20 text-rose-200 border border-rose-500/40 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Open ({openCount})
          </button>
          <button
            onClick={() => setFilter('logged')}
            className={`px-2 py-0.5 rounded transition-all ${
              filter === 'logged'
                ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/40 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Logged ({loggedCount})
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-2 py-0.5 rounded transition-all ${
              filter === 'all'
                ? 'bg-white/10 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All ({anomalies.length})
          </button>
        </div>
      </div>

      {/* Requirement 2: Bulk Action Bar when defects are open */}
      {openCount > 0 && (
        <div className="mb-3 p-2 rounded-xl bg-black/30 border border-white/10 flex items-center justify-between gap-2 flex-wrap text-[10px] font-mono">
          <span className="text-slate-400 flex items-center gap-1">
            <CheckCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>Bulk Handle All ({openCount}):</span>
          </span>

          <div className="flex items-center gap-1.5 ml-auto">
            <button
              onClick={() => handleBulkAction('acknowledged')}
              disabled={loadingBulk !== null}
              className="py-1 px-2 rounded bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/30 flex items-center gap-1 transition-all active:scale-95"
              title="Acknowledge all open defect alerts"
            >
              <CheckCircle2 className="w-3 h-3 text-sky-400" />
              <span>{loadingBulk === 'acknowledged' ? '...' : 'Acknowledge All'}</span>
            </button>

            <button
              onClick={() => handleBulkAction('resolved')}
              disabled={loadingBulk !== null}
              className="py-1 px-2.5 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 flex items-center gap-1 transition-all active:scale-95 font-semibold"
              title="Resolve all defect alerts and restore normal station state"
            >
              <Check className="w-3 h-3 text-emerald-400" />
              <span>{loadingBulk === 'resolved' ? '...' : 'Resolve All'}</span>
            </button>

            <button
              onClick={() => handleBulkAction('ignored')}
              disabled={loadingBulk !== null}
              className="py-1 px-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/10 flex items-center gap-1 transition-all active:scale-95"
              title="Ignore open defect alerts and assume all sensors OK"
            >
              <EyeOff className="w-3 h-3 text-slate-400" />
              <span>{loadingBulk === 'ignored' ? '...' : 'Ignore All'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Scrollable Anomaly Cards List */}
      <div className="overflow-y-auto space-y-2.5 pr-1 flex-1">
        {filtered.length === 0 ? (
          <div className="h-36 flex flex-col items-center justify-center text-center p-4 rounded-xl bg-slate-900/30 border border-white/5 space-y-1">
            <span className="text-xs font-mono text-slate-300 font-semibold">
              {filter === 'open' ? 'No active alerts. All sensors OK.' : 'No anomalies logged in this filter.'}
            </span>
            <span className="text-[10px] font-mono text-slate-500 max-w-xs">
              {filter === 'open'
                ? 'Station telemetry is operating within nominal physical bounds.'
                : 'Detected sensor defects and operator logs will appear here.'}
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
