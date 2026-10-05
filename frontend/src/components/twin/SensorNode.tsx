'use client';

import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { useTelemetryStore, normalizeSensorId, matchSensor } from '@/stores/telemetryStore';

interface SensorNodeProps {
  id: string;
  label: string;
  position: [number, number, number];
  children: React.ReactNode;
  readingValue?: string;
  unit?: string;
}

export function SensorNode({ id, label, position, children, readingValue, unit }: SensorNodeProps) {
  const {
    selectedSensor,
    setSelectedSensor,
    anomalies,
    activeAnomaly,
    confluence,
    activeFault,
    imputation,
  } = useTelemetryStore();

  const [hovered, setHovered] = useState(false);
  const glowMeshRef = useRef<THREE.Mesh>(null);
  const shockwaveRef = useRef<THREE.Mesh>(null);
  const pulseCageRef = useRef<THREE.Mesh>(null);

  const normId = normalizeSensorId(id);
  const isSelected = normalizeSensorId(selectedSensor) === normId;

  // Requirement 2: Assumes all sensors OK once sensor defect is logged (acknowledged, resolved, or ignored)
  const hasOpenAnomalyOnThisSensor = anomalies.some(
    (a) =>
      a.status === 'open' &&
      a.culprit_sensors &&
      a.culprit_sensors.some((c) => matchSensor(c, normId))
  );

  const isActiveAnomalyOnThisSensor = Boolean(
    activeAnomaly &&
      activeAnomaly.status === 'open' &&
      activeAnomaly.culprit_sensors &&
      activeAnomaly.culprit_sensors.some((c) => matchSensor(c, normId))
  );

  const hasOpenDefectsOverall = anomalies.some(
    (a) => a.status === 'open' && a.classification === 'Sensor Defect'
  );

  const isCulprit =
    hasOpenAnomalyOnThisSensor ||
    isActiveAnomalyOnThisSensor ||
    (hasOpenDefectsOverall &&
      confluence?.classification === 'Sensor Defect' &&
      (matchSensor(confluence.defect_class || '', normId) ||
        matchSensor(confluence.defect_type || '', normId) ||
        matchSensor(activeFault || '', normId))) ||
    (hasOpenDefectsOverall && Boolean(imputation?.active && matchSensor(imputation.sensor || '', normId)));

  // Animate pulse glow and shockwave
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (glowMeshRef.current) {
      if (isCulprit) {
        const pulse = Math.sin(t * 8) * 0.35 + 0.65;
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = pulse * 0.75;
      } else if (isSelected) {
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = 0.35;
      } else if (hovered) {
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = 0.2;
      } else {
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = 0.0;
      }
    }

    if (shockwaveRef.current) {
      if (isCulprit) {
        const wave = (t * 1.6) % 1.0;
        shockwaveRef.current.scale.set(1 + wave * 0.9, 1 + wave * 0.9, 1);
        (shockwaveRef.current.material as THREE.MeshBasicMaterial).opacity = (1 - wave) * 0.65;
      } else {
        (shockwaveRef.current.material as THREE.MeshBasicMaterial).opacity = 0.0;
      }
    }

    if (pulseCageRef.current) {
      if (isCulprit) {
        const pulse = Math.sin(t * 6) * 0.25 + 0.55;
        (pulseCageRef.current.material as THREE.MeshBasicMaterial).opacity = pulse * 0.5;
      } else {
        (pulseCageRef.current.material as THREE.MeshBasicMaterial).opacity = 0.0;
      }
    }
  });

  const glowColor = isCulprit ? '#f43f5e' : isSelected ? '#06b6d4' : '#10b981';

  return (
    <group position={position}>
      {/* Invisible bounding interaction sphere for easy clicking */}
      <mesh
        onClick={(e) => {
          e.stopPropagation();
          setSelectedSensor(normId);
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = 'auto';
        }}
      >
        <sphereGeometry args={[0.45, 16, 16]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>

      {/* Cyber Targeting Ring */}
      <mesh ref={glowMeshRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <ringGeometry args={[0.25, 0.35, 32]} />
        <meshBasicMaterial
          color={glowColor}
          transparent
          opacity={0}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Expanding Shockwave Wave for Defected Sensor */}
      <mesh ref={shockwaveRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.04, 0]}>
        <ringGeometry args={[0.35, 0.40, 32]} />
        <meshBasicMaterial
          color="#f43f5e"
          transparent
          opacity={0}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Holographic Wireframe Cage for Defected Component */}
      <mesh ref={pulseCageRef} position={[0, 0.05, 0]}>
        <cylinderGeometry args={[0.22, 0.22, 0.45, 12]} />
        <meshBasicMaterial
          color="#f43f5e"
          wireframe
          transparent
          opacity={0}
          depthWrite={false}
        />
      </mesh>

      {/* Actual 3D Geometry */}
      {children}

      {/* High-Intensity Status Beacon & Point Light */}
      <mesh position={[0, 0.35, 0]}>
        <sphereGeometry args={[isCulprit ? 0.065 : 0.04, 16, 16]} />
        <meshStandardMaterial
          color={glowColor}
          emissive={glowColor}
          emissiveIntensity={isCulprit ? 8.0 : isSelected ? 3.0 : 1.5}
        />
      </mesh>
      {isCulprit && <pointLight color="#f43f5e" intensity={3.5} distance={1.8} />}

      {/* Interactive Tooltip / Defect HUD */}
      {(hovered || isSelected || isCulprit) && (
        <Html
          position={[0, isCulprit ? 0.65 : 0.55, 0]}
          center
          distanceFactor={6}
          style={{
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
            transform: 'translate3d(0, 0, 0)',
          }}
        >
          <div
            className={`px-3 py-1.5 rounded-xl text-xs font-mono border backdrop-blur-md shadow-2xl transition-all ${
              isCulprit
                ? 'bg-rose-950/95 border-rose-500 text-rose-100 shadow-rose-900/60 animate-bounce'
                : isSelected
                ? 'bg-cyan-950/85 border-cyan-500/60 text-cyan-200 shadow-cyan-900/40'
                : 'bg-slate-900/85 border-slate-700 text-slate-200'
            }`}
          >
            <div className="flex items-center gap-1.5 font-bold">
              <span
                className={`w-2 h-2 rounded-full ${
                  isCulprit ? 'bg-rose-400 animate-ping' : isSelected ? 'bg-cyan-400' : 'bg-emerald-400'
                }`}
              />
              <span className={isCulprit ? 'text-rose-300 font-extrabold' : ''}>{label}</span>
            </div>
            {readingValue && (
              <div className="text-[11px] text-slate-300 mt-0.5">
                {readingValue} <span className="text-slate-400">{unit}</span>
              </div>
            )}
            {isCulprit && (
              <div className="text-[10px] text-rose-300 font-bold mt-1 tracking-wider uppercase flex items-center gap-1">
                <span>⚠ DEFECT DETECTED</span>
              </div>
            )}
          </div>
        </Html>
      )}
    </group>
  );
}
