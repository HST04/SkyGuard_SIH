'use client';

import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { SensorNode } from './SensorNode';
import { useTelemetryStore } from '@/stores/telemetryStore';

export function StationModel() {
  const { latestTelemetry } = useTelemetryStore();
  const anemometerRef = useRef<THREE.Group>(null);
  const windVaneRef = useRef<THREE.Group>(null);

  // Rotate anemometer cups based on simulated wind speed
  useFrame((_, delta) => {
    if (anemometerRef.current) {
      const speed = latestTelemetry ? latestTelemetry.wind_speed_ms : 3.0;
      anemometerRef.current.rotation.y += delta * (speed * 1.8);
    }

    if (windVaneRef.current && latestTelemetry) {
      const targetRad = (latestTelemetry.wind_dir_deg * Math.PI) / 180;
      // Gentle smoothing towards target direction
      windVaneRef.current.rotation.y = THREE.MathUtils.lerp(
        windVaneRef.current.rotation.y,
        targetRad,
        delta * 2.0
      );
    }
  });

  const tempVal = latestTelemetry ? `${latestTelemetry.temperature_c.toFixed(1)}` : '--';
  const rhVal = latestTelemetry ? `${latestTelemetry.humidity_pct.toFixed(1)}` : '--';
  const pressVal = latestTelemetry ? `${latestTelemetry.pressure_hpa.toFixed(1)}` : '--';
  const windVal = latestTelemetry ? `${latestTelemetry.wind_speed_ms.toFixed(1)}` : '--';
  const solarVal = latestTelemetry ? `${latestTelemetry.solar_radiation_wm2.toFixed(0)}` : '--';

  return (
    <group position={[0, 0, 0]} scale={[1.2, 1.2, 1.2]}>
      {/* 1. Base Foundation: Concrete Pad */}
      <mesh position={[0, 0.05, 0]} receiveShadow>
        <cylinderGeometry args={[1.2, 1.3, 0.1, 8]} />
        <meshStandardMaterial color="#1e293b" roughness={0.9} metalness={0.1} />
      </mesh>

      {/* Base Tripod Struts */}
      {[0, 120, 240].map((angle, idx) => (
        <group key={`strut-${idx}`} rotation={[0, (angle * Math.PI) / 180, 0]}>
          <mesh position={[0.45, 0.45, 0]} rotation={[0, 0, -Math.PI / 4]}>
            <cylinderGeometry args={[0.025, 0.025, 1.1, 8]} />
            <meshStandardMaterial color="#475569" metalness={0.8} roughness={0.3} />
          </mesh>
        </group>
      ))}

      {/* 2. Main Vertical Aluminum Mast (height 4.0m) */}
      <mesh position={[0, 2.0, 0]} castShadow>
        <cylinderGeometry args={[0.05, 0.05, 4.0, 16]} />
        <meshStandardMaterial color="#64748b" metalness={0.85} roughness={0.25} />
      </mesh>

      {/* Mast Guy-Wire Collars */}
      <mesh position={[0, 2.8, 0]}>
        <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        <meshStandardMaterial color="#334155" metalness={0.9} roughness={0.2} />
      </mesh>

      {/* 3. Barometer & Data Logger Enclosure (Mounted at 1.2m) */}
      <SensorNode
        id="pressure"
        label="Barometric Sensor (P)"
        position={[0, 1.25, 0.3]}
        readingValue={pressVal}
        unit="hPa"
      >
        <group>
          {/* Mounting Bracket */}
          <mesh position={[0, 0, -0.15]}>
            <boxGeometry args={[0.08, 0.06, 0.2]} />
            <meshStandardMaterial color="#475569" metalness={0.7} roughness={0.3} />
          </mesh>
          {/* Weatherproof IP67 Enclosure Box */}
          <mesh castShadow receiveShadow>
            <boxGeometry args={[0.32, 0.4, 0.2]} />
            <meshStandardMaterial color="#cbd5e1" metalness={0.3} roughness={0.4} />
          </mesh>
          {/* Pressure Vent / Transducer Port */}
          <mesh position={[0, -0.22, 0]}>
            <cylinderGeometry args={[0.03, 0.03, 0.06, 12]} />
            <meshStandardMaterial color="#334155" metalness={0.9} roughness={0.2} />
          </mesh>
          {/* Status Label on Box */}
          <mesh position={[0, 0.08, 0.101]}>
            <planeGeometry args={[0.22, 0.08]} />
            <meshStandardMaterial color="#0f172a" roughness={0.5} />
          </mesh>
        </group>
      </SensorNode>

      {/* 4. Temperature Sensor: Stevenson Solar Radiation Shield (Mounted at 2.2m) */}
      <SensorNode
        id="temperature"
        label="Ambient Temperature (T)"
        position={[0.55, 2.2, 0]}
        readingValue={tempVal}
        unit="°C"
      >
        <group>
          {/* Crossarm Arm to Mast */}
          <mesh position={[-0.28, 0, 0]}>
            <boxGeometry args={[0.55, 0.03, 0.03]} />
            <meshStandardMaterial color="#64748b" metalness={0.8} roughness={0.3} />
          </mesh>
          {/* Multi-plate Louvered Radiation Shield (Stacked Discs) */}
          {[...Array(6)].map((_, i) => (
            <mesh key={`plate-${i}`} position={[0, -0.12 + i * 0.05, 0]} castShadow>
              <cylinderGeometry args={[0.13 - i * 0.005, 0.14 - i * 0.005, 0.02, 16]} />
              <meshStandardMaterial color="#ffffff" roughness={0.2} metalness={0.1} />
            </mesh>
          ))}
          {/* Internal PT100 Platinum RTD Sensor Tip */}
          <mesh position={[0, 0, 0]}>
            <cylinderGeometry args={[0.015, 0.015, 0.22, 8]} />
            <meshStandardMaterial color="#38bdf8" metalness={0.9} roughness={0.1} />
          </mesh>
        </group>
      </SensorNode>

      {/* 5. Humidity Sensor: Shielded Capacitive Hygrometer (Mounted at 2.0m opposite side) */}
      <SensorNode
        id="humidity"
        label="Relative Humidity (RH)"
        position={[0.55, 1.9, 0.2]}
        readingValue={rhVal}
        unit="%"
      >
        <group>
          {/* Extension Mount */}
          <mesh position={[-0.25, 0, -0.1]}>
            <boxGeometry args={[0.5, 0.025, 0.025]} />
            <meshStandardMaterial color="#64748b" metalness={0.8} roughness={0.3} />
          </mesh>
          {/* Sintered Filter Shield */}
          <mesh position={[0, 0, 0]} castShadow>
            <cylinderGeometry args={[0.055, 0.055, 0.2, 16]} />
            <meshStandardMaterial color="#e2e8f0" metalness={0.5} roughness={0.3} />
          </mesh>
          {/* Mesh Filter tip */}
          <mesh position={[0, -0.11, 0]}>
            <sphereGeometry args={[0.052, 12, 12]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.6} roughness={0.4} wireframe />
          </mesh>
        </group>
      </SensorNode>

      {/* 6. Solar Panel & Power System (Mounted at 2.6m, angled) */}
      <SensorNode
        id="solar"
        label="Photovoltaic System (Solar)"
        position={[-0.55, 2.6, 0]}
        readingValue={solarVal}
        unit="W/m²"
      >
        <group rotation={[0.4, 0, 0.5]}>
          {/* Solar Bracket */}
          <mesh position={[0.25, -0.15, 0]}>
            <cylinderGeometry args={[0.02, 0.02, 0.4, 8]} />
            <meshStandardMaterial color="#475569" metalness={0.8} roughness={0.3} />
          </mesh>
          {/* Solar Frame */}
          <mesh castShadow>
            <boxGeometry args={[0.45, 0.65, 0.03]} />
            <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.3} />
          </mesh>
          {/* Blue PV Silicon Cells */}
          <mesh position={[0, 0, 0.018]}>
            <boxGeometry args={[0.41, 0.61, 0.01]} />
            <meshStandardMaterial color="#1e3a8a" roughness={0.1} metalness={0.9} />
          </mesh>
        </group>
      </SensorNode>

      {/* 7. Top Crossarm & Wind Suite (Mounted at 3.9m) */}
      <SensorNode
        id="wind"
        label="Wind Suite (Speed & Dir)"
        position={[0, 4.1, 0]}
        readingValue={windVal}
        unit="m/s"
      >
        <group>
          {/* Horizontal Crossarm */}
          <mesh position={[0, -0.15, 0]}>
            <cylinderGeometry args={[0.025, 0.025, 0.8, 12]} />
            <meshStandardMaterial color="#64748b" metalness={0.85} roughness={0.2} />
          </mesh>

          {/* Anemometer Station (Left Side) */}
          <group position={[-0.35, -0.05, 0]}>
            <mesh position={[0, -0.08, 0]}>
              <cylinderGeometry args={[0.02, 0.025, 0.16, 8]} />
              <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.3} />
            </mesh>
            {/* Rotating 3-cup assembly */}
            <group ref={anemometerRef} position={[0, 0.03, 0]}>
              <mesh>
                <cylinderGeometry args={[0.03, 0.03, 0.04, 12]} />
                <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.2} />
              </mesh>
              {[0, 120, 240].map((cupAngle, i) => (
                <group key={`cup-${i}`} rotation={[0, (cupAngle * Math.PI) / 180, 0]}>
                  <mesh position={[0.08, 0, 0]}>
                    <boxGeometry args={[0.14, 0.01, 0.01]} />
                    <meshStandardMaterial color="#475569" metalness={0.8} />
                  </mesh>
                  <mesh position={[0.15, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
                    <sphereGeometry args={[0.035, 12, 12, 0, Math.PI]} />
                    <meshStandardMaterial color="#0284c7" metalness={0.6} roughness={0.3} side={THREE.DoubleSide} />
                  </mesh>
                </group>
              ))}
            </group>
          </group>

          {/* Wind Vane Station (Right Side) */}
          <group position={[0.35, -0.05, 0]}>
            <mesh position={[0, -0.08, 0]}>
              <cylinderGeometry args={[0.02, 0.025, 0.16, 8]} />
              <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.3} />
            </mesh>
            {/* Rotating Wind Vane Fin */}
            <group ref={windVaneRef} position={[0, 0.04, 0]}>
              <mesh position={[0, 0, 0]}>
                <cylinderGeometry args={[0.025, 0.025, 0.04, 12]} />
                <meshStandardMaterial color="#1e293b" metalness={0.8} />
              </mesh>
              {/* Vane Shaft */}
              <mesh position={[0, 0, 0.02]}>
                <boxGeometry args={[0.01, 0.015, 0.28]} />
                <meshStandardMaterial color="#475569" metalness={0.8} />
              </mesh>
              {/* Vane Tail Fin */}
              <mesh position={[0, 0.04, 0.14]} rotation={[0, 0, 0]}>
                <boxGeometry args={[0.005, 0.09, 0.12]} />
                <meshStandardMaterial color="#0284c7" metalness={0.6} roughness={0.3} />
              </mesh>
              {/* Counterweight Pointer */}
              <mesh position={[0, 0, -0.12]} rotation={[Math.PI / 2, 0, 0]}>
                <coneGeometry args={[0.02, 0.06, 8]} />
                <meshStandardMaterial color="#f59e0b" metalness={0.8} roughness={0.2} />
              </mesh>
            </group>
          </group>
        </group>
      </SensorNode>

      {/* 8. Lightning Rod at Mast Pinnacle */}
      <mesh position={[0, 4.3, 0]}>
        <cylinderGeometry args={[0.005, 0.02, 0.6, 8]} />
        <meshStandardMaterial color="#e2e8f0" metalness={0.95} roughness={0.1} />
      </mesh>
    </group>
  );
}
