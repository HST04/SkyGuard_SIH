'use client';

import React, { useState } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { api } from '@/lib/api';
import { Sparkles, Check, ArrowRight, ShieldCheck, AlertCircle, RefreshCw, Cpu } from 'lucide-react';

export function ImputationPanel() {
  const {
    imputation,
    latestTelemetry,
    activeFault,
    imputationAccepted,
    markImputationAccepted,
    setLatestTelemetry,
  } = useTelemetryStore();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successNote, setSuccessNote] = useState<string | null>(null);

  const imp = imputation || {
    active: activeFault === 'humidity_drift',
    sensor: 'humidity',
    reported: 84.2,
    suggested: 42.6,
    method: 'Multivariate Ridge Regression (T, P, Solar)',
    uncertainty: 1.8,
    mae: 0.45,
    reason: 'drift',
  };

  const isCorrupted = imp.active || activeFault === 'humidity_drift';
  const reportedVal = imp.reported !== undefined ? imp.reported.toFixed(1) : (latestTelemetry?.humidity_pct.toFixed(1) || '84.2');
  const suggestedVal = imp.suggested !== null && imp.suggested !== undefined ? imp.suggested.toFixed(1) : '42.6';
  const maeVal = imp.mae ? imp.mae.toFixed(2) : '0.45';

  const handleAcceptImpute = async () => {
    setIsSubmitting(true);
    setSuccessNote(null);
    try {
      await api.acceptImputation({
        station_id: latestTelemetry?.station_id || 'AGRA-01',
        sensor: 'humidity',
        suggested: Number(suggestedVal),
        reported: Number(reportedVal),
        timestamp: latestTelemetry?.timestamp || new Date().toISOString(),
        sequence: latestTelemetry?.sequence || 100,
        method: imp.method || 'Ridge Regression',
      });

      markImputationAccepted(true);
      setSuccessNote(`Applied imputed value (${suggestedVal}%) to active pipeline`);

      // Update current telemetry reading locally to reflect repaired value
      if (latestTelemetry) {
        setLatestTelemetry({
          ...latestTelemetry,
          humidity_pct: Number(suggestedVal),
          reconstruction_error: 0.0152,
        });
      }
    } catch {
      // Local fallback for offline/demo operation
      markImputationAccepted(true);
      setSuccessNote(`Applied imputed value (${suggestedVal}%) to active pipeline (simulated)`);
      if (latestTelemetry) {
        setLatestTelemetry({
          ...latestTelemetry,
          humidity_pct: Number(suggestedVal),
          reconstruction_error: 0.0152,
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className={`glass-panel rounded-2xl p-4 border transition-all duration-300 ${
        isCorrupted && !imputationAccepted
          ? 'border-cyan-500/50 bg-cyan-950/20 shadow-glow-cyan/20'
          : 'border-white/10 shadow-glass'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Imputation & Data Repair (Layer 3.5)
          </h3>
        </div>

        {imputationAccepted ? (
          <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
            <Check className="w-3 h-3 text-emerald-400" />
            REPAIRED
          </span>
        ) : isCorrupted ? (
          <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 animate-pulse flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            REPAIR AVAILABLE
          </span>
        ) : (
          <span className="text-[10px] font-mono font-medium px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            CHANNELS HEALTHY
          </span>
        )}
      </div>

      {/* Main Comparison Block: Reported vs Imputed */}
      <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 mb-3">
        <div className="flex items-center justify-between text-xs font-mono mb-2">
          <span className="text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
            Channel: Relative Humidity (RH)
          </span>
          <span className="text-slate-400 text-[10px]">MAE: ±{maeVal}%</span>
        </div>

        <div className="grid grid-cols-2 gap-3 items-center">
          {/* Corrupt Reported Value */}
          <div className="p-2.5 rounded-lg bg-black/40 border border-rose-500/30">
            <div className="text-[10px] font-mono text-rose-300 uppercase flex items-center gap-1">
              <AlertCircle className="w-3 h-3 text-rose-400" />
              Reported Corrupt
            </div>
            <div className="text-xl font-mono font-bold text-rose-200 mt-1">
              {reportedVal}%
            </div>
            <div className="text-[9px] font-mono text-slate-500 mt-0.5">
              Raw sensor bias
            </div>
          </div>

          {/* Corrected Suggested Value */}
          <div className="p-2.5 rounded-lg bg-cyan-950/40 border border-cyan-500/40 shadow-glow-cyan/20">
            <div className="text-[10px] font-mono text-cyan-300 uppercase flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              Suggested Repair
            </div>
            <div className="text-xl font-mono font-bold text-cyan-200 mt-1">
              {suggestedVal}%
            </div>
            <div className="text-[9px] font-mono text-slate-400 mt-0.5">
              Physical covariance estimate
            </div>
          </div>
        </div>

        {/* Delta Difference Bar */}
        <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-300">
          <span>Correction Delta:</span>
          <span className="text-cyan-400 font-bold">
            -{(Number(reportedVal) - Number(suggestedVal)).toFixed(1)}% RH bias removed
          </span>
        </div>
      </div>

      {/* Mathematical Method Explanation */}
      <div className="p-2.5 rounded-xl bg-black/20 border border-white/5 mb-3 text-xs font-mono text-slate-400 space-y-1">
        <div className="text-[10px] text-slate-400 uppercase font-semibold">Reconstruction Model:</div>
        <div className="text-slate-200">{imp.method || 'Multivariate Ridge Regression'}</div>
        <div className="text-[10px] text-slate-500">
          Reconstructs faulty channel using correlated thermodynamic variables (T, P, Solar) to preserve downstream NWP weather models.
        </div>
      </div>

      {/* Success Notification */}
      {successNote && (
        <div className="p-2 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs font-mono mb-3 flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{successNote}</span>
        </div>
      )}

      {/* Action Button: Accept & Impute */}
      <button
        onClick={handleAcceptImpute}
        disabled={isSubmitting || imputationAccepted}
        className={`w-full py-2.5 px-4 rounded-xl text-xs font-mono font-bold flex items-center justify-center gap-2 transition-all ${
          imputationAccepted
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 cursor-default'
            : isCorrupted
            ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white shadow-glow-cyan cursor-pointer'
            : 'bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10'
        }`}
      >
        {isSubmitting ? (
          <>
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Broadcasting Imputed Stream...</span>
          </>
        ) : imputationAccepted ? (
          <>
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span>Imputation Applied & Stream Corrected</span>
          </>
        ) : (
          <>
            <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
            <span>Accept & Impute Telemetry Stream</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </>
        )}
      </button>
    </div>
  );
}
