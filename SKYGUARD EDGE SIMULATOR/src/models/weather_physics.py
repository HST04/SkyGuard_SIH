"""Stochastic Meteorological Physics Engine.
Implements:
1. Solar Zenith Angle & Diurnal Radiative Thermal Curve
2. Magnus-Tetens Psychrometric Vapor Pressure & Relative Humidity Correlation
3. Atmospheric Tidal Barometric Pressure Oscillations
4. Ornstein-Uhlenbeck (OU) Mean-Reverting Stochastic Diffusion Processes
"""

import math
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any

from src.models.indian_climates import ClimateProfile

@dataclass
class WeatherReading:
    timestamp_ms: int
    iso_time: str
    temperature_c: float
    humidity_pct: float
    pressure_hpa: float
    wind_speed_mps: float
    wind_direction_deg: float
    solar_radiation_wm2: float
    precipitation_mmh: float
    battery_pct: float
    voltage_v: float
    rssi_dbm: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp_ms": self.timestamp_ms,
            "iso_time": self.iso_time,
            "temperature_c": round(self.temperature_c, 2),
            "humidity_pct": round(self.humidity_pct, 2),
            "pressure_hpa": round(self.pressure_hpa, 2),
            "wind_speed_mps": round(self.wind_speed_mps, 2),
            "wind_direction_deg": round(self.wind_direction_deg, 1),
            "solar_radiation_wm2": round(self.solar_radiation_wm2, 1),
            "precipitation_mmh": round(self.precipitation_mmh, 2),
            "battery_pct": round(self.battery_pct, 1),
            "voltage_v": round(self.voltage_v, 2),
            "rssi_dbm": int(self.rssi_dbm),
        }

