"""Fault & Anomaly Injection Engine.
Maintains a rigorous, scientifically valid distinction between:
1. REAL WEATHER ANOMALIES (Multivariate, physically correlated shifts across multiple sensors)
2. SENSOR DEFECTS (Isolated, unphysical, or non-meteorological hardware/electrical failures)
"""

import copy
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional

from src.models.weather_physics import WeatherReading

class AnomalyType(Enum):
    NONE = "NORMAL"
    # Physical Weather Anomalies (Multi-sensor correlated)
    WEATHER_SEVERE_STORM = "WEATHER_ANOMALY:SEVERE_STORM"
    WEATHER_HEATWAVE = "WEATHER_ANOMALY:HEATWAVE"
    WEATHER_COLD_SNAP = "WEATHER_ANOMALY:COLD_SNAP"
    # Hardware Sensor Defects (Unphysical / Isolated)
    DEFECT_STUCK_SENSOR = "SENSOR_DEFECT:STUCK_TEMP"
    DEFECT_CALIBRATION_DRIFT = "SENSOR_DEFECT:CALIBRATION_DRIFT"
    DEFECT_ERRATIC_NOISE = "SENSOR_DEFECT:ERRATIC_NOISE"
    DEFECT_OUTLIER_SPIKE = "SENSOR_DEFECT:OUTLIER_SPIKE"
    DEFECT_PACKET_DROP_NULL = "SENSOR_DEFECT:NULL_READING"
    DEFECT_ADC_SATURATION = "SENSOR_DEFECT:ADC_SATURATION"

@dataclass
class InjectionState:
    weather_anomaly: AnomalyType = AnomalyType.NONE
    active_sensor_defects: List[AnomalyType] = field(default_factory=list)
    # Drift state tracking
    drift_accumulated_c: float = 0.0
    stuck_temp_value: Optional[float] = None
    spike_counter: int = 0

