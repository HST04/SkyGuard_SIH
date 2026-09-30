'use client';

import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { useTelemetryStore } from '@/stores/telemetryStore';

interface SensorNodeProps {
  id: string;
  label: string;
  position: [number, number, number];
  children: React.ReactNode;
  readingValue?: string;
  unit?: string;
}

export function SensorNode({ id, label, position, children, readingValue, unit }: SensorNodeProps) {
  const { selectedSensor, setSelectedSensor, anomalies } = useTelemetryStore();
  const [hovered, setHovered] = useState(false);
  const glowMeshRef = useRef<THREE.Mesh>(null);

  // Check if this sensor is a culprit in an active open anomaly
  const isCulprit = anomalies.some(
    (a) => a.status === 'open' && a.culprit_sensors && a.culprit_sensors.includes(id)
  );

  const isSelected = selectedSensor === id;

  // Animate pulse glow if culprit
  useFrame(({ clock }) => {
    if (glowMeshRef.current) {
      if (isCulprit) {
        const pulse = Math.sin(clock.getElapsedTime() * 7) * 0.35 + 0.65;
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = pulse * 0.55;
      } else if (isSelected) {
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = 0.25;
      } else if (hovered) {
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = 0.15;
      } else {
        (glowMeshRef.current.material as THREE.MeshBasicMaterial).opacity = 0.0;
      }
    }
  });

  const glowColor = isCulprit ? '#f43f5e' : (isSelected ? '#06b6d4' : '#10b981');

  return (
    <group position={position}>
      {/* Invisible bounding interaction sphere for easy clicking */}
      <mesh
        onClick={(e) => {
          e.stopPropagation();
          setSelectedSensor(id);
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

      {/* Sleek Cyber Targeting Ring */}
      <mesh ref={glowMeshRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <ringGeometry args={[0.25, 0.32, 32]} />
        <meshBasicMaterial
          color={glowColor}
          transparent
          opacity={0}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Actual 3D Geometry */}
      {children}

      {/* Status LED Beacon */}
      <mesh position={[0, 0.35, 0]}>
        <sphereGeometry args={[0.04, 12, 12]} />
        <meshStandardMaterial
          color={glowColor}
          emissive={glowColor}
          emissiveIntensity={isCulprit ? 4.0 : 1.5}
        />
      </mesh>

      {/* Interactive Tooltip HUD */}
      {(hovered || isSelected || isCulprit) && (
        <Html
          position={[0, 0.55, 0]}
          center
          distanceFactor={7}
          style={{
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
            transform: 'translate3d(0, 0, 0)',
          }}
        >
          <div
            className={`px-2.5 py-1.5 rounded-lg text-xs font-mono border backdrop-blur-md shadow-lg transition-all ${
              isCulprit
                ? 'bg-rose-950/80 border-rose-500/60 text-rose-200 shadow-rose-900/50'
                : isSelected
                ? 'bg-cyan-950/80 border-cyan-500/60 text-cyan-200 shadow-cyan-900/40'
                : 'bg-slate-900/80 border-slate-700 text-slate-200'
            }`}
          >
            <div className="flex items-center gap-1.5 font-bold">
              <span
                className={`w-2 h-2 rounded-full ${
                  isCulprit ? 'bg-rose-400 animate-ping' : isSelected ? 'bg-cyan-400' : 'bg-emerald-400'
                }`}
              />
              {label}
            </div>
            {readingValue && (
              <div className="text-[11px] text-slate-300 mt-0.5">
                {readingValue} <span className="text-slate-400">{unit}</span>
              </div>
            )}
            {isCulprit && (
              <div className="text-[10px] text-rose-300 font-semibold mt-0.5 tracking-wider">
                FAULT DETECTED
              </div>
            )}
          </div>
        </Html>
      )}
    </group>
  );
}
