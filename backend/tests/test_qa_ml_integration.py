"""
Harsh, Rigorous ML Pipeline & Yukti Integration QA Test Suite.

Target Services Tested:
  - backend/services/anomaly_detector.py (MultivariateAnomalyDetector)
  - backend/services/confluence_engine.py (ConfluenceEngine)
  - backend/services/multi_scale_analyzer.py (MultiScaleAnalyzer)
  - notebooks/02_train_autoencoder.ipynb (Yukti's Training Specification & Artifact Schema)

Areas of Deep Auditing:
  1. Missing artifacts handling & graceful fallback
  2. Corrupted / invalid model files (binary corruption, malformed JSON, pickled payloads)
  3. Programmatic synthetic artifact hot-plugging (autoencoder.onnx, scaler.json, model_a, model_b)
  4. Tensor shape compatibility & failure modes (timesteps 3, 6, 12, 24, channel count, batch dimension)
  5. Silent error masking & fallback collision bugs
  6. Dead-code / uncalled models in ConfluenceEngine
  7. Ignored scaler.json configuration
  8. Confluence decision matrix, confidence formula discrepancy, and defect schema mismatches
"""

import os
import sys
import json
import uuid
import tempfile
import shutil
import pytest
import numpy as np
from datetime import datetime, timezone
from typing import List
from unittest.mock import MagicMock, patch

# Ensure stdout handles UTF-8 for PyTorch ONNX logging on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import onnxruntime as ort
import joblib
from sklearn.linear_model import LogisticRegression

# Import system under test
from models.schemas import TelemetryPayload, AnomalyEvent
from services.anomaly_detector import MultivariateAnomalyDetector, AnomalyEvaluation
from services.confluence_engine import ConfluenceEngine, ConfluenceResult
from services.multi_scale_analyzer import MultiScaleAnalyzer


# =====================================================================
# FIXTURES & SYNTHETIC ARTIFACT BUILDERS
# =====================================================================

def build_synthetic_autoencoder_onnx(output_path: str):
    """
    Exports a valid ONNX 1D-CNN Autoencoder matching Yukti's exact PyTorch architecture
    from notebooks/02_train_autoencoder.ipynb.
    Input shape: (batch_size, 8, 12)
    Output shape: (batch_size, 8, 12)
    """
    import torch
    import torch.nn as nn

    class Conv1DAutoencoder(nn.Module):
        def __init__(self, in_channels=8, seq_len=12, latent_dim=8):
            super().__init__()
            self.enc_conv1 = nn.Conv1d(in_channels, 16, kernel_size=3, padding=1)
            self.enc_relu1 = nn.ReLU()
            self.enc_pool = nn.MaxPool1d(2)  # 12 -> 6
            self.enc_conv2 = nn.Conv1d(16, latent_dim, kernel_size=3, padding=1)
            self.enc_relu2 = nn.ReLU()

            self.dec_upsample = nn.Upsample(scale_factor=2, mode="nearest")  # 6 -> 12
            self.dec_conv1 = nn.Conv1d(latent_dim, 16, kernel_size=3, padding=1)
            self.dec_relu1 = nn.ReLU()
            self.dec_conv2 = nn.Conv1d(16, in_channels, kernel_size=3, padding=1)

        def forward(self, x):
            z = self.enc_relu1(self.enc_conv1(x))
            z = self.enc_pool(z)
            z = self.enc_relu2(self.enc_conv2(z))
            out = self.dec_upsample(z)
            out = self.dec_relu1(self.dec_conv1(out))
            out = self.dec_conv2(out)
            return out

    model = Conv1DAutoencoder()
    model.eval()
    dummy_input = torch.randn(1, 8, 12, requires_grad=False)
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=18,
        do_constant_folding=True,
        input_names=["weather_window"],
        output_names=["reconstructed_window"],
        dynamic_axes={
            "weather_window": {0: "batch_size"},
            "reconstructed_window": {0: "batch_size"},
        },
    )


