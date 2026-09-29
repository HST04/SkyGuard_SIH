import logging
import math
from typing import Any, Dict, List, Optional, Union
import numpy as np

logger = logging.getLogger("skyguard.multi_scale_analyzer")


class MultiScaleAnalyzer:
    """
    Layer 2.1: Multi-Scale Multivariate Physical Analyzer (PRD Section 5.3 / TASKS.md Task 1.3).
    
    Unpacks rolling telemetry windows to evaluate thermodynamic coupling:
      1. Computes short-term numerical rates of change: dT/dt, dP/dt, dRH/dt, d²P/dt².
      2. Computes the inter-channel thermodynamic correlation coefficient: rho_{T, RH}.
         Under normal physics, diurnal heating causes relative humidity to fall (rho < -0.70).
      3. Evaluates physical decoupling flag:
         rho_{T, RH} > 0.0 and abs(dP/dt) < 2.0 hPa
         Indicates that humidity is drifting or increasing without an associated barometric drop.
      4. Generates an engineered feature dictionary used by Model A (Squall/Weather)
         and Model B (Sensor Defect) classifiers.
    """

    def __init__(self, default_window_size: int = 12) -> None:
        self.default_window_size = default_window_size

    @staticmethod
    def _extract_val(item: Any, key: str, default: float = 0.0) -> float:
        """Safely extracts a float field from a Pydantic model or dictionary."""
        if hasattr(item, key):
            val = getattr(item, key)
        elif isinstance(item, dict):
            val = item.get(key, default)
        else:
            val = default
        try:
            return float(val) if val is not None else default
        except (ValueError, TypeError):
            return default

    def compute_derivatives(self, window: List[Any]) -> Dict[str, float]:
        """
        Computes numerical first derivatives (dT/dt, dP/dt, dRH/dt) and second
        derivative (d²P/dt²) over the telemetry window.
        """
        if not window:
            return {"dt_dt": 0.0, "dp_dt": 0.0, "drh_dt": 0.0, "d2p_dt2": 0.0}

        curr = window[-1]
        prev = window[-2] if len(window) > 1 else curr

        curr_t = self._extract_val(curr, "temperature_c", 25.0)
        prev_t = self._extract_val(prev, "temperature_c", curr_t)
        dt_dt = curr_t - prev_t

        curr_p = self._extract_val(curr, "pressure_hpa", 1010.0)
        prev_p = self._extract_val(prev, "pressure_hpa", curr_p)
        dp_dt = curr_p - prev_p

        curr_rh = self._extract_val(curr, "humidity_pct", 50.0)
        prev_rh = self._extract_val(prev, "humidity_pct", curr_rh)
        drh_dt = curr_rh - prev_rh

        # Second derivative of pressure: d²P/dt²
        if len(window) >= 3:
            prev2 = window[-3]
            prev2_p = self._extract_val(prev2, "pressure_hpa", prev_p)
            prev_dp_dt = prev_p - prev2_p
            d2p_dt2 = dp_dt - prev_dp_dt
        else:
            d2p_dt2 = 0.0

        return {
            "dt_dt": round(dt_dt, 4),
            "dp_dt": round(dp_dt, 4),
            "drh_dt": round(drh_dt, 4),
            "d2p_dt2": round(d2p_dt2, 4),
        }

    def compute_thermodynamic_correlation(self, window: List[Any]) -> float:
        """
        Computes Pearson correlation coefficient rho_{T, RH} across the sliding window.
        Returns 0.0 if window has fewer than 2 samples or zero variance.
        """
        if len(window) < 2:
            return 0.0

        temps = [self._extract_val(item, "temperature_c", 25.0) for item in window]
        rhs = [self._extract_val(item, "humidity_pct", 50.0) for item in window]

        n = len(temps)
        mean_t = sum(temps) / n
        mean_rh = sum(rhs) / n

        var_t = sum((t - mean_t) ** 2 for t in temps)
        var_rh = sum((rh - mean_rh) ** 2 for rh in rhs)

        # Invariant sensor or near-zero variance
        if var_t < 1e-7 or var_rh < 1e-7:
            return 0.0

        cov = sum((t - mean_t) * (rh - mean_rh) for t, rh in zip(temps, rhs))
        std_prod = math.sqrt(var_t * var_rh)

        if std_prod <= 0.0:
            return 0.0

        corr = cov / std_prod
        return round(float(np.clip(corr, -1.0, 1.0)), 4)

    def analyze_window(self, window: List[Any]) -> Dict[str, Any]:
        """
        Comprehensive multi-scale analysis over the current rolling telemetry window.
        Returns engineered feature dictionary for Model A, Model B, and Confluence Engine.
        """
        if not window:
            return {
                "dT_dt": 0.0,
                "dP_dt": 0.0,
                "dRH_dt": 0.0,
                "d2P_dt2": 0.0,
                "dt_dt": 0.0,
                "dp_dt": 0.0,
                "drh_dt": 0.0,
                "d2p_dt2": 0.0,
                "rho_t_rh": 0.0,
                "rho_T_RH": 0.0,
                "decoupling_flag": False,
                "temperature_c": 25.0,
                "humidity_pct": 50.0,
                "pressure_hpa": 1013.25,
                "dew_point_c": 14.0,
                "wind_speed_ms": 2.5,
                "wind_dir_deg": 180.0,
                "solar_radiation_wm2": 450.0,
                "window_size": 0,
                "features_vector": [25.0, 50.0, 1013.25, 14.0, 2.5, 0.0, 0.0, 0.0, 0.0, 0.0],
            }

        curr = window[-1]
        derivs = self.compute_derivatives(window)
        rho_t_rh = self.compute_thermodynamic_correlation(window)

        # Decoupling Rule (Layer 2.1):
        # Thermodynamic decoupling occurs when Temperature and Humidity are positively correlated
        # without significant barometric pressure drops (|dP/dt| < 2.0 hPa).
        decoupling_flag = bool(rho_t_rh > 0.0 and abs(derivs["dp_dt"]) < 2.0)

        temp = self._extract_val(curr, "temperature_c", 25.0)
        rh = self._extract_val(curr, "humidity_pct", 50.0)
        pres = self._extract_val(curr, "pressure_hpa", 1013.25)
        dew = self._extract_val(curr, "dew_point_c", 14.0)
        wind = self._extract_val(curr, "wind_speed_ms", 2.5)
        wind_dir = self._extract_val(curr, "wind_dir_deg", 180.0)
        solar = self._extract_val(curr, "solar_radiation_wm2", 450.0)

        feature_vector = [
            temp,
            rh,
            pres,
            dew,
            wind,
            derivs["dt_dt"],
            derivs["dp_dt"],
            derivs["drh_dt"],
            derivs["d2p_dt2"],
            rho_t_rh,
        ]

        return {
            # Uppercase keys matching PRD math notation
            "dT_dt": derivs["dt_dt"],
            "dP_dt": derivs["dp_dt"],
            "dRH_dt": derivs["drh_dt"],
            "d2P_dt2": derivs["d2p_dt2"],
            # Lowercase keys for pythonic ease
            "dt_dt": derivs["dt_dt"],
            "dp_dt": derivs["dp_dt"],
            "drh_dt": derivs["drh_dt"],
            "d2p_dt2": derivs["d2p_dt2"],
            # Thermodynamic correlation
            "rho_t_rh": rho_t_rh,
            "rho_T_RH": rho_t_rh,
            # Physical decoupling indicator
            "decoupling_flag": decoupling_flag,
            # Channel context
            "temperature_c": temp,
            "humidity_pct": rh,
            "pressure_hpa": pres,
            "dew_point_c": dew,
            "wind_speed_ms": wind,
            "wind_dir_deg": wind_dir,
            "solar_radiation_wm2": solar,
            "window_size": len(window),
            "features_vector": feature_vector,
        }


multi_scale_analyzer = MultiScaleAnalyzer()
