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
  Legend,
  CartesianGrid,
} from 'recharts';
import { LineChart as ChartIcon } from 'lucide-react';

export function TimeSeriesChart() {
  const { telemetryHistory } = useTelemetryStore();

  const chartData = useMemo(() => {
    return telemetryHistory.map((pt) => {
      const d = new Date(pt.timestamp);
      return {
        time: `${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`,
        temperature: pt.temperature_c,
        humidity: pt.humidity_pct,
        pressure: pt.pressure_hpa,
      };
    });
  }, [telemetryHistory]);

  return (
    <div className="glass-panel rounded-2xl p-4 border border-white/10 flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <ChartIcon className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Real-Time Multivariate Telemetry Stream (60s Window)
          </h3>
        </div>
        <div className="text-[10px] font-mono text-slate-400">
          Window: <strong>{telemetryHistory.length}</strong> timesteps
        </div>
      </div>

      <div className="w-full h-48">
        {chartData.length < 2 ? (
          <div className="w-full h-full flex items-center justify-center text-xs font-mono text-slate-500">
            Buffering 1 Hz telemetry packets...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
              <XAxis
                dataKey="time"
                stroke="#64748b"
                tick={{ fontSize: 10, fontFamily: 'monospace' }}
                interval="preserveStartEnd"
              />
              <YAxis
                yAxisId="temp_rh"
                domain={[0, 100]}
                stroke="#64748b"
                tick={{ fontSize: 10, fontFamily: 'monospace' }}
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
                labelStyle={{ color: '#94a3b8', fontWeight: 'bold' }}
              />
              <Legend
                wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace', paddingTop: '6px' }}
              />
              <Line
                yAxisId="temp_rh"
                type="monotone"
                dataKey="temperature"
                name="Temp (°C)"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                yAxisId="temp_rh"
                type="monotone"
                dataKey="humidity"
                name="Humidity (%)"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
