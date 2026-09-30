import asyncio
import math
import random
import time

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from config import settings
from data.store import store
from models.schemas import TelemetryPayload, PitchScriptStatus
from services.rule_engine import calculate_dew_point
from services.telemetry_ingestion import telemetry_ingestion

class EdgeTelemetrySimulator:
    def __init__(self):
        self.station_id = settings.STATION_ID
        self.sequence = 1000
        self.running = False
        self._task: Optional[asyncio.Task] = None

        # Base atmospheric state for AGRA-01 (aligned with regional profile and scaler baseline)
        self.sim_time_sec = 0
        self.base_temp = 30.0
        self.base_humidity = 62.5
        self.base_pressure = 1005.0
        self.base_wind = 3.2

        # 5-minute Pitch Script state
        self.pitch_script_active = False
        self.pitch_script_start_time = 0.0
        self.pitch_phase = "IDLE"

    def start(self):
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._simulation_loop())

    def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()

    def trigger_pitch_script(self):
        self.pitch_script_active = True
        self.pitch_script_start_time = time.time()
        self.pitch_phase = "BASELINE"
        store.set_fault("normal")

    def stop_pitch_script(self):
        self.pitch_script_active = False
        self.pitch_phase = "IDLE"
        store.set_fault("normal")

    def get_pitch_script_status(self) -> PitchScriptStatus:
        if not self.pitch_script_active:
            return PitchScriptStatus(
                active=False,
                phase_id="IDLE",
                phase_title="Standby Mode",
                phase_description="Simulator running normal diurnal telemetry. Pitch script ready.",
                elapsed_seconds=0,
                total_seconds=300,
                expected_status="Normal"
            )

        elapsed = int(time.time() - self.pitch_script_start_time)
        if elapsed < 90:  # 0:00 to 1:30
            return PitchScriptStatus(
                active=True,
                phase_id="BASELINE",
                phase_title="Phase 1: Diurnal Baseline (0:00 - 1:30)",
                phase_description="Normal diurnal solar cycle. 1D-CNN autoencoder reconstruction error is nominal. Station 3D twin remains Green.",
                elapsed_seconds=elapsed,
                total_seconds=300,
                expected_status="Normal (Green)"
            )
        elif elapsed < 180:  # 1:30 to 3:00
            return PitchScriptStatus(
                active=True,
                phase_id="TRUE_NEGATIVE_STORM",
                phase_title="Phase 2: Severe Thunderstorm True-Negative Test (1:30 - 3:00)",
                phase_description="Simulating sharp squall line: Pressure drops -12 hPa, Humidity surges to 92%, Temp drops -8°C. Multivariate correlations remain physically valid. System maintains Green (Zero False Alarm).",
                elapsed_seconds=elapsed,
                total_seconds=300,
                expected_status="Valid Weather (Green)"
            )
        elif elapsed < 225:  # 3:00 to 3:45
            return PitchScriptStatus(
                active=True,
                phase_id="CAPACITIVE_DRIFT",
                phase_title="Phase 3: Subtle Capacitive Drift Injected (3:00 - 3:45)",
                phase_description="Subtle +15% humidity bias injected while thermal profile remains warm. Static IMD limits fail to detect. 1D-CNN latent bottleneck accumulates reconstruction error.",
                elapsed_seconds=elapsed,
                total_seconds=300,
                expected_status="Degradation In Progress"
            )
        elif elapsed <= 300:  # 3:45 to 5:00
            return PitchScriptStatus(
                active=True,
                phase_id="ANOMALY_TRIGGERED",
                phase_title="Phase 4: AI Anomaly & SHAP Attribution (3:45 - 5:00)",
                phase_description="Autoencoder threshold breached! 3D Twin pulses Red, camera auto-focuses on Humidity shield, SHAP isolates culprit sensor. Operator can flag false alarm or acknowledge.",
                elapsed_seconds=min(300, elapsed),
                total_seconds=300,
                expected_status="Anomaly Detected (Red Pulse)"
            )
        else:
            self.pitch_script_active = False
            return self.get_pitch_script_status()

    async def _simulation_loop(self):
        """Main 1 Hz simulation tick."""
        while self.running:
            try:
                # If external script is posting telemetry, pause internal simulation ticks
                if store.is_external_telemetry_active(timeout_sec=4.0):
                    await asyncio.sleep(settings.SAMPLING_INTERVAL_SEC)
                    continue

                self.sim_time_sec += 1
                self.sequence += 1
                
                payload = self._generate_telemetry()
                
                await telemetry_ingestion.ingest(payload)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Simulator] Error in simulation tick: {e}")

            await asyncio.sleep(settings.SAMPLING_INTERVAL_SEC)

    def _generate_telemetry(self) -> TelemetryPayload:
        now_iso = datetime.now(timezone.utc).isoformat()
        t = self.sim_time_sec

        # Smooth diurnal cycle (24-hour cycle compressed into 600s for demo visibility)
        diurnal_cycle = math.sin((2 * math.pi * (t % 600)) / 600)

        # Baseline physics
        temp = self.base_temp + (diurnal_cycle * 4.0) + (random.uniform(-0.15, 0.15))
        # Relative humidity opposes temperature in nominal daytime conditions
        rh = self.base_humidity - (diurnal_cycle * 12.0) + (random.uniform(-0.4, 0.4))
        # Barometric pressure has semi-diurnal tides
        press = self.base_pressure + (math.cos((4 * math.pi * (t % 600)) / 600) * 1.5) + (random.uniform(-0.08, 0.08))
        wind = max(0.5, self.base_wind + (random.uniform(-0.3, 0.5)))
        wind_dir = (180.0 + (math.sin(t / 20.0) * 45.0)) % 360.0
        solar = max(0.0, 500.0 + (diurnal_cycle * 350.0) + random.uniform(-10, 10))

        active_fault = store.get_active_fault()
        intensity = store.get_fault_intensity()

        # Handle 5-Minute Pitch Script Timeline overrides
        if self.pitch_script_active:
            elapsed = time.time() - self.pitch_script_start_time
            if elapsed < 90:
                # Phase 1: Clean diurnal baseline
                pass
            elif elapsed < 180:
                # Phase 2: Natural Severe Thunderstorm (True Negative test)
                storm_progress = min(1.0, (elapsed - 90) / 45.0)
                temp -= (storm_progress * 8.5)
                press -= (storm_progress * 11.0)
                rh = min(98.0, rh + (storm_progress * 35.0))
                wind += (storm_progress * 8.0)
            elif elapsed < 225:
                # Phase 3: Subtle +15% humidity drift injected
                drift_progress = (elapsed - 180) / 45.0
                rh += (drift_progress * 16.0) # stays under 100% so rules pass, but CNN flags!
            elif elapsed <= 300:
                # Phase 4: Full drift active
                rh += 16.5
            else:
                self.pitch_script_active = False

        # Handle Manual Fault Injections
        if active_fault == "heat_spike":
            temp += (8.0 * intensity)
        elif active_fault == "pressure_drop":
            press -= (7.0 * intensity)
        elif active_fault == "stuck_humidity":
            rh = 100.0
        elif active_fault == "humidity_drift":
            # Subtle +15% drift: passes static 100% check, but violates multivariate manifold
            rh = min(96.0, rh + (16.0 * intensity))
        elif active_fault == "cross_decoupling":
            # Decouple temperature and humidity: RH jumps to 88% while Temp is 38°C with constant pressure
            temp = max(temp, 37.5)
            rh = 88.5
        elif active_fault == "sensor_noise":
            temp += random.uniform(-3.5, 3.5)
            rh += random.uniform(-15.0, 15.0)
            press += random.uniform(-4.0, 4.0)
        elif active_fault == "valid_squall":
            # Natural Severe Thunderstorm: Pressure drops, humidity surges, temp drops (True Negative test)
            temp -= (7.8 * intensity)
            press -= (10.5 * intensity)
            rh = min(96.0, rh + (32.0 * intensity))
            wind += (9.5 * intensity)

        # Sanitize reasonable limits for raw calculations
        td = calculate_dew_point(temp, rh)
        imd_passed = bool(
            -10.0 <= temp <= 60.0
            and 0.0 <= rh <= 100.0
            and 850.0 <= press <= 1080.0
            and td <= temp + 1.0
        )

        return TelemetryPayload(
            station_id=self.station_id,
            timestamp=now_iso,
            temperature_c=round(temp, 2),
            pressure_hpa=round(press, 2),
            humidity_pct=round(rh, 2),
            dew_point_c=td,
            wind_speed_ms=round(wind, 2),
            wind_dir_deg=round(wind_dir, 1),
            solar_radiation_wm2=round(solar, 1),
            sequence=self.sequence,
            source="edge-simulator",
            drop_flag=0,
            imd_passed=imd_passed
        )

simulator = EdgeTelemetrySimulator()
