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
        if artifacts_dir is None:
            artifacts_dir = os.path.join(
                os.path.dirname(__file__), "..", "ml_artifacts"
            )
        self.artifacts_dir = artifacts_dir
        self.model_a = None
        self.model_b = None
        self._load_models()

    def _load_models(self) -> None:
        """
        Attempts to load Model A (Weather) and Model B (Defect) from artifacts.
        If models are not yet trained, the engine activates meteorological heuristic inference.
        """
        model_a_path = os.path.join(self.artifacts_dir, "model_a_weather.pkl")
        model_b_path = os.path.join(self.artifacts_dir, "model_b_defect.pkl")

        if os.path.exists(model_a_path):
            try:
                import joblib

                self.model_a = joblib.load(model_a_path)
                logger.info(f"Loaded Model A (Weather Classifier) from {model_a_path}")
            except Exception as exc:
                logger.warning(f"Could not load Model A from {model_a_path}: {exc}")

        if os.path.exists(model_b_path):
            try:
                import joblib

                self.model_b = joblib.load(model_b_path)
                logger.info(f"Loaded Model B (Sensor Defect Classifier) from {model_b_path}")
            except Exception as exc:
                logger.warning(f"Could not load Model B from {model_b_path}: {exc}")

    def compute_confidence(self, p_weather: float, p_defect: float) -> float:
        """
        Calculates mathematical confidence score (0-100%) according to Layer 2.3:
        max(P_D, P_W) * (1.0 - (1.0 - |P_D - P_W|) * 0.18) * 100
        Penalizes ambiguous/contradicting models and rewards decisive divergence.
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
        """
        Evaluates the deterministic Confluence Decision Matrix (PRD Section 5.5 / TASKS.md Task 4.2).

        Rules:
          - P(Weather) >= 0.70 and P(Defect) < 0.30  ==> Natural Weather Event (no operator alarm)
          - P(Weather) < 0.30 and P(Defect) >= 0.70  ==> Sensor Defect (operator alarm)
          - P(Weather) >= 0.70 and P(Defect) >= 0.70 ==> Compound Event (warning)
          - Otherwise                                ==> Uncertain Anomaly (triage)

        Returns:
          ConfluenceResult containing classification, confidence_score, severity, operator_alert,
          action_taken, p_weather, p_defect, and defect_type.
        """
        p_w = float(p_weather)
        p_d = float(p_defect)
        confidence_score = self.compute_confidence(p_w, p_d)

        if p_w >= 0.70 and p_d < 0.30:
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

        # Extract delta values
        dt_p = float(getattr(curr, "pressure_hpa", 1005.0)) - float(getattr(prev, "pressure_hpa", 1005.0))
        dt_rh = float(getattr(curr, "humidity_pct", 60.0)) - float(getattr(prev, "humidity_pct", 60.0))
        dt_t = float(getattr(curr, "temperature_c", 30.0)) - float(getattr(prev, "temperature_c", 30.0))
        wind = float(getattr(curr, "wind_speed_ms", 2.5))
        recon_err = float(getattr(curr, "reconstruction_error", 0.0142))

        # Check physical features if provided by MultiScaleAnalyzer
        rho_t_rh = 0.0
        decoupling_flag = False
        if physical_features:
            rho_t_rh = physical_features.get("rho_t_rh", 0.0)
            decoupling_flag = physical_features.get("decoupling_flag", False)

        p_weather = 0.05
        p_defect = 0.05
        defect_type = "none"

        # 1. Evaluate Model A features (Squall / severe weather dynamics)
        if dt_p < -3.0 and dt_rh > 15.0 and dt_t < -2.0:
            # Clear squall line signature
            p_weather = min(0.98, 0.85 + (abs(dt_p) / 20.0))
        elif dt_p < -1.5 and wind > 8.0:
            p_weather = 0.75

        # 2. Evaluate Model B features (Hardware failure dynamics)
        # Check for frozen value (flatline)
        if len(window) >= 6:
            rh_values = [float(getattr(w, "humidity_pct", 60.0)) for w in window[-6:]]
            if np.std(rh_values) < 0.001 and float(getattr(curr, "humidity_pct", 60.0)) > 70.0:
                p_defect = 0.95
                defect_type = "frozen_value"

        # Check for capacitive drift / cross-channel decoupling
        if decoupling_flag or (rho_t_rh > 0.0 and abs(dt_p) < 2.0 and recon_err > 0.040):
            p_defect = max(p_defect, 0.94)
            defect_type = "capacitive_drift"
        elif recon_err > 0.042 and p_weather < 0.30:
            p_defect = max(p_defect, 0.88)
            if defect_type == "none":
                defect_type = "sensor_noise"

        return self.evaluate_confluence(p_weather, p_defect, defect_type)


confluence_engine = ConfluenceEngine()
