'use client';

import React from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { BarChart3, HelpCircle, CheckCircle, AlertOctagon } from 'lucide-react';

export function ShapChart() {
  const { activeAnomaly } = useTelemetryStore();

  if (!activeAnomaly || activeAnomaly.status !== 'open') {
    return (
      <div className="glass-panel rounded-2xl p-4 border border-white/10">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              SHAP Explainability & Latent Bottleneck
            </h3>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
            NOMINAL
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/40 border border-white/5 flex items-center gap-3.5">
          <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <div className="text-xs font-mono text-slate-300">
            <div>1D-CNN Autoencoder latent bottleneck error is below operating threshold.</div>
            <div className="text-slate-500 text-[11px] mt-0.5">
              Current Reconstruction MSE: <strong>0.0142</strong> • Threshold: <strong>0.0420</strong>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const attributions = activeAnomaly.shap_values && activeAnomaly.shap_values.length > 0
    ? activeAnomaly.shap_values
    : [
        { feature: activeAnomaly.culprit_sensors[0] || 'humidity', importance: 0.88, direction: 'positive' as const, message: 'Sensor output diverges from multivariate physics.' },
        { feature: 'temperature', importance: 0.12, direction: 'negative' as const, message: 'Residual baseline variance.' },
      ];

  return (
    <div className="glass-panel rounded-2xl p-4 border border-rose-500/30 shadow-glow-rose/20">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-rose-400 animate-pulse" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            SHAP Attribution: Culprit Feature Breakdown
          </h3>
        </div>
        <div className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold">
          MSE: {activeAnomaly.reconstruction_error.toFixed(4)}
        </div>
      </div>

      {/* Plain-English Diagnostic Message */}
      <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-xs font-mono text-rose-200 mb-3">
        <div className="font-semibold text-[11px] text-rose-300 uppercase tracking-wider mb-1">
          Root-Cause Diagnostic
        </div>
        {activeAnomaly.diagnostic_message}
      </div>

      {/* Feature Attribution Horizontal Bars */}
      <div className="space-y-2.5">
        {attributions.map((attr, idx) => {
          const pct = Math.min(100, Math.round(attr.importance * 100));
          const isTop = idx === 0;

          return (
            <div key={attr.feature} className="font-mono text-xs">
              <div className="flex items-center justify-between mb-1">
                <span className={`font-semibold ${isTop ? 'text-rose-300' : 'text-slate-300'}`}>
                  {attr.feature.toUpperCase()}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-slate-400">
                    {attr.direction === 'positive' ? '+ Contribution' : '- Suppression'}
                  </span>
                  <span className={`font-bold ${isTop ? 'text-rose-400' : 'text-slate-300'}`}>
                    {pct}%
                  </span>
                </div>
              </div>

              {/* Progress Track */}
              <div className="w-full h-2 rounded-full bg-slate-800/80 overflow-hidden border border-white/5">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isTop ? 'bg-gradient-to-r from-amber-500 to-rose-500 shadow-glow-rose' : 'bg-cyan-500/70'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>

              <div className="text-[10px] text-slate-400 mt-1 truncate">
                {attr.message}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
