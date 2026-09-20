'use client';

import React from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { Thermometer, Droplets, Gauge, Wind, Sun, CloudRain } from 'lucide-react';

export function TelemetryPanel() {
  const { latestTelemetry, telemetryHistory, selectedSensor, setSelectedSensor, anomalies } = useTelemetryStore();

  const openAnomalies = anomalies.filter((a) => a.status === 'open');

  // Compute 5-second rate of change
  const prev5 = telemetryHistory.length >= 6 ? telemetryHistory[telemetryHistory.length - 6] : null;

  const tempDelta = latestTelemetry && prev5 ? (latestTelemetry.temperature_c - prev5.temperature_c).toFixed(2) : '0.00';
  const rhDelta = latestTelemetry && prev5 ? (latestTelemetry.humidity_pct - prev5.humidity_pct).toFixed(1) : '0.0';
  const pressDelta = latestTelemetry && prev5 ? (latestTelemetry.pressure_hpa - prev5.pressure_hpa).toFixed(2) : '0.00';

  const metrics = [
    {
      id: 'temperature',
      label: 'Ambient Temperature',
      shortLabel: 'T',
      value: latestTelemetry ? latestTelemetry.temperature_c.toFixed(1) : '--',
      unit: '°C',
      delta: `${Number(tempDelta) >= 0 ? '+' : ''}${tempDelta} °C/5s`,
      icon: Thermometer,
      accent: 'cyan',
      nominal: '25.0 – 42.0 °C',
    },
    {
      id: 'humidity',
      label: 'Relative Humidity',
      shortLabel: 'RH',
      value: latestTelemetry ? latestTelemetry.humidity_pct.toFixed(1) : '--',
      unit: '%',
      delta: `${Number(rhDelta) >= 0 ? '+' : ''}${rhDelta} %/5s`,
      icon: Droplets,
      accent: 'emerald',
      nominal: '30.0 – 85.0 %',
    },
    {
      id: 'pressure',
      label: 'Atmospheric Pressure',
      shortLabel: 'P',
      value: latestTelemetry ? latestTelemetry.pressure_hpa.toFixed(1) : '--',
      unit: 'hPa',
      delta: `${Number(pressDelta) >= 0 ? '+' : ''}${pressDelta} hPa/5s`,
      icon: Gauge,
      accent: 'indigo',
      nominal: '995.0 – 1015.0 hPa',
    },
    {
      id: 'dew_point',
      label: 'Calculated Dew Point',
      shortLabel: 'Td',
      value: latestTelemetry ? latestTelemetry.dew_point_c.toFixed(1) : '--',
      unit: '°C',
      delta: 'Magnus Eq.',
      icon: CloudRain,
      accent: 'blue',
      nominal: 'Td ≤ T + 0.5',
    },
    {
      id: 'wind',
      label: 'Wind Suite',
      shortLabel: 'Wind',
      value: latestTelemetry ? `${latestTelemetry.wind_speed_ms.toFixed(1)}` : '--',
      unit: 'm/s',
      delta: latestTelemetry ? `${latestTelemetry.wind_dir_deg.toFixed(0)}° Dir` : '--',
      icon: Wind,
      accent: 'teal',
      nominal: '0.5 – 18.0 m/s',
    },
    {
      id: 'solar',
      label: 'Solar Insolation',
      shortLabel: 'Solar',
      value: latestTelemetry ? latestTelemetry.solar_radiation_wm2.toFixed(0) : '--',
      unit: 'W/m²',
      delta: 'Diurnal Peak',
      icon: Sun,
      accent: 'amber',
      nominal: '0 – 950 W/m²',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        const isSelected = selectedSensor === metric.id;
        const isCulprit = openAnomalies.some((a) => a.culprit_sensors && a.culprit_sensors.includes(metric.id));

        return (
          <div
            key={metric.id}
            onClick={() => setSelectedSensor(metric.id === selectedSensor ? 'station' : metric.id)}
            className={`cursor-pointer rounded-xl p-3 border transition-all ${
              isCulprit
                ? 'bg-rose-950/40 border-rose-500/60 shadow-glow-rose'
                : isSelected
                ? 'bg-cyan-950/40 border-cyan-500/60 shadow-glow-cyan'
                : 'glass-panel-interactive border-white/10'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-1.5">
                <Icon
                  className={`w-4 h-4 ${
                    isCulprit ? 'text-rose-400 animate-pulse' : isSelected ? 'text-cyan-400' : 'text-slate-400'
                  }`}
                />
                <span className="text-xs font-mono font-medium text-slate-300 truncate">
                  {metric.label}
                </span>
              </div>
              {isCulprit ? (
                <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-rose-500/30 text-rose-300 font-bold border border-rose-500/40">
                  FLAGGED
                </span>
              ) : (
                <span className="text-[10px] font-mono text-slate-500">{metric.shortLabel}</span>
              )}
            </div>

            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-mono font-bold text-white tracking-tight">
                {metric.value}
              </span>
              <span className="text-xs font-mono text-slate-400 font-medium">{metric.unit}</span>
            </div>

            <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5 text-[10px] font-mono">
              <span className="text-slate-400">{metric.delta}</span>
              <span className="text-slate-500">{metric.nominal}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
