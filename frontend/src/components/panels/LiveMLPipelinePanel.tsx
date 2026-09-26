'use client';

import React, { useMemo } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { Activity, Zap, AlertTriangle, ShieldCheck } from 'lucide-react';

const RECONSTRUCTION_THRESHOLD = 0.042;

export function LiveMLPipelinePanel() {
  const { telemetryHistory, latestTelemetry, stationStatus, activeAnomaly } = useTelemetryStore();

  const currentError = latestTelemetry?.reconstruction_error ?? (
    activeAnomaly ? activeAnomaly.reconstruction_error : 0.0142
  );
  const currentSpeed = latestTelemetry?.inference_time_ms ?? 2.4;
  const isAnomaly = currentError > RECONSTRUCTION_THRESHOLD || stationStatus === 'anomaly';

  const chartData = useMemo(() => {
    return telemetryHistory.map((pt, idx) => {
      const d = new Date(pt.timestamp);
      const timeStr = isNaN(d.getTime())
        ? `${idx}s`
        : `${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
      const mse = pt.reconstruction_error ?? (isAnomaly ? 0.051 : 0.0142);
      return {
        time: timeStr,
        mse: parseFloat(mse.toFixed(4)),
        threshold: RECONSTRUCTION_THRESHOLD,
      };
    });
  }, [telemetryHistory, isAnomaly]);

  return (
    <div
      className={`glass-panel rounded-2xl p-4 border transition-all duration-300 ${
        isAnomaly
          ? 'border-rose-500/40 bg-rose-950/20 shadow-glow-rose/20'
          : 'border-white/10 shadow-glass'
      }`}
    >
      {/* Header with Title and Status Pill */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className={`w-4 h-4 ${isAnomaly ? 'text-rose-400 animate-pulse' : 'text-emerald-400'}`} />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Live AI Error Meter (1D-CNN)
          </h3>
        </div>

        {/* Dynamic Status Pill */}
        {isAnomaly ? (
          <span className="flex items-center gap-1.5 text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-glow-rose animate-pulse">
            <AlertTriangle className="w-3 h-3 text-rose-400" />
            AI ALERT: DRIFT DETECTED
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-[10px] font-mono font-medium px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            AI STATUS: NOMINAL
          </span>
        )}
      </div>

      {/* Key Metrics Strip: Current Error Number & Inference Speed */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-3">
        {/* Metric 1: Current Reconstruction MSE */}
        <div className="p-2.5 rounded-xl bg-slate-900/60 border border-white/5 flex flex-col justify-between">
          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
            Reconstruction MSE
          </div>
          <div className="flex items-baseline gap-1.5 mt-0.5">
            <span
              className={`text-lg font-mono font-bold tracking-tight ${
                isAnomaly ? 'text-rose-400' : 'text-emerald-400'
              }`}
            >
              {currentError.toFixed(4)}
            </span>
            <span className="text-[10px] font-mono text-slate-500">
              / {RECONSTRUCTION_THRESHOLD.toFixed(3)}
            </span>
          </div>
        </div>

        {/* Metric 2: AI Inference Speed */}
        <div className="p-2.5 rounded-xl bg-slate-900/60 border border-white/5 flex flex-col justify-between">
          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Zap className="w-3 h-3 text-amber-400" />
            Inference Speed
          </div>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-lg font-mono font-bold text-cyan-300">
              {currentSpeed.toFixed(1)}
            </span>
            <span className="text-[10px] font-mono text-slate-400">ms / packet</span>
          </div>
        </div>

        {/* Metric 3: Model Architecture Info */}
        <div className="hidden sm:flex p-2.5 rounded-xl bg-slate-900/60 border border-white/5 flex-col justify-between">
          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
            Architecture
          </div>
          <div className="text-[11px] font-mono text-slate-300 font-semibold truncate mt-0.5">
            1D-CNN Autoencoder
          </div>
          <div className="text-[9px] font-mono text-slate-500">
            Latent Dim: 8 • ONNX Runtime
          </div>
        </div>
      </div>

      {/* Real-Time Line Chart (60s Window) */}
      <div className="w-full h-36">
        {chartData.length < 2 ? (
          <div className="w-full h-full flex items-center justify-center text-xs font-mono text-slate-500">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              Buffering 1 Hz AI inference stream...
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 8, right: 12, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
              <XAxis
                dataKey="time"
                stroke="#64748b"
                tick={{ fontSize: 9, fontFamily: 'monospace' }}
                interval="preserveStartEnd"
              />
              <YAxis
                domain={[0, (dataMax: number) => Math.max(0.065, Math.ceil((dataMax + 0.01) * 100) / 100)]}
                stroke="#64748b"
                tick={{ fontSize: 9, fontFamily: 'monospace' }}
                tickFormatter={(val) => val.toFixed(2)}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.92)',
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '0.75rem',
                  fontSize: '11px',
                  fontFamily: 'monospace',
                  backdropFilter: 'blur(8px)',
                }}
                formatter={(val: number) => [val.toFixed(4), 'MSE']}
                labelStyle={{ color: '#94a3b8', fontWeight: 'bold' }}
              />

              {/* Threshold Dashed Red Reference Line */}
              <ReferenceLine
                y={RECONSTRUCTION_THRESHOLD}
                stroke="#f43f5e"
                strokeDasharray="4 4"
                strokeWidth={1.5}
                label={{
                  value: 'Threshold: 0.042',
                  fill: '#f43f5e',
                  fontSize: 10,
                  fontFamily: 'monospace',
                  position: 'insideTopRight',
                  offset: 4,
                }}
              />

              {/* Live Reconstruction MSE Line */}
              <Line
                type="monotone"
                dataKey="mse"
                name="Reconstruction MSE"
                stroke={isAnomaly ? '#f43f5e' : '#10b981'}
                strokeWidth={2.2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Footer Legend Note */}
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5 text-[10px] font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-0.5 bg-emerald-400 inline-block" /> Normal (&lt; 0.042)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-0.5 bg-rose-500 inline-block" /> Drift Spikes
          </span>
        </div>
        <span className="text-slate-500">60s Rolling Window</span>
      </div>
    </div>
  );
}
