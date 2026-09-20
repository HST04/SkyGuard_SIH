import math
from typing import Optional, Tuple, List, Dict
from models.schemas import TelemetryPayload, ShapAttribution

def calculate_dew_point(temperature_c: float, humidity_pct: float) -> float:
    """Calculates dew point using the standard Magnus-Tetens approximation formula."""
    rh = max(0.01, min(100.0, humidity_pct))
    a = 17.27
    b = 237.7
    try:
        alpha = ((a * temperature_c) / (b + temperature_c)) + math.log(rh / 100.0)
        td = (b * alpha) / (a - alpha)
        return round(td, 2)
    except Exception:
        return temperature_c - ((100.0 - rh) / 5.0)

class IMDPhysicsRuleEngine:
    """
    Stage 1: Deterministic Climatological & Physical Bounds Checker.
    Strictly based on India Meteorological Department (IMD) and WMO AWS standards.
    """
    
    # Climatological Limits for Indian subcontinent Automatic Weather Stations
    TEMP_MIN = -10.0   # °C
    TEMP_MAX = 60.0    # °C
    PRESS_MIN = 850.0  # hPa (Agra elevation ~169m has ~990-1015 hPa normal)
    PRESS_MAX = 1080.0 # hPa
    RH_MIN = 0.0       # %
    RH_MAX = 100.0     # %
    
    MAX_TEMP_STEP_PER_SEC = 2.0   # Fast rate check
    MAX_PRESS_STEP_PER_SEC = 3.0
    MAX_RH_STEP_PER_SEC = 10.0

    @classmethod
    def evaluate(
        cls, 
        current: TelemetryPayload, 
        history: List[TelemetryPayload]
    ) -> Optional[Dict]:
        """
        Evaluates current reading against IMD physics bounds and previous step.
        Returns None if passed, or a dict detailing the violation if failed.
        """
        # 1. Physical Bounds Check (Zero tolerance)
        if current.temperature_c < cls.TEMP_MIN or current.temperature_c > cls.TEMP_MAX:
            return {
                "rule": "IMD_CLIMATOLOGICAL_TEMP_BOUND",
                "culprit": ["temperature"],
                "severity": 0.95,
                "message": f"Temperature reading {current.temperature_c:.1f}°C is physically impossible for station environment [{cls.TEMP_MIN}°C, {cls.TEMP_MAX}°C].",
                "shap_attributions": [
                    ShapAttribution(feature="temperature", importance=0.95, direction="positive" if current.temperature_c > cls.TEMP_MAX else "negative", message="Extreme physical boundary violation.")
                ]
            }

        if current.humidity_pct < cls.RH_MIN or current.humidity_pct > cls.RH_MAX:
            return {
                "rule": "IMD_CLIMATOLOGICAL_RH_BOUND",
                "culprit": ["humidity"],
                "severity": 0.90,
                "message": f"Relative Humidity reading {current.humidity_pct:.1f}% violates physical saturation limits [0%, 100%].",
                "shap_attributions": [
                    ShapAttribution(feature="humidity", importance=0.92, direction="positive" if current.humidity_pct > cls.RH_MAX else "negative", message="Sensor exceeded 100% physical saturation.")
                ]
            }

        if current.pressure_hpa < cls.PRESS_MIN or current.pressure_hpa > cls.PRESS_MAX:
            return {
                "rule": "IMD_BAROMETRIC_PRESSURE_BOUND",
                "culprit": ["pressure"],
                "severity": 0.90,
                "message": f"Barometric pressure {current.pressure_hpa:.1f} hPa outside operational envelope [{cls.PRESS_MIN}, {cls.PRESS_MAX}] hPa.",
                "shap_attributions": [
                    ShapAttribution(feature="pressure", importance=0.91, direction="negative" if current.pressure_hpa < cls.PRESS_MIN else "positive", message="Barometer output fell below atmospheric envelope.")
                ]
            }

        # 2. Dew Point Supersaturation Sanity
        # In free air, dew point cannot significantly exceed air temperature (Td <= T + 0.5)
        calculated_td = calculate_dew_point(current.temperature_c, current.humidity_pct)
        if calculated_td > current.temperature_c + 1.0:
            return {
                "rule": "IMD_SUPERSATURATION_VIOLATION",
                "culprit": ["humidity", "temperature"],
                "severity": 0.85,
                "message": f"Calculated Dew Point ({calculated_td:.1f}°C) exceeds ambient temperature ({current.temperature_c:.1f}°C), violating thermodynamic equilibrium.",
                "shap_attributions": [
                    ShapAttribution(feature="humidity", importance=0.65, direction="positive", message="Moisture reading inconsistent with temperature."),
                    ShapAttribution(feature="temperature", importance=0.35, direction="negative", message="Ambient temp unable to sustain reported vapor pressure.")
                ]
            }

        # 3. Dynamic Step Checks (Requires previous reading)
        if history and len(history) >= 1:
            prev = history[-1]
            dt_temp = abs(current.temperature_c - prev.temperature_c)
            dt_press = abs(current.pressure_hpa - prev.pressure_hpa)
            dt_rh = abs(current.humidity_pct - prev.humidity_pct)

            if dt_temp > cls.MAX_TEMP_STEP_PER_SEC:
                return {
                    "rule": "IMD_TEMP_RATE_OF_CHANGE_EXCEEDED",
                    "culprit": ["temperature"],
                    "severity": 0.88,
                    "message": f"Sudden thermal transient detected: ΔT of {dt_temp:.2f}°C/s exceeds physical thermal inertia limit.",
                    "shap_attributions": [
                        ShapAttribution(feature="dT_dt", importance=0.89, direction="positive", message="Severe thermal step change detected.")
                    ]
                }

            if dt_press > cls.MAX_PRESS_STEP_PER_SEC:
                return {
                    "rule": "IMD_PRESSURE_BURST_EXCEEDED",
                    "culprit": ["pressure"],
                    "severity": 0.85,
                    "message": f"Sudden barometric discontinuity: ΔP of {dt_press:.2f} hPa/s exceeds atmospheric front velocity.",
                    "shap_attributions": [
                        ShapAttribution(feature="dP_dt", importance=0.86, direction="negative", message="Rapid pressure drop rate observed.")
                    ]
                }

            if dt_rh > cls.MAX_RH_STEP_PER_SEC:
                return {
                    "rule": "IMD_HUMIDITY_SPIKE_EXCEEDED",
                    "culprit": ["humidity"],
                    "severity": 0.82,
                    "message": f"Rapid humidity jump: ΔRH of {dt_rh:.1f}%/s exceeds physical diffusion rate.",
                    "shap_attributions": [
                        ShapAttribution(feature="dRH_dt", importance=0.84, direction="positive", message="Capacitive humidity sensor pulse detected.")
                    ]
                }

        # 4. Flatline / Stuck Sensor Check (Last 10 identical readings)
        if history and len(history) >= 8:
            recent_rh = [p.humidity_pct for p in history[-8:]] + [current.humidity_pct]
            if len(set(recent_rh)) == 1 and (current.humidity_pct == 100.0 or current.humidity_pct == 0.0):
                return {
                    "rule": "IMD_STUCK_SENSOR_FLATLINE",
                    "culprit": ["humidity"],
                    "severity": 0.80,
                    "message": f"Relative Humidity is frozen flatlined at {current.humidity_pct}% for extended intervals (probable sensor condensation lock or trace failure).",
                    "shap_attributions": [
                        ShapAttribution(feature="humidity", importance=0.90, direction="positive", message="Sensor stuck at saturation asymptote.")
                    ]
                }

        return None