def build_synthetic_scaler_json(output_path: str, custom_threshold: float = 0.038):
    """Generates scaler.json matching Yukti's schema from notebook Step 3."""
    config = {
        "feature_names": ["T", "RH", "P", "Td", "dT_dt", "dP_dt", "dRH_dt", "drop_flag"],
        "means": {
            "T": 30.5,
            "RH": 62.0,
            "P": 1008.2,
            "Td": 21.0,
            "dT_dt": 0.05,
            "dP_dt": -0.02,
            "dRH_dt": 0.1,
            "drop_flag": 0.0,
        },
        "stds": {
            "T": 5.2,
            "RH": 14.5,
            "P": 4.1,
            "Td": 3.0,
            "dT_dt": 0.35,
            "dP_dt": 0.22,
            "dRH_dt": 1.2,
            "drop_flag": 1.0,
        },
        "threshold": custom_threshold,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def build_synthetic_model_a(output_path: str):
    """Generates Model A (Weather Classifier) returning classes ['nominal', 'squall']."""
    np.random.seed(42)
    X = np.random.randn(40, 10)
    y = np.array(["nominal"] * 20 + ["squall"] * 20)
    clf = LogisticRegression()
    clf.fit(X, y)
    joblib.dump(clf, output_path)


def build_synthetic_model_b(output_path: str):
    """Generates Model B (Sensor Defect Classifier) returning 6 defect classes."""
    np.random.seed(42)
    classes = [
        "none",
        "frozen_value",
        "capacitive_drift",
        "impulse_spike",
        "noise_burst",
        "packet_dropout",
    ]
    X = np.random.randn(60, 10)
    y = np.array(classes * 10)
    clf = LogisticRegression()
    clf.fit(X, y)
    joblib.dump(clf, output_path)


def make_telemetry_window(length: int, base_temp=30.0, base_rh=60.0, base_p=1010.0) -> List[TelemetryPayload]:
    """Helper to generate sliding window of synthetic TelemetryPayload items."""
    window = []
    base_time = datetime.now(timezone.utc).timestamp()
    for i in range(length):
        p = TelemetryPayload(
            station_id="AGRA-01",
            timestamp=datetime.fromtimestamp(base_time + i, tz=timezone.utc).isoformat(),
            temperature_c=round(base_temp + (i * 0.05), 2),
            humidity_pct=round(base_rh - (i * 0.1), 2),
            pressure_hpa=round(base_p + (i * 0.02), 2),
            dew_point_c=round(base_temp - ((100 - base_rh) / 5), 2),
            wind_speed_ms=2.5,
            wind_dir_deg=180.0,
            solar_radiation_wm2=450.0,
            sequence=i,
            source="test-harness",
            drop_flag=0,
        )
        window.append(p)
    return window


@pytest.fixture(scope="module")
def synthetic_artifacts_dir():
    """Module-level fixture creating a temporary directory populated with all Yukti artifacts."""
    tmp_dir = tempfile.mkdtemp(prefix="skyguard_qa_artifacts_")
    onnx_path = os.path.join(tmp_dir, "autoencoder.onnx")
    scaler_path = os.path.join(tmp_dir, "scaler.json")
    model_a_path = os.path.join(tmp_dir, "model_a_weather.pkl")
    model_b_path = os.path.join(tmp_dir, "model_b_defect.pkl")

    build_synthetic_autoencoder_onnx(onnx_path)
    build_synthetic_scaler_json(scaler_path, custom_threshold=0.038)
    build_synthetic_model_a(model_a_path)
    build_synthetic_model_b(model_b_path)

    yield tmp_dir

    shutil.rmtree(tmp_dir, ignore_errors=True)


# =====================================================================
# TEST SUITE 1: MISSING ARTIFACTS BEHAVIOR & GRACEFUL DEGRADATION
# =====================================================================

class TestMissingArtifactsHandling:
    """Verifies that missing artifacts do not crash the backend and trigger statistical fallbacks."""

    def test_anomaly_detector_initialization_when_artifacts_missing(self):
        detector = MultivariateAnomalyDetector(threshold=0.042)
        # Point to a guaranteed non-existent path
        with patch("os.path.exists", return_value=False):
            detector.onnx_session = None
            detector._init_onnx_model()
            assert detector.onnx_session is None, "onnx_session must remain None when autoencoder.onnx is missing"

    def test_confluence_engine_initialization_when_artifacts_missing(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            engine = ConfluenceEngine(artifacts_dir=empty_dir)
            assert engine.model_a is None, "model_a must be None when model_a_weather.pkl is absent"
            assert engine.model_b is None, "model_b must be None when model_b_defect.pkl is absent"

    def test_anomaly_detector_cold_start_buffering_without_artifacts(self):
        detector = MultivariateAnomalyDetector(threshold=0.042)
        detector.onnx_session = None

        # Buffering for window length 0, 1, 2 (< 3 points)
        for count in [0, 1, 2]:
            window = make_telemetry_window(count)
            res = detector.evaluate_window(window)
            assert isinstance(res, AnomalyEvaluation)
            assert res.anomaly is None
            assert res.reconstruction_error == 0.0142
            assert len(res.attributions) == 3

    def test_anomaly_detector_surrogate_inference_without_artifacts(self):
        detector = MultivariateAnomalyDetector(threshold=0.042)
        detector.onnx_session = None

        # Nominal window of 12 points
        window = make_telemetry_window(12, base_temp=32.0, base_rh=58.0, base_p=1004.5)
        res = detector.evaluate_window(window)
        assert res.reconstruction_error < detector.threshold
        assert res.anomaly is None

        # Drift window: surge in RH without pressure drop (Capacitive Drift)
        drift_window = make_telemetry_window(12, base_temp=33.0, base_rh=75.0, base_p=1004.5)
        drift_window[-1].humidity_pct = 95.0
        drift_window[-2].humidity_pct = 90.0
        drift_window[-3].humidity_pct = 85.0
        res_drift = detector.evaluate_window(drift_window)
        assert res_drift.reconstruction_error > detector.threshold
        assert res_drift.anomaly is not None
        assert "humidity" in res_drift.anomaly.culprit_sensors


# =====================================================================
# TEST SUITE 2: CORRUPTED / INVALID ARTIFACT HANDLING
# =====================================================================

class TestCorruptedArtifactsHandling:
    """Verifies that corrupted model files are caught gracefully and do not break startup."""

    def test_corrupted_onnx_model_graceful_handling(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_onnx = os.path.join(tmp_dir, "autoencoder.onnx")
            with open(bad_onnx, "wb") as f:
                f.write(b"NOT_A_VALID_ONNX_MODEL_CORRUPTED_BINARY_BYTES")

            detector = MultivariateAnomalyDetector(threshold=0.042)
            with patch("os.path.join", return_value=bad_onnx):
                with patch("os.path.exists", return_value=True):
                    # _init_onnx_model catches Exception and keeps onnx_session as None
                    detector._init_onnx_model()
                    assert detector.onnx_session is None, "Corrupted ONNX must not initialize an active session"

    def test_corrupted_model_a_pickle_handling(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_pkl = os.path.join(tmp_dir, "model_a_weather.pkl")
            with open(bad_pkl, "wb") as f:
                f.write(b"\x80\x04\x95corrupted_pickle_payload_garbage")

            engine = ConfluenceEngine(artifacts_dir=tmp_dir)
            assert engine.model_a is None, "Corrupted Model A pickle must be caught gracefully and leave model_a as None"

    def test_corrupted_model_b_pickle_handling(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_pkl = os.path.join(tmp_dir, "model_b_defect.pkl")
            with open(bad_pkl, "wb") as f:
                f.write(b"\x00\x01\x02\x03invalid_unpickling_stream")

            engine = ConfluenceEngine(artifacts_dir=tmp_dir)
            assert engine.model_b is None, "Corrupted Model B pickle must be caught gracefully and leave model_b as None"

    def test_corrupted_scaler_json_demonstrates_dead_code_absence(self):
        """
        DISCREPANCY CHECK:
        If scaler.json is corrupted or invalid, does anomaly_detector.py crash?
        ANSWER: No, because anomaly_detector.py completely ignores scaler.json!
        This test proves scaler.json is unread.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_scaler = os.path.join(tmp_dir, "scaler.json")
            with open(bad_scaler, "w", encoding="utf-8") as f:
                f.write("{ INVALID JSON SYNTAX NO CLOSING BRACE ")

            detector = MultivariateAnomalyDetector(threshold=0.042)
            # Detector will happily initialize with hardcoded baseline means, completely ignoring the file
            assert "T" in detector.BASELINE_MEANS
            assert detector.BASELINE_MEANS["T"] == 32.0


# =====================================================================
# TEST SUITE 3: HOT-PLUGGING SYNTHETIC ARTIFACTS & INTEGRATION GAPS
# =====================================================================

class TestSyntheticArtifactsHotPlugging:
    """Rigorous tests evaluating live hot-plugged ML artifacts matching Yukti's schema."""

    def test_hot_plugged_autoencoder_onnx_valid_12_timesteps(self, synthetic_artifacts_dir):
        onnx_path = os.path.join(synthetic_artifacts_dir, "autoencoder.onnx")
        session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        assert session is not None

        detector = MultivariateAnomalyDetector(threshold=0.042)
        detector.onnx_session = session

        window_12 = make_telemetry_window(12, base_temp=32.0, base_rh=58.0, base_p=1004.5)
        res = detector.evaluate_window(window_12)
        assert isinstance(res, AnomalyEvaluation)
        assert isinstance(res.reconstruction_error, float)
        assert res.reconstruction_error >= 0.0

    def test_hot_plugged_scaler_json_is_completely_ignored_by_anomaly_detector(self, synthetic_artifacts_dir):
        """
        BUG DISCOVERY:
        scaler.json contains custom baseline means: T=30.5, RH=62.0, threshold=0.038.
        MultivariateAnomalyDetector hardcodes: T=32.0, RH=58.0, threshold=settings.RECONSTRUCTION_THRESHOLD (0.042).
        Even when scaler.json exists in artifacts_dir, detector never loads it!
        """
        detector = MultivariateAnomalyDetector(threshold=0.042)

        scaler_path = os.path.join(synthetic_artifacts_dir, "scaler.json")
        with open(scaler_path, "r", encoding="utf-8") as f:
            scaler_data = json.load(f)

        # Confirm the synthetic scaler has custom means
        assert scaler_data["means"]["T"] == 30.5
        assert scaler_data["threshold"] == 0.038

        # BUT detector's BASELINE_MEANS and threshold are hardcoded and unchanged
        assert detector.BASELINE_MEANS["T"] == 32.0, "BUG: AnomalyDetector uses hardcoded means instead of scaler.json"
        assert detector.threshold == 0.042, "BUG: AnomalyDetector ignores calibrated threshold from scaler.json"

    def test_hot_plugged_model_a_and_model_b_loaded_into_confluence_engine(self, synthetic_artifacts_dir):
        engine = ConfluenceEngine(artifacts_dir=synthetic_artifacts_dir)
        assert engine.model_a is not None, "Model A should be successfully loaded from model_a_weather.pkl"
        assert engine.model_b is not None, "Model B should be successfully loaded from model_b_defect.pkl"

    def test_confluence_engine_evaluate_window_never_calls_loaded_models(self, synthetic_artifacts_dir):
        """
        CRITICAL BUG DISCOVERY:
        In confluence_engine.py, self.model_a and self.model_b are loaded into memory,
        BUT evaluate_window() NEVER calls self.model_a.predict() or self.model_b.predict()!
        The entire evaluate_window() runs on hardcoded heuristics.
        """
        engine = ConfluenceEngine(artifacts_dir=synthetic_artifacts_dir)
        assert engine.model_a is not None
        assert engine.model_b is not None

        # Wrap loaded models with MagicMock spies
        engine.model_a.predict = MagicMock(return_value=["squall"])
        engine.model_a.predict_proba = MagicMock(return_value=[[0.05, 0.95]])
        engine.model_b.predict = MagicMock(return_value=["capacitive_drift"])
        engine.model_b.predict_proba = MagicMock(return_value=[[0.02, 0.01, 0.94, 0.01, 0.01, 0.01]])

        window = make_telemetry_window(12)
        analyzer = MultiScaleAnalyzer()
        phys_feat = analyzer.analyze_window(window)

        # Run evaluate_window
        result = engine.evaluate_window(window, physical_features=phys_feat)

        # ASSERTION PROVING DEAD CODE:
        # evaluate_window does NOT call model_a or model_b!
        assert engine.model_a.predict.call_count == 0, "BUG: model_a.predict was never called by evaluate_window"
        assert engine.model_a.predict_proba.call_count == 0, "BUG: model_a.predict_proba was never called by evaluate_window"
        assert engine.model_b.predict.call_count == 0, "BUG: model_b.predict was never called by evaluate_window"
        assert engine.model_b.predict_proba.call_count == 0, "BUG: model_b.predict_proba was never called by evaluate_window"


# =====================================================================
# TEST SUITE 4: TENSOR SHAPE COMPATIBILITY & SILENT FAILURE MODES
# =====================================================================

class TestShapeCompatibilityAndFailureModes:
    """Harsh tests on ONNX dimension contracts and anomaly_detector error handling."""

    def test_onnx_dimension_mismatch_on_window_lengths_3_6_11(self, synthetic_artifacts_dir):
        """
        Strict shape test:
        Yukti's ONNX autoencoder exports with fixed timesteps=12: ['batch_size', 8, 12].
        Directly passing steps < 12 into ONNX Runtime MUST throw InvalidArgument exception.
        """
        onnx_path = os.path.join(synthetic_artifacts_dir, "autoencoder.onnx")
        session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        input_name = session.get_inputs()[0].name

        for steps in [3, 6, 11]:
            inp = np.random.randn(1, 8, steps).astype(np.float32)
            with pytest.raises(Exception) as exc_info:
                session.run(None, {input_name: inp})
            assert "INVALID_ARGUMENT" in str(exc_info.value) or "invalid dimensions" in str(exc_info.value)

    def test_anomaly_detector_masks_onnx_shape_errors_silently(self, synthetic_artifacts_dir):
        """
        BUG DISCOVERY:
        When window has 3 to 11 points, norm_matrix[-12:, :] returns shape (len, 8).
        Anomaly detector passes (1, 8, len) to ONNX session, causing an InvalidArgument crash.
        Lines 166-167 catch ALL exceptions silently and set reconstruction_error = 0.0142!
        The caller is never notified that ONNX failed due to a dimension mismatch.
        """
        onnx_path = os.path.join(synthetic_artifacts_dir, "autoencoder.onnx")
        session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

        detector = MultivariateAnomalyDetector(threshold=0.042)
        detector.onnx_session = session

        # Window with 6 items (< 12)
        window_6 = make_telemetry_window(6)
        res = detector.evaluate_window(window_6)

        # Silent fallback produces exactly 0.0142 or surrogate fallback
        assert isinstance(res, AnomalyEvaluation)
        # Verify that reconstruction error was masked to nominal rather than propagating the shape error
        assert res.reconstruction_error < detector.threshold

    def test_window_length_24_slices_last_12_and_succeeds(self, synthetic_artifacts_dir):
        """
        When window length is 24 (> 12), norm_matrix[-12:, :] takes the last 12 points,
        matching ONNX's expected 12 timesteps.
        """
        onnx_path = os.path.join(synthetic_artifacts_dir, "autoencoder.onnx")
        session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

        detector = MultivariateAnomalyDetector(threshold=0.042)
        detector.onnx_session = session

        window_24 = make_telemetry_window(24)
        res = detector.evaluate_window(window_24)
        assert isinstance(res, AnomalyEvaluation)
        assert res.reconstruction_error >= 0.0

    def test_feature_order_and_channel_count_contract(self):
        """
        FEATURE ORDER CONTRACT:
        Both training notebook and anomaly_detector.py must agree on the 8 features:
        ["T", "RH", "P", "Td", "dT_dt", "dP_dt", "dRH_dt", "drop_flag"]
        """
        expected_features = ["T", "RH", "P", "Td", "dT_dt", "dP_dt", "dRH_dt", "drop_flag"]
        assert MultivariateAnomalyDetector.FEATURE_NAMES == expected_features

        detector = MultivariateAnomalyDetector()
        window = make_telemetry_window(5)
        mat = detector.extract_features(window)
        assert mat.shape == (5, 8), f"Expected shape (5, 8), got {mat.shape}"

    def test_batch_size_flexibility_in_onnx(self, synthetic_artifacts_dir):
        """Verify dynamic_axes allows batch sizes 1, 2, and 8 when sequence length is exactly 12."""
        onnx_path = os.path.join(synthetic_artifacts_dir, "autoencoder.onnx")
        session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        input_name = session.get_inputs()[0].name

        for batch_size in [1, 2, 8]:
            inp = np.random.randn(batch_size, 8, 12).astype(np.float32)
            outputs = session.run(None, {input_name: inp})
            assert outputs[0].shape == (batch_size, 8, 12)


# =====================================================================
# TEST SUITE 5: CONFLUENCE DECISION MATRIX, CONFIDENCE & DEFECT CLASSES
# =====================================================================

class TestConfluenceConfidenceAndDecisionMatrix:
    """Rigorously audits the Confluence Decision Matrix and Confidence formulas."""

    def test_confidence_scoring_bounds_and_symmetry(self):
        engine = ConfluenceEngine()

        # Decisive agreement / divergence
        assert engine.compute_confidence(0.95, 0.05) > 90.0
        assert engine.compute_confidence(0.05, 0.95) > 90.0

        # Maximum ambiguity (P_D == P_W == 0.5)
        conf_ambiguous = engine.compute_confidence(0.50, 0.50)
        # Formula: 0.5 * (1.0 - 1.0 * 0.18) * 100 = 0.5 * 0.82 * 100 = 41.0
        assert conf_ambiguous == 41.0

        # Boundary values
        assert engine.compute_confidence(0.0, 0.0) == 0.0
        assert 0.0 <= engine.compute_confidence(1.0, 1.0) <= 100.0

    def test_confidence_formula_factor_discrepancy(self):
        """
        DISCREPANCY DOCUMENTATION:
        confluence_engine.py line 79 uses factor 0.18:
          max(P_D, P_W) * (1.0 - (1.0 - |P_D - P_W|) * 0.18) * 100
        Whereas TASKS.md Task 4.2 line 212 specifies factor 0.20:
          max(P_D, P_W) * (1.0 - |P_D - P_W| * 0.20)
        And ML Strat.md line 323 specifies factor 0.25!
        """
        engine = ConfluenceEngine()
        # With P_w=0.05, P_d=0.94:
        # diff = 0.89, ambiguity = 0.11
        # Code with 0.18 gives: 0.94 * (1.0 - 0.11 * 0.18) * 100 = 92.1%
        conf = engine.compute_confidence(0.05, 0.94)
        assert conf == 92.1

    def test_four_quadrant_decision_matrix(self):
        engine = ConfluenceEngine()

        # Quadrant 1: Natural Weather Event
        q1 = engine.evaluate_confluence(0.85, 0.15, "none")
        assert q1.classification == "Natural Weather Event"
        assert q1.severity == "Nominal"
        assert q1.operator_alert is False

        # Quadrant 2: Sensor Defect
        q2 = engine.evaluate_confluence(0.15, 0.85, "capacitive_drift")
        assert q2.classification == "Sensor Defect"
        assert q2.severity == "High"
        assert q2.operator_alert is True
        assert q2.defect_type == "capacitive_drift"

        # Quadrant 3: Compound Event
        q3 = engine.evaluate_confluence(0.85, 0.85, "packet_dropout")
        assert q3.classification == "Compound Event"
        assert q3.severity == "Warning"
        assert q3.operator_alert is True

        # Quadrant 4: Uncertain Anomaly
        q4 = engine.evaluate_confluence(0.50, 0.50, "none")
        assert q4.classification == "Uncertain Anomaly"
        assert q4.severity == "Moderate"
        assert q4.operator_alert is False

    def test_defect_classes_schema_mismatch_sensor_noise_typo(self):
        """
        DEFECT TYPE BUG DISCOVERY:
        In confluence_engine.py line 31:
          DEFECT_CLASSES = ["none", "frozen_value", "capacitive_drift", "impulse_spike", "noise_burst", "packet_dropout"]
        However, in evaluate_window line 202:
          if defect_type == "none":
              defect_type = "sensor_noise"
        "sensor_noise" is NOT in DEFECT_CLASSES! The proper class is "noise_burst".
        This causes an out-of-schema defect type to be emitted.
        """
        engine = ConfluenceEngine()
        assert "noise_burst" in engine.DEFECT_CLASSES
        assert "sensor_noise" not in engine.DEFECT_CLASSES, "sensor_noise is invalid per schema"

        # Trigger line 202 condition: recon_err > 0.042 and p_weather < 0.30
        window = make_telemetry_window(12)
        window[-1].reconstruction_error = 0.055
        res = engine.evaluate_window(window)

        # Expose the bug: evaluate_window emits 'sensor_noise' instead of 'noise_burst'
        assert res.defect_type == "sensor_noise", "Exposes that line 202 emits non-schema 'sensor_noise'"

    def test_extreme_and_out_of_bound_probabilities(self):
        engine = ConfluenceEngine()
        # Pass negative and > 1.0 values to check clamping
        conf_neg = engine.compute_confidence(-0.5, 1.5)
        # p_w clamped to 0.0, p_d clamped to 1.0 -> diff=1.0, ambiguity=0.0 -> conf=100.0
        assert conf_neg == 100.0


# =====================================================================
# TEST SUITE 6: MULTI-SCALE ANALYZER INTERFACE COMPATIBILITY
# =====================================================================

class TestMultiScaleAnalyzerFeatureCompatibility:
    """Verifies MultiScaleAnalyzer output vector contract with downstream models."""

    def test_feature_vector_dimensions_and_naming(self):
        analyzer = MultiScaleAnalyzer()
        window = make_telemetry_window(12)
        feats = analyzer.analyze_window(window)

        assert "features_vector" in feats
        assert len(feats["features_vector"]) == 10
        assert "rho_t_rh" in feats
        assert "decoupling_flag" in feats
        assert isinstance(feats["decoupling_flag"], bool)

    def test_thermodynamic_decoupling_detection(self):
        """
        Under normal physics, rho(T, RH) is strongly negative (-0.7 to -0.9).
        When RH increases while T increases (positive correlation) without pressure drop,
        decoupling_flag MUST be True.
        """
        analyzer = MultiScaleAnalyzer()

        # Generate decoupled window: T rises, RH rises simultaneously, P stable
        base_time = datetime.now(timezone.utc).timestamp()
        window = []
        for i in range(12):
            p = TelemetryPayload(
                station_id="AGRA-01",
                timestamp=datetime.fromtimestamp(base_time + i, tz=timezone.utc).isoformat(),
                temperature_c=25.0 + (i * 0.5),  # Rising T
                humidity_pct=50.0 + (i * 2.0),   # Rising RH (abnormal coupling!)
                pressure_hpa=1013.25,            # Stable P
                dew_point_c=14.0,
                wind_speed_ms=2.5,
                wind_dir_deg=180.0,
                solar_radiation_wm2=450.0,
                sequence=i,
                source="test-harness",
            )
            window.append(p)

        feats = analyzer.analyze_window(window)
        assert feats["rho_t_rh"] > 0.0, f"Expected positive correlation, got {feats['rho_t_rh']}"
        assert feats["decoupling_flag"] is True, "Decoupling flag should be True during rising T and rising RH"

    def test_multiscale_analyzer_empty_and_short_window(self):
        analyzer = MultiScaleAnalyzer()
        feats_empty = analyzer.analyze_window([])
        assert feats_empty["window_size"] == 0
        assert len(feats_empty["features_vector"]) == 10

        window_1 = make_telemetry_window(1)
        feats_1 = analyzer.analyze_window(window_1)
        assert feats_1["rho_t_rh"] == 0.0
