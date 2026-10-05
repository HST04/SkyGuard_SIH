'use client';

import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { ContactShadows, Grid, Sparkles } from '@react-three/drei';
import { StationModel } from './StationModel';
import { CameraController } from './CameraController';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { RotateCcw, Crosshair, Maximize2, Minimize2 } from 'lucide-react';

interface WeatherStation3DProps {
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export function WeatherStation3D({ isExpanded, onToggleExpand }: WeatherStation3DProps) {
  const { stationStatus, selectedSensor, setSelectedSensor, anomalies, latestTelemetry } = useTelemetryStore();
  const isStandby = !latestTelemetry;

  const openAnomalies = anomalies.filter((a) => a.status === 'open');

  return (
    <div
      className="relative w-full h-full canvas-container select-none overflow-hidden"
      style={{ height: '100%', width: '100%' }}
    >
      {/* Top Left Floating Station HUD */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 pointer-events-none">
        <div className="glass-panel px-3.5 py-2 rounded-xl flex items-center gap-3 pointer-events-auto border border-white/10 shadow-glass">
          <div
            className={`w-3 h-3 rounded-full flex-shrink-0 ${
              stationStatus === 'anomaly'
                ? 'bg-rose-500 shadow-glow-rose animate-ping'
                : stationStatus === 'warning'
                ? 'bg-amber-400 shadow-glow-amber animate-pulse'
                : isStandby
                ? 'bg-amber-400 shadow-glow-amber animate-pulse'
                : 'bg-emerald-400 shadow-glow-emerald'
            }`}
          />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-slate-200">
                AGRA-01 DIGITAL TWIN
              </span>
              <span
                className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                  stationStatus === 'anomaly'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    : stationStatus === 'warning'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : isStandby
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                }`}
              >
                {isStandby ? 'STANDBY' : stationStatus.toUpperCase()}
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono">
              27.1767° N, 78.0081° E • 169m MSL
            </div>
          </div>
        </div>

        {/* Active Target Banner */}
        {selectedSensor !== 'station' && (
          <div className="glass-panel px-3 py-1.5 rounded-lg flex items-center gap-2 pointer-events-auto border border-cyan-500/30 text-cyan-300 text-xs font-mono">
            <Crosshair className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
            <span>Target Focused: <strong className="capitalize">{selectedSensor}</strong></span>
            <button
              onClick={() => setSelectedSensor('station')}
              className="ml-2 hover:text-white underline text-[10px]"
            >
              Reset View
            </button>
          </div>
        )}
      </div>

      {/* Top Right Controls Overlay: Overview Reset & Expand Toggle */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
        <button
          onClick={() => setSelectedSensor('station')}
          className="glass-panel-interactive px-3 py-2 rounded-xl text-xs font-mono text-slate-300 flex items-center gap-1.5 border border-white/10"
          title="Reset Camera Overview"
        >
          <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Overview</span>
        </button>

        {onToggleExpand && (
          <button
            onClick={onToggleExpand}
            className="glass-panel-interactive px-3 py-2 rounded-xl text-xs font-mono text-slate-300 flex items-center gap-1.5 border border-white/10"
            title={isExpanded ? "Collapse to standard view" : "Maximize 3D viewport"}
          >
            {isExpanded ? (
              <>
                <Minimize2 className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">Split View</span>
              </>
            ) : (
              <>
                <Maximize2 className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">Maximize 3D</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Bottom Center Sensor Quick-Target Buttons */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1.5 glass-panel px-3 py-1.5 rounded-xl border border-white/10 shadow-glass">
        <span className="text-[10px] font-mono text-cyan-400 font-semibold uppercase tracking-wider mr-1 hidden sm:inline">
          Inspect Sensor:
        </span>
        {[
          { id: 'temperature', label: 'Temp (T)' },
          { id: 'humidity', label: 'Humidity (RH)' },
          { id: 'pressure', label: 'Barometer (P)' },
        ].map((sensor) => {
          const isTargeted = selectedSensor === sensor.id;
          const isCulprit = openAnomalies.some((a) => a.culprit_sensors.includes(sensor.id));

          return (
            <button
              key={sensor.id}
              onClick={() => setSelectedSensor(sensor.id)}
              className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium transition-all ${
                isCulprit
                  ? 'bg-rose-600/30 text-rose-200 border border-rose-500/60 shadow-glow-rose'
                  : isTargeted
                  ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/50 shadow-glow-cyan'
                  : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-transparent'
              }`}
            >
              {sensor.label}
              {isCulprit && <span className="ml-1 w-1.5 h-1.5 rounded-full bg-rose-400 inline-block animate-ping" />}
            </button>
          );
        })}
      </div>

      {/* R3F 3D Canvas with tuned camera framing to fill viewport height */}
      <Canvas
        className="w-full h-full"
        style={{ width: '100%', height: '100%', display: 'block' }}
        camera={{ position: [3.2, 2.6, 3.8], fov: 45 }}
        shadows
        gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
      >
        <color attach="background" args={['#080c14']} />
        <fog attach="fog" args={['#080c14', 10, 26]} />

        {/* Atmospheric Lighting */}
        <ambientLight intensity={0.75} color="#94a3b8" />
        <directionalLight
          position={[8, 14, 6]}
          intensity={2.4}
          castShadow
          shadow-mapSize-width={1024}
          shadow-mapSize-height={1024}
          shadow-camera-far={25}
          shadow-camera-left={-5}
          shadow-camera-right={5}
          shadow-camera-top={5}
          shadow-camera-bottom={-5}
        />
        {/* Cyan Cyber Accent Rim Light */}
        <directionalLight position={[-8, 6, -6]} intensity={1.3} color="#06b6d4" />
        {/* Soft Violet Back Light */}
        <pointLight position={[0, 5, -5]} intensity={1.0} color="#8b5cf6" distance={15} />

        <Suspense fallback={null}>
          <StationModel />

          {/* Interactive Camera Controller */}
          <CameraController />

          {/* Ground Cyber Grid & Contact Shadows */}
          <Grid
            position={[0, 0, 0]}
            args={[20, 20]}
            cellSize={0.5}
            cellThickness={0.6}
            cellColor="#1e293b"
            sectionSize={2.0}
            sectionThickness={1.2}
            sectionColor="#0ea5e9"
            fadeDistance={18}
            fadeStrength={1.5}
          />
          <ContactShadows
            position={[0, 0.01, 0]}
            opacity={0.8}
            scale={10}
            blur={2.5}
            far={4}
          />

          {/* Subtle Atmospheric Dust / Solar Particles */}
          <Sparkles
            count={45}
            scale={8}
            size={1.5}
            speed={0.4}
            opacity={0.35}
            color="#38bdf8"
          />
        </Suspense>
      </Canvas>
    </div>
  );
}