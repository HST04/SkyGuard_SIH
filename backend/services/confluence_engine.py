import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

logger = logging.getLogger("skyguard.confluence")


class ConfluenceResult(dict):
    """
    Structured outcome of the Dual-Model Classification Confluence Decision Matrix (PRD Section 5.5).
    Inherits from dict so it can be unpacked, formatted as JSON, or indexed as a dictionary,
    while supporting direct dot-attribute access.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class ConfluenceEngine:
    """
    Layer 2.3: Classification Confluence & Confidence Scoring Engine.
    Reconciles predictions from:
      - Model A: Weather Classifier (P(Weather), distinguishing squalls from nominal)
      - Model B: Sensor Defect Classifier (P(Defect) and defect pattern classification)
    Applies a deterministic decision matrix and mathematical confidence scoring formula
    to produce auditable, reproducible AI alerting decisions.
    """

    DEFECT_CLASSES = [
        "none",
        "frozen_value",
        "capacitive_drift",
        "impulse_spike",
        "noise_burst",
        "packet_dropout",
    ]

    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = artifacts_dir
        self.model_a = None
        self.model_b = None
        self._load_models()

    def _load_models(self) -> None:
        """
        Attempts to load Model A (Weather) and Model B (Defect) from artifacts or root.
        If models are not yet trained, the engine activates meteorological heuristic inference.
        """
        if self.artifacts_dir is not None:
            candidate_dirs = [self.artifacts_dir]
        else:
            candidate_dirs = [
                os.path.join(os.path.dirname(__file__), "..", "ml_artifacts"),
                os.path.join(os.path.dirname(__file__), "..", ".."),
                os.getcwd(),
                os.path.join(os.getcwd(), "backend", "ml_artifacts"),
            ]

        model_a_path = None
        model_b_path = None

        for d in candidate_dirs:
            if not d:
                continue
            pa = os.path.join(d, "model_a_weather.pkl")
            if model_a_path is None and os.path.exists(pa):
                model_a_path = pa
            pb = os.path.join(d, "model_b_defect.pkl")
            if model_b_path is None and os.path.exists(pb):
                model_b_path = pb

        if model_a_path:
            try:
                import joblib

                self.model_a = joblib.load(model_a_path)
                logger.info(f"Loaded Model A (Weather Classifier) from {model_a_path}")
            except Exception as exc:
                self.model_a = None
                logger.warning(f"Could not load Model A from {model_a_path}: {exc}")

        if model_b_path:
            try:
                import joblib

                self.model_b = joblib.load(model_b_path)
                logger.info(f"Loaded Model B (Sensor Defect Classifier) from {model_b_path}")
            except Exception as exc:
                self.model_b = None
                logger.warning(f"Could not load Model B from {model_b_path}: {exc}")

    def compute_confidence(self, p_weather: float, p_defect: float) -> float:
        """
        Calculates mathematical confidence score (0-100%).
        Formula: max(P_d, P_w) * (1.0 - (1.0 - |P_d - P_w|) * 0.18) * 100.0.
        """
        p_w = max(0.0, min(1.0, float(p_weather)))
        p_d = max(0.0, min(1.0, float(p_defect)))

        diff = abs(p_d - p_w)
        max_p = max(p_d, p_w)
        ambiguity = 1.0 - diff

        conf_pct = max_p * (1.0 - ambiguity * 0.18) * 100.0
        return round(conf_pct, 1)

    def evaluate_confluence(
        self,
        p_weather: float,
        p_defect: float,
        defect_type: str = "none",
    ) -> ConfluenceResult:
        p_w = float(p_weather)
        p_d = float(p_defect)
        confidence_score = self.compute_confidence(p_w, p_d)

        if p_w < 0.30 and p_d < 0.30:
            classification = "Nominal Baseline"
            severity = "Nominal"
            operator_alert = False
            action_taken = "Continuous 1 Hz nominal monitoring; atmospheric parameters healthy"
            confidence_score = round((1.0 - max(p_w, p_d)) * 100.0, 1)
        elif p_w >= 0.70 and p_d < 0.30:
            classification = "Natural Weather Event"
            severity = "Nominal"
            operator_alert = False
            action_taken = "Logged as valid extreme weather; baseline updated"
        elif p_w < 0.30 and p_d >= 0.70:
            classification = "Sensor Defect"
            severity = "High"
            operator_alert = True
            action_taken = "Trigger SHAP, flag faulty sensor, invoke Imputation"
        elif p_w >= 0.70 and p_d >= 0.70:
            classification = "Compound Event"
            severity = "Warning"
            operator_alert = True
            action_taken = "Weather event with degraded sensor; technician review"
        else:
            classification = "Uncertain Anomaly"
            severity = "Moderate"
            operator_alert = False
            action_taken = "Logged for active learning / operator verification"

        return ConfluenceResult(
            classification=classification,
            confidence_score=confidence_score,
            severity=severity,
            operator_alert=operator_alert,
            action_taken=action_taken,
            p_weather=round(p_w, 4),
            p_defect=round(p_d, 4),
            defect_type=defect_type,
        )

    @staticmethod
    def _extract_val(item: Any, key: str, default: float) -> float:
        if isinstance(item, dict):
            val = item.get(key, default)
        else:
            val = getattr(item, key, default)
        try:
            return float(val) if val is not None else default
        except (ValueError, TypeError):
            return default

    def evaluate_window(
        self,
        window: List[Any],
        physical_features: Optional[Dict[str, Any]] = None,
    ) -> ConfluenceResult:
        """
        Evaluates a window of telemetry records. If trained models are present,
        runs model inference. Otherwise, uses physics-informed heuristic inference.
        """
        if not window:
            return self.evaluate_confluence(0.01, 0.01, "none")

        curr = window[-1]
        prev = window[-2] if len(window) > 1 else curr

        # Extract values supporting both dicts and Pydantic models
        curr_p = self._extract_val(curr, "pressure_hpa", 1005.0)
        prev_p = self._extract_val(prev, "pressure_hpa", 1005.0)
        curr_rh = self._extract_val(curr, "humidity_pct", 60.0)
        prev_rh = self._extract_val(prev, "humidity_pct", 60.0)
        curr_t = self._extract_val(curr, "temperature_c", 30.0)
        prev_t = self._extract_val(prev, "temperature_c", 30.0)
        wind = self._extract_val(curr, "wind_speed_ms", 2.5)
        recon_err = self._extract_val(curr, "reconstruction_error", 0.0142)

        dt_p = curr_p - prev_p
        dt_rh = curr_rh - prev_rh
        dt_t = curr_t - prev_t

        # Check physical features if provided by MultiScaleAnalyzer
        rho_t_rh = 0.0
        decoupling_flag = False
        if physical_features:
            rho_t_rh = physical_features.get("rho_t_rh", 0.0)
            decoupling_flag = physical_features.get("decoupling_flag", False)

        p_weather = 0.03
        p_defect = 0.03
        defect_type = "none"

        # 1. Run ML Model Inferences if loaded
        if self.model_a is not None:
            try:
                feat_a = np.array([[
                    curr_t,
                    curr_rh,
                    curr_p,
                    self._extract_val(curr, "dew_point_c", 20.0),
                    wind,
                    self._extract_val(curr, "wind_dir_deg", 180.0),
                    self._extract_val(curr, "solar_radiation_wm2", 450.0),
                    dt_t,
                    dt_p,
                    dt_rh,
                ]], dtype=np.float32)

                if hasattr(self.model_a, "predict_proba"):
                    probs_a = self.model_a.predict_proba(feat_a)[0]
                    classes_a = list(self.model_a.classes_)
                    squall_idx = classes_a.index("squall") if "squall" in classes_a else 1
                    p_weather = float(probs_a[squall_idx])
                elif hasattr(self.model_a, "predict"):
                    pred_a = self.model_a.predict(feat_a)[0]
                    p_weather = 0.92 if pred_a == "squall" else 0.04
            except Exception as e:
                logger.debug(f"Model A inference fallback: {e}")

        if self.model_b is not None:
            try:
                feat_b = np.array([[
                    curr_t,
                    curr_rh,
                    curr_p,
                    self._extract_val(curr, "dew_point_c", 20.0),
                    wind,
                    self._extract_val(curr, "wind_dir_deg", 180.0),
                    self._extract_val(curr, "solar_radiation_wm2", 450.0),
                    dt_t,
                    dt_p,
                    dt_rh,
                    self._extract_val(curr, "drop_flag", 0.0),
                ]], dtype=np.float32)

                if hasattr(self.model_b, "predict_proba"):
                    probs_b = self.model_b.predict_proba(feat_b)[0]
                    classes_b = list(self.model_b.classes_)
                    if "none" in classes_b:
                        none_idx = classes_b.index("none")
                        p_none = float(probs_b[none_idx])
                        p_defect = 1.0 - p_none
                    else:
                        p_defect = float(np.max(probs_b))
                    best_idx = int(np.argmax(probs_b))
                    defect_type = str(classes_b[best_idx])
                elif hasattr(self.model_b, "predict"):
                    pred_b = str(self.model_b.predict(feat_b)[0])
                    p_defect = 0.04 if pred_b == "none" else 0.92
                    defect_type = pred_b
            except Exception as e:
                logger.debug(f"Model B inference fallback: {e}")

        # 2. Meteorological & physical safety overrides (IMD & PRD specs)
        # Clear squall line signature: coupled thermodynamics (barometric plunge with RH surge & cooling, or sustained storm conditions)
        is_squall_physics = (
            (dt_p < -3.0 and dt_rh > 12.0 and dt_t < -2.0)
            or (p_weather >= 0.70 and dt_p < -1.5)
            or (curr_p <= 998.0 and curr_rh >= 88.0 and curr_t <= 26.0)
        )
        if is_squall_physics:
            p_weather = max(p_weather, min(0.98, 0.88 + (abs(dt_p) / 20.0)))
            p_defect = min(p_defect, 0.08)
            defect_type = "none"

        # Frozen sensor flatline (zero variance over 6 consecutive points)
        if len(window) >= 6:
            rh_values = [float(getattr(w, "humidity_pct", 60.0)) for w in window[-6:]]
            if np.std(rh_values) < 0.001 and float(getattr(curr, "humidity_pct", 60.0)) > 40.0:
                p_defect = max(p_defect, 0.95)
                p_weather = min(p_weather, 0.05)
                defect_type = "frozen_value"

        # Capacitive drift / Thermodynamic decoupling (elevated moisture without squall)
        curr_rh = float(getattr(curr, "humidity_pct", 50.0) if hasattr(curr, "humidity_pct") else curr.get("humidity_pct", 50.0))
        curr_t = float(getattr(curr, "temperature_c", 25.0) if hasattr(curr, "temperature_c") else curr.get("temperature_c", 25.0))
        if (defect_type == "capacitive_drift" or (decoupling_flag and curr_rh >= 65.0 and curr_t >= 22.0)) and not is_squall_physics:
            p_defect = max(p_defect, 0.92)
            p_weather = min(p_weather, 0.08)
            defect_type = "capacitive_drift"

        # Heat spike / thermal surge (valid atmospheric weather anomaly / heat burst)
        # Weather anomaly: classified as Natural Weather Event with zero false alarm on hardware sensors!
        is_heat_spike = (abs(dt_t) >= 4.0 or curr_t >= 37.5) and not is_squall_physics and curr_rh <= 75.0 and -10.0 <= curr_t <= 60.0
        if is_heat_spike:
            p_weather = max(p_weather, 0.90)
            p_defect = min(p_defect, 0.08)
            defect_type = "none"

        # Genuine physical boundary failure (impossible AWS values indicate broken hardware / open circuit)
        if curr_t < -10.0 or curr_t > 60.0 or curr_rh < 0.0 or curr_rh > 100.0 or curr_p < 850.0 or curr_p > 1080.0:
            p_defect = max(p_defect, 0.96)
            p_weather = min(p_weather, 0.04)
            if defect_type in ("none", "nominal"):
                defect_type = "impulse_spike" if (curr_t < -10.0 or curr_t > 60.0) else "noise_burst"

        # Packet dropout check
        if self._extract_val(curr, "drop_flag", 0.0) == 1.0:
            p_defect = max(p_defect, 0.92)
            defect_type = "packet_dropout"

        # Nominal Diurnal Baseline validation:
        # If Model B indicates healthy ('none') and no physical fault signature exists,
        # ensure defect probability is strictly clamped low (< 0.10).
        if defect_type == "none" and not is_squall_physics and not is_heat_spike and abs(dt_t) < 3.5 and abs(dt_p) < 2.5:
            p_defect = min(p_defect, 0.08)
            p_weather = min(p_weather, 0.10)

        return self.evaluate_confluence(p_weather, p_defect, defect_type)


confluence_engine = ConfluenceEngine()