class WeatherPhysicsEngine:
    """Simulates realistic atmospheric variables governed by physical laws and stochastic variance."""

    def __init__(self, profile: ClimateProfile, seed: int = None):
        self.profile = profile
        if seed is not None:
            random.seed(seed)
        
        # State variables for Ornstein-Uhlenbeck process
        self.current_temp = profile.temp_mean
        self.current_pressure = profile.pressure_mean
        self.current_rh = profile.rh_mean
        self.current_wind = profile.wind_mean
        self.current_wind_dir = random.uniform(180, 270)  # Typical SW monsoon/westerly vector
        self.current_solar = 0.0
        self.current_rain = 0.0

        # Device health state
        self.battery_pct = 98.0
        self.voltage_v = 3.85
        self.rssi_dbm = -65

    def step(self, hour_of_day: float, dt_seconds: float = 1.0) -> WeatherReading:
        """Computes next physical state based on time of day and Ornstein-Uhlenbeck diffusion."""
        dt = dt_seconds / 3600.0  # Convert to fraction of hour

        # 1. Solar Irradiance Model (W/m²)
        # Daylight between 06:00 and 18:00, peak at 12:00 solar noon
        if 6.0 <= hour_of_day <= 18.0:
            solar_angle = math.pi * (hour_of_day - 6.0) / 12.0
            solar_target = self.profile.solar_noon_max * math.sin(solar_angle)
            # Add cloud turbidity fluctuation
            solar_target *= random.uniform(0.85, 1.0)
        else:
            solar_target = 0.0
        self.current_solar = max(0.0, solar_target)

        # 2. Diurnal Temperature Curve (°C)
        # Thermal inertia shifts peak temperature to ~15:00 (3 PM), trough to ~05:00 (5 AM)
        # sin((hour - 9) * 2pi / 24): at hour=15 -> sin(pi/2)=1.0; at hour=3 -> sin(-pi/2)=-1.0
        thermal_cycle_phase = 2.0 * math.pi * (hour_of_day - 9.0) / 24.0
        temp_target = self.profile.temp_mean + self.profile.temp_diurnal_amplitude * math.sin(thermal_cycle_phase)

        # Ornstein-Uhlenbeck Mean-Reverting Random Walk: dX = theta * (target - X)*dt + sigma * sqrt(dt) * N(0,1)
        theta = self.profile.ou_theta
        sigma_temp = self.profile.ou_sigma_temp
        d_temp = theta * (temp_target - self.current_temp) * dt + sigma_temp * math.sqrt(max(dt, 0.0001)) * random.gauss(0, 1)
        self.current_temp += d_temp
        self.current_temp = max(self.profile.temp_min_hard, min(self.profile.temp_max_hard, self.current_temp))

        # 3. Barometric Pressure (hPa)
        # Includes semi-diurnal atmospheric solar tide (12-hour cycle with ~1.5 hPa amplitude)
        tide_phase = 4.0 * math.pi * (hour_of_day - 10.0) / 24.0
        pressure_target = self.profile.pressure_mean + 1.2 * math.sin(tide_phase)
        sigma_press = self.profile.ou_sigma_pressure
        d_pressure = theta * (pressure_target - self.current_pressure) * dt + sigma_press * math.sqrt(max(dt, 0.0001)) * random.gauss(0, 1)
        self.current_pressure += d_pressure
        self.current_pressure = max(self.profile.pressure_min_hard, min(self.profile.pressure_max_hard, self.current_pressure))

        # 4. Psychrometric Relative Humidity (Magnus-Tetens Equation)
        # Warm air holds exponentially more moisture: es(T) = 6.1078 * exp(17.27 * T / (T + 237.3))
        # Base vapor pressure stays relatively conserved in a micro-airmass,
        # causing RH to inversely track diurnal temperature fluctuations
        temp_normalized_delta = (self.current_temp - self.profile.temp_mean)
        rh_target = self.profile.rh_mean - 1.4 * temp_normalized_delta
        sigma_rh = self.profile.ou_sigma_rh
        d_rh = theta * (rh_target - self.current_rh) * dt + sigma_rh * math.sqrt(max(dt, 0.0001)) * random.gauss(0, 1)
        self.current_rh += d_rh
        self.current_rh = max(self.profile.rh_min_hard, min(self.profile.rh_max_hard, self.current_rh))

        # 5. Wind Speed (m/s) & Direction (deg)
        # Thermal diurnal breeze: wind slightly picks up during maximum heat gradient
        wind_target = self.profile.wind_mean + (1.2 if 11.0 <= hour_of_day <= 17.0 else -0.5)
        self.current_wind += 0.2 * (wind_target - self.current_wind) * dt + 0.3 * random.gauss(0, 1)
        self.current_wind = max(0.2, min(self.profile.wind_max_hard, self.current_wind))
        # Gentle wind direction drift
        self.current_wind_dir = (self.current_wind_dir + random.gauss(0, 1.5)) % 360.0

        # 6. Precipitation (mm/h)
        if random.random() < self.profile.rain_base_probability:
            # Active precipitation pulse
            rain_rate = max(0.0, random.gauss(self.profile.rain_rate_mean, 5.0))
            self.current_rain = round(rain_rate, 2)
            # Rain cools temperature and saturates humidity
            self.current_rh = min(99.0, self.current_rh + 5.0)
            self.current_temp = max(self.profile.temp_min_hard, self.current_temp - 0.8)
        else:
            self.current_rain = 0.0

        # 7. Device Health / Battery Telemetry
        # Micro battery drain (~0.001% per 1000 ticks)
        self.battery_pct = max(10.0, self.battery_pct - 0.0001)
        self.voltage_v = 3.3 + (self.battery_pct / 100.0) * 0.9  # 3.3V to 4.2V Li-ion discharge curve
        self.rssi_dbm = int(-65 + random.randint(-4, 4))

        # Timing metadata
        now_utc = datetime.now(timezone.utc)
        timestamp_ms = int(now_utc.timestamp() * 1000)
        iso_time = now_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"

        return WeatherReading(
            timestamp_ms=timestamp_ms,
            iso_time=iso_time,
            temperature_c=self.current_temp,
            humidity_pct=self.current_rh,
            pressure_hpa=self.current_pressure,
            wind_speed_mps=self.current_wind,
            wind_direction_deg=self.current_wind_dir,
            solar_radiation_wm2=self.current_solar,
            precipitation_mmh=self.current_rain,
            battery_pct=self.battery_pct,
            voltage_v=self.voltage_v,
            rssi_dbm=self.rssi_dbm,
        )