class FaultInjector:
    """Applies weather anomalies and/or sensor defects to baseline weather telemetry."""

    def __init__(self):
        self.state = InjectionState()

    def set_weather_anomaly(self, anomaly: AnomalyType):
        """Sets or clears the active atmospheric weather anomaly."""
        self.state.weather_anomaly = anomaly

    def toggle_defect(self, defect: AnomalyType):
        """Toggles a specific hardware sensor defect on or off."""
        if defect in self.state.active_sensor_defects:
            self.state.active_sensor_defects.remove(defect)
            if defect == AnomalyType.DEFECT_CALIBRATION_DRIFT:
                self.state.drift_accumulated_c = 0.0
            if defect == AnomalyType.DEFECT_STUCK_SENSOR:
                self.state.stuck_temp_value = None
        else:
            self.state.active_sensor_defects.append(defect)

    def clear_all(self):
        """Clears all weather anomalies and sensor defects, restoring normal operation."""
        self.state.weather_anomaly = AnomalyType.NONE
        self.state.active_sensor_defects.clear()
        self.state.drift_accumulated_c = 0.0
        self.state.stuck_temp_value = None
        self.state.spike_counter = 0

    def get_ground_truth(self) -> Dict[str, Any]:
        """Returns ground-truth classification labels for validation/scoring by judges."""
        labels = []
        if self.state.weather_anomaly != AnomalyType.NONE:
            labels.append(self.state.weather_anomaly.value)
        for defect in self.state.active_sensor_defects:
            labels.append(defect.value)
        
        status = "NORMAL"
        if any(d.startswith("SENSOR_DEFECT") for d in labels):
            status = "SENSOR_DEFECT"
        elif any(w.startswith("WEATHER_ANOMALY") for w in labels):
            status = "WEATHER_ANOMALY"

        return {
            "status": status,
            "active_labels": labels if labels else ["NORMAL"],
        }

    def process(self, baseline: WeatherReading) -> Dict[str, Any]:
        """Transforms baseline reading by applying physical weather shifts, then hardware defects."""
        # Work on a copy of baseline data dictionary
        data = baseline.to_dict()

        # -------------------------------------------------------------
        # STEP 1: APPLY WEATHER ANOMALIES (Multivariate physical shifts)
        # -------------------------------------------------------------
        if self.state.weather_anomaly == AnomalyType.WEATHER_SEVERE_STORM:
            # Physics of Severe Thunderstorm / Squall Downdraft:
            # - Barometric pressure crashes rapidly (-12 hPa)
            # - Wind gusts surge drastically (>22 m/s) with chaotic veer
            # - Torrential precipitation spike (>55 mm/h)
            # - Evaporative cooling drops temperature (-5.5°C)
            # - Relative humidity saturates near 98-100%
            # - Solar radiation collapses due to thick cumulonimbus anvil
            data["pressure_hpa"] = round(data["pressure_hpa"] - 13.5 + random.uniform(-1.0, 1.0), 2)
            data["wind_speed_mps"] = round(data["wind_speed_mps"] + random.uniform(16.0, 24.0), 2)
            data["precipitation_mmh"] = round(data["precipitation_mmh"] + random.uniform(45.0, 75.0), 2)
            data["temperature_c"] = round(data["temperature_c"] - 6.2 + random.uniform(-0.5, 0.5), 2)
            data["humidity_pct"] = round(min(99.5, data["humidity_pct"] + 25.0), 2)
            data["solar_radiation_wm2"] = round(max(0.0, data["solar_radiation_wm2"] * 0.05), 1)

        elif self.state.weather_anomaly == AnomalyType.WEATHER_HEATWAVE:
            # Physics of Intense Heatwave:
            # - Temperature spikes dramatically (+8.5°C)
            # - Relative humidity plummets due to high saturation vapor pressure (-20%)
            # - Barometric pressure slightly lowers due to thermal convective depression (-3.0 hPa)
            # - Precipitation is strictly zero
            data["temperature_c"] = round(data["temperature_c"] + 8.8 + random.uniform(-0.5, 0.5), 2)
            data["humidity_pct"] = round(max(8.0, data["humidity_pct"] - 22.0 + random.uniform(-1.5, 1.5)), 2)
            data["pressure_hpa"] = round(data["pressure_hpa"] - 3.2, 2)
            data["precipitation_mmh"] = 0.0

        elif self.state.weather_anomaly == AnomalyType.WEATHER_COLD_SNAP:
            # Physics of Cold Front / Western Disturbance:
            # - Temperature drops sharply (-11°C)
            # - Barometric pressure rises due to dense cold air mass (+9.5 hPa)
            # - Gusty northwesterly wind shifts
            data["temperature_c"] = round(max(-2.0, data["temperature_c"] - 11.0 + random.uniform(-0.8, 0.8)), 2)
            data["pressure_hpa"] = round(data["pressure_hpa"] + 9.8, 2)
            data["wind_speed_mps"] = round(data["wind_speed_mps"] + random.uniform(4.0, 8.0), 2)

        # -------------------------------------------------------------
        # STEP 2: APPLY HARDWARE SENSOR DEFECTS (Unphysical isolated faults)
        # -------------------------------------------------------------
        # 1. Stuck Sensor / Flatline (Zero variance on temperature while other sensors move)
        if AnomalyType.DEFECT_STUCK_SENSOR in self.state.active_sensor_defects:
            if self.state.stuck_temp_value is None:
                self.state.stuck_temp_value = data["temperature_c"]
            data["temperature_c"] = round(self.state.stuck_temp_value, 2)

        # 2. Calibration Drift (Cumulative artificial offset without physical justification)
        if AnomalyType.DEFECT_CALIBRATION_DRIFT in self.state.active_sensor_defects:
            self.state.drift_accumulated_c += 0.15  # creeps up by 0.15°C every tick
            data["temperature_c"] = round(data["temperature_c"] + self.state.drift_accumulated_c, 2)

        # 3. High-Frequency Electrical Noise (Violates physical thermodynamic inertia limits)
        if AnomalyType.DEFECT_ERRATIC_NOISE in self.state.active_sensor_defects:
            noise = random.choice([-12.5, 12.5, -9.0, 14.0]) + random.gauss(0, 3.0)
            data["temperature_c"] = round(data["temperature_c"] + noise, 2)

        # 4. Outlier Spike (Impossible instantaneous jump for a single tick)
        if AnomalyType.DEFECT_OUTLIER_SPIKE in self.state.active_sensor_defects:
            # Fires once or intermittently every 4 ticks
            self.state.spike_counter += 1
            if self.state.spike_counter % 3 == 0:
                data["temperature_c"] = 88.88  # Impossible atmospheric ambient temperature!
                data["humidity_pct"] = 150.0   # Physically impossible relative humidity!

        # 5. Packet Drop / Null Reading (I2C/SPI bus transmission error)
        if AnomalyType.DEFECT_PACKET_DROP_NULL in self.state.active_sensor_defects:
            data["temperature_c"] = None
            data["humidity_pct"] = None

        # 6. ADC Rail Saturation (Sensor voltage pegged at rail limits)
        if AnomalyType.DEFECT_ADC_SATURATION in self.state.active_sensor_defects:
            data["temperature_c"] = 999.9
            data["pressure_hpa"] = 0.0

        # Attach ground truth annotations
        data["_ground_truth"] = self.get_ground_truth()
        return data
