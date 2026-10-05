'use client';

import { useRef, useEffect } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { useTelemetryStore, normalizeSensorId } from '@/stores/telemetryStore';

interface CameraTarget {
  position: THREE.Vector3;
  target: THREE.Vector3;
}

// Tuned camera positions to frame the entire station filling the viewport
const TARGETS: Record<string, CameraTarget> = {
  station: {
    position: new THREE.Vector3(3.2, 2.6, 3.8),
    target: new THREE.Vector3(0, 2.2, 0),
  },
  temperature: {
    position: new THREE.Vector3(1.2, 2.4, 0.9),
    target: new THREE.Vector3(0.55, 2.2, 0),
  },
  humidity: {
    position: new THREE.Vector3(1.1, 2.0, 1.0),
    target: new THREE.Vector3(0.55, 1.9, 0.2),
  },
  pressure: {
    position: new THREE.Vector3(0.8, 1.4, 0.9),
    target: new THREE.Vector3(0, 1.25, 0.3),
  },
  wind: {
    position: new THREE.Vector3(1.1, 4.3, 1.2),
    target: new THREE.Vector3(0, 4.1, 0),
  },
  solar: {
    position: new THREE.Vector3(-1.3, 2.8, 1.2),
    target: new THREE.Vector3(-0.55, 2.6, 0),
  },
};

export function CameraController() {
  const { selectedSensor } = useTelemetryStore();
  const controlsRef = useRef<OrbitControlsImpl>(null);
  const { camera } = useThree();

  const isTransitioning = useRef(false);
  const targetCamPos = useRef(new THREE.Vector3().copy(TARGETS.station.position));
  const targetLookAt = useRef(new THREE.Vector3().copy(TARGETS.station.target));

  useEffect(() => {
    const normKey = normalizeSensorId(selectedSensor);
    const config = TARGETS[normKey] || TARGETS.station;
    targetCamPos.current.copy(config.position);
    targetLookAt.current.copy(config.target);
    isTransitioning.current = true;
  }, [selectedSensor]);

  useFrame((_, delta) => {
    if (isTransitioning.current && controlsRef.current) {
      const lerpSpeed = Math.min(1.0, delta * 4.0);
      camera.position.lerp(targetCamPos.current, lerpSpeed);
      controlsRef.current.target.lerp(targetLookAt.current, lerpSpeed);
      controlsRef.current.update();

      if (
        camera.position.distanceTo(targetCamPos.current) < 0.05 &&
        controlsRef.current.target.distanceTo(targetLookAt.current) < 0.05
      ) {
        isTransitioning.current = false;
      }
    }
  });

  return (
    <OrbitControls
      ref={controlsRef}
      target={[0, 2.1, 0]}
      makeDefault
      enableDamping
      dampingFactor={0.06}
      minDistance={0.8}
      maxDistance={8.0}
      maxPolarAngle={Math.PI / 2 + 0.05} // Don't clip below ground
    />
  );
}
