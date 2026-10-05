"""Indian Climate Profiles based on Indian Meteorological Department (IMD) historical baselines.
Provides realistic boundaries, diurnal parameters, and stochastic volatility parameters
for varied micro-climates across India.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class ClimateProfile:
    key: str
    display_name: str
    description: str
    # Temperature (°C)
    temp_mean: float
    temp_diurnal_amplitude: float  # peak offset above/below mean over 24h
    temp_min_hard: float
    temp_max_hard: float
    # Relative Humidity (%)
    rh_mean: float
    rh_min_hard: float
    rh_max_hard: float
    # Barometric Pressure (hPa at MSL)
    pressure_mean: float
    pressure_min_hard: float
    pressure_max_hard: float
    # Wind Speed (m/s)
    wind_mean: float
    wind_max_hard: float
    # Solar Irradiance (W/m² at solar noon)
    solar_noon_max: float
    # Precipitation (mm/h)
    rain_base_probability: float  # Chance of rain tick in baseline state
    rain_rate_mean: float         # Average rain rate when raining
    # Stochastic Ornstein-Uhlenbeck Parameters
    ou_theta: float               # Mean reversion rate (how strongly it pulls to physical curve)
    ou_sigma_temp: float          # Noise variance for temperature
    ou_sigma_pressure: float      # Noise variance for pressure
    ou_sigma_rh: float            # Noise variance for humidity

CLIMATE_PROFILES: Dict[str, ClimateProfile] = {
    "mumbai_monsoon": ClimateProfile(
        key="mumbai_monsoon",
        display_name="Mumbai Monsoon Coastal (Konkan Coast)",
        description="High humidity, coastal squalls, heavy episodic downpours, depressed barometric pressure.",
        temp_mean=29.0,
        temp_diurnal_amplitude=3.5,
        temp_min_hard=24.0,
        temp_max_hard=35.0,
        rh_mean=86.0,
        rh_min_hard=70.0,
        rh_max_hard=99.0,
        pressure_mean=1003.5,
        pressure_min_hard=994.0,
        pressure_max_hard=1012.0,
        wind_mean=6.5,
        wind_max_hard=22.0,
        solar_noon_max=450.0,      # Overcast monsoonal cloud decks
        rain_base_probability=0.35,
        rain_rate_mean=18.0,
        ou_theta=0.15,
        ou_sigma_temp=0.35,
        ou_sigma_pressure=0.25,
        ou_sigma_rh=1.2,
    ),
    "delhi_summer": ClimateProfile(
        key="delhi_summer",
        display_name="Delhi Summer Heatwave (Northern Plains)",
        description="Blistering heat, dry desiccating air, intense solar radiation, gusty Loo winds.",
        temp_mean=39.5,
        temp_diurnal_amplitude=7.5,
        temp_min_hard=30.0,
        temp_max_hard=48.0,
        rh_mean=28.0,
        rh_min_hard=12.0,
        rh_max_hard=50.0,
        pressure_mean=1004.0,
        pressure_min_hard=997.0,
        pressure_max_hard=1012.0,
        wind_mean=5.0,
        wind_max_hard=16.0,
        solar_noon_max=1020.0,     # Blazing unclouded skies
        rain_base_probability=0.01,
        rain_rate_mean=0.0,
        ou_theta=0.12,
        ou_sigma_temp=0.45,
        ou_sigma_pressure=0.20,
        ou_sigma_rh=0.8,
    ),
    "thar_desert": ClimateProfile(
        key="thar_desert",
        display_name="Thar Desert Arid (Rajasthan)",
        description="Extreme diurnal temperature swings (scorching days, crisp nights), near-zero rain, arid air.",
        temp_mean=35.0,
        temp_diurnal_amplitude=11.0,
        temp_min_hard=20.0,
        temp_max_hard=50.0,
        rh_mean=20.0,
        rh_min_hard=8.0,
        rh_max_hard=42.0,
        pressure_mean=1006.0,
        pressure_min_hard=998.0,
        pressure_max_hard=1015.0,
        wind_mean=5.8,
        wind_max_hard=18.0,
        solar_noon_max=1080.0,
        rain_base_probability=0.002,
        rain_rate_mean=0.0,
        ou_theta=0.10,
        ou_sigma_temp=0.50,
        ou_sigma_pressure=0.18,
        ou_sigma_rh=0.7,
    ),
    "bengaluru_temperate": ClimateProfile(
        key="bengaluru_temperate",
        display_name="Bengaluru Temperate (Deccan Plateau)",
        description="Moderate year-round climate, gentle plateau breezes, comfortable humidity, mild diurnal shifts.",
        temp_mean=25.5,
        temp_diurnal_amplitude=5.0,
        temp_min_hard=18.0,
        temp_max_hard=34.0,
        rh_mean=60.0,
        rh_min_hard=35.0,
        rh_max_hard=88.0,
        pressure_mean=1013.0,
        pressure_min_hard=1005.0,
        pressure_max_hard=1020.0,
        wind_mean=3.8,
        wind_max_hard=12.0,
        solar_noon_max=800.0,
        rain_base_probability=0.08,
        rain_rate_mean=5.0,
        ou_theta=0.14,
        ou_sigma_temp=0.30,
        ou_sigma_pressure=0.15,
        ou_sigma_rh=1.0,
    ),
}

def get_climate_profile(region_key: str) -> ClimateProfile:
    """Returns climate profile by key, defaulting to mumbai_monsoon."""
    return CLIMATE_PROFILES.get(region_key, CLIMATE_PROFILES["mumbai_monsoon"])
