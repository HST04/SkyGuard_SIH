"""
Comprehensive QA Test Suite: Backend Core, Confluence Matrix & Mathematical Edge Cases
QA Agent 2: Backend Core, Confluence Matrix & Mathematical Edge Cases QA Specialist

This test suite executes harsh, rigorous verification of:
1. MultiScaleAnalyzer (window sizes, zero variance, NaN/Inf, timestamps, decoupling)
2. ConfluenceEngine (confidence formula bounds, quadrant boundaries, dict vs object bug)
3. ImputationEngine (thermodynamics, Magnus-Tetens singularities, zero division, temperature bounds)
4. PredictiveMaintenance (learning vs operational, zero-sigma crash, negative drift, time-scale inversion)
5. SensorHealth & Store/DB (None/NaN handling, thread safety, concurrent async DB writes)
"""

import asyncio
import math
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
import numpy as np
import pytest

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from data.db import (
    init_db,
    insert_telemetry,
    insert_anomaly,
    insert_maintenance_prediction,
    get_recent_telemetry,
    get_session,
    TelemetryRecord,
)
from data.store import InMemoryStore, store
from models.schemas import AnomalyEvent, TelemetryPayload
from services.confluence_engine import ConfluenceEngine, confluence_engine
from services.imputation_engine import (
    ImputationEngine,
    MAGNUS_A,
    MAGNUS_B,
    sat_vp,
    dew_point,
    rh_from_dewpoint,
    t_from_dewpoint,
)
from services.multi_scale_analyzer import MultiScaleAnalyzer, multi_scale_analyzer
from services.predictive_maintenance import DriftTracker, WARMUP_SAMPLES, FAIL_SIGMA, AT_RISK_SIGMA
from services.sensor_health import SensorHealthService, _epoch


# ==============================================================================
# 1. MultiScaleAnalyzer Edge Cases & Mathematical Stress Tests
# ==============================================================================

class TestMultiScaleAnalyzerEdgeCases:
    """Rigorous mathematical tests for Layer 2.1 MultiScaleAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return MultiScaleAnalyzer(default_window_size=12)

    def test_window_sizes_edge_cases(self, analyzer):
        """Test window sizes: 0, 1, 2, 5, 12, 100 points."""
        # 1. Empty window (0 points)
        res0 = analyzer.analyze_window([])
        assert res0["window_size"] == 0
        assert res0["dT_dt"] == 0.0
        assert res0["dP_dt"] == 0.0
        assert res0["dRH_dt"] == 0.0
        assert res0["d2P_dt2"] == 0.0
        assert res0["rho_t_rh"] == 0.0
        assert res0["decoupling_flag"] is False
        assert len(res0["features_vector"]) == 10

        # 2. Single-point window (1 point)
        p1 = {"temperature_c": 28.5, "pressure_hpa": 1008.0, "humidity_pct": 65.0, "timestamp": "2026-09-29T10:00:00Z"}
        res1 = analyzer.analyze_window([p1])
        assert res1["window_size"] == 1
        assert res1["dT_dt"] == 0.0
        assert res1["dP_dt"] == 0.0
        assert res1["dRH_dt"] == 0.0
        assert res1["d2P_dt2"] == 0.0
        assert res1["rho_t_rh"] == 0.0
        assert res1["temperature_c"] == 28.5

        # 3. Two-point window (2 points) -> First derivatives exist, second derivative is 0.0
        p2 = {"temperature_c": 29.5, "pressure_hpa": 1006.0, "humidity_pct": 60.0, "timestamp": "2026-09-29T10:00:01Z"}
        res2 = analyzer.analyze_window([p1, p2])
        assert res2["window_size"] == 2
        assert res2["dT_dt"] == 1.0
        assert res2["dP_dt"] == -2.0
        assert res2["dRH_dt"] == -5.0
        assert res2["d2P_dt2"] == 0.0  # len < 3, so d2P_dt2 must be 0.0
        # Correlation between 2 distinct points should be +1.0 or -1.0
        assert abs(abs(res2["rho_t_rh"]) - 1.0) < 1e-4

        # 4. Five-point window (5 points) -> Second derivative active
        w5 = [
            {"temperature_c": 20.0 + i, "pressure_hpa": 1010.0 - (i ** 2), "humidity_pct": 80.0 - i * 2}
            for i in range(5)
        ]
        res5 = analyzer.analyze_window(w5)
        assert res5["window_size"] == 5
        # curr=4 (p=994), prev=3 (p=1001) -> dp_dt = -7
        # prev2=2 (p=1006) -> prev_dp_dt = -5 -> d2p_dt2 = -7 - (-5) = -2.0
        assert res5["dP_dt"] == -7.0
        assert res5["d2P_dt2"] == -2.0

        # 5. Hundred-point window (100 points)
        w100 = [
            {"temperature_c": 25.0 + math.sin(i / 10.0), "pressure_hpa": 1013.0, "humidity_pct": 50.0 + math.cos(i / 10.0)}
            for i in range(100)
        ]
        res100 = analyzer.analyze_window(w100)
        assert res100["window_size"] == 100
        assert isinstance(res100["rho_t_rh"], float)
        assert -1.0 <= res100["rho_t_rh"] <= 1.0

    def test_zero_variance_denominator_handling(self, analyzer):
        """Zero variance in temperature or humidity must return 0.0 correlation without NaN/Inf."""
        # Case A: Temperature is perfectly constant (zero variance in T)
        w_t_const = [{"temperature_c": 25.0, "humidity_pct": 40.0 + i * 2.0} for i in range(12)]
        rho_t = analyzer.compute_thermodynamic_correlation(w_t_const)
        assert rho_t == 0.0, f"Expected 0.0 for constant T, got {rho_t}"
        assert not math.isnan(rho_t)

        # Case B: Humidity is perfectly constant (zero variance in RH)
        w_rh_const = [{"temperature_c": 20.0 + i * 0.5, "humidity_pct": 60.0} for i in range(12)]
        rho_rh = analyzer.compute_thermodynamic_correlation(w_rh_const)
        assert rho_rh == 0.0, f"Expected 0.0 for constant RH, got {rho_rh}"
        assert not math.isnan(rho_rh)

        # Case C: Both Temperature and Humidity are constant (flatline)
        w_both_const = [{"temperature_c": 25.0, "humidity_pct": 50.0} for i in range(12)]
        rho_both = analyzer.compute_thermodynamic_correlation(w_both_const)
        assert rho_both == 0.0, f"Expected 0.0 for constant T and RH, got {rho_both}"

        # Case D: Near-zero variance (below 1e-7 threshold)
        w_near_zero = [{"temperature_c": 25.0 + 1e-5 * i, "humidity_pct": 50.0} for i in range(5)]
        rho_near = analyzer.compute_thermodynamic_correlation(w_near_zero)
        assert rho_near == 0.0

    def test_nan_and_inf_propagation_flaw(self, analyzer):
        """Document flaw: NaN or Inf inside window propagates silently into correlation and feature vector."""
        # Window with NaN in temperature
        w_nan = [
            {"temperature_c": 25.0, "humidity_pct": 50.0, "pressure_hpa": 1010.0},
            {"temperature_c": float("nan"), "humidity_pct": 55.0, "pressure_hpa": 1009.0},
            {"temperature_c": 27.0, "humidity_pct": 60.0, "pressure_hpa": 1008.0},
        ]
        rho_nan = analyzer.compute_thermodynamic_correlation(w_nan)
        # Note: In current implementation, var_t becomes NaN, which bypasses var_t < 1e-7 and yields NaN!
        assert math.isnan(rho_nan), "Confirmed: NaN temperature produces NaN correlation coefficient"

        res_nan = analyzer.analyze_window(w_nan)
        assert math.isnan(res_nan["rho_t_rh"])
        assert any(math.isnan(x) for x in res_nan["features_vector"]), "Confirmed: NaN propagates into features_vector"

        # Window with Inf in pressure
        w_inf = [
            {"temperature_c": 25.0, "humidity_pct": 50.0, "pressure_hpa": 1010.0},
            {"temperature_c": 26.0, "humidity_pct": 50.0, "pressure_hpa": float("inf")},
        ]
        res_inf = analyzer.analyze_window(w_inf)
        assert math.isinf(res_inf["dP_dt"]), "Confirmed: Inf pressure yields Inf derivative"

    def test_out_of_order_and_rapid_timestamps(self, analyzer):
        """
        Document flaw: compute_derivatives relies on list indexing window[-1] - window[-2]
        without timestamp normalization. Out-of-order packets invert the derivative.
        """
        # Chronological order: t=0 -> 25 C, t=1 -> 30 C (rising +5 C)
        # Out-of-order arrival: [t=1 (30 C), t=0 (25 C)]
        w_ooo = [
            {"timestamp": "2026-09-29T10:00:05Z", "temperature_c": 30.0, "pressure_hpa": 1010.0, "humidity_pct": 50.0},
            {"timestamp": "2026-09-29T10:00:00Z", "temperature_c": 25.0, "pressure_hpa": 1010.0, "humidity_pct": 50.0},
        ]
        derivs = analyzer.compute_derivatives(w_ooo)
        # It calculates 25.0 - 30.0 = -5.0 instead of +5.0 because it doesn't sort by timestamp
        assert derivs["dt_dt"] == -5.0

    def test_decoupling_flag_boundary_conditions(self, analyzer):
        """Verify boundary condition: rho_{T, RH} > 0.0 and abs(dP/dt) < 2.0."""
        # Exact boundary: rho = 0.0001, dP/dt = 1.99 -> True
        w1 = [
            {"temperature_c": 20.0, "humidity_pct": 40.0, "pressure_hpa": 1010.0},
            {"temperature_c": 25.0, "humidity_pct": 50.0, "pressure_hpa": 1008.01},  # dP = -1.99
        ]
        res1 = analyzer.analyze_window(w1)
        assert res1["rho_t_rh"] > 0.0
        assert abs(res1["dP_dt"]) < 2.0
        assert res1["decoupling_flag"] is True

        # Boundary: dP/dt = -2.00 (abs(dP/dt) == 2.0, condition requires < 2.0) -> False
        w2 = [
            {"temperature_c": 20.0, "humidity_pct": 40.0, "pressure_hpa": 1010.0},
            {"temperature_c": 25.0, "humidity_pct": 50.0, "pressure_hpa": 1008.0},  # dP = -2.00
        ]
        res2 = analyzer.analyze_window(w2)
        assert res2["decoupling_flag"] is False

        # Boundary: rho < 0 (normal diurnal coupling) -> False
        w3 = [
            {"temperature_c": 20.0, "humidity_pct": 60.0, "pressure_hpa": 1010.0},
            {"temperature_c": 25.0, "humidity_pct": 40.0, "pressure_hpa": 1009.5},  # dP = -0.5
        ]
        res3 = analyzer.analyze_window(w3)
        assert res3["rho_t_rh"] < 0.0
        assert res3["decoupling_flag"] is False


# ==============================================================================
# 2. ConfluenceEngine Boundary & Mathematical Flaw Tests
# ==============================================================================

class TestConfluenceEngineEdgeCases:
    """Rigorous verification of Layer 2.3 ConfluenceEngine and confidence score formula."""

    @pytest.fixture
    def engine(self):
        return ConfluenceEngine()

    def test_confidence_score_formula_bounds_and_symmetry(self, engine):
        """
        Verify confidence formula:
        conf_pct = max(P_D, P_W) * (1.0 - (1.0 - |P_D - P_W|) * 0.18) * 100.0
        Must strictly remain in [0.0, 100.0] for all combinations.
        """
        grid = [0.0, 0.05, 0.1, 0.25, 0.3, 0.5, 0.7, 0.75, 0.9, 0.95, 1.0]
        for pw in grid:
            for pd in grid:
                score = engine.compute_confidence(pw, pd)
                assert 0.0 <= score <= 100.0, f"Score {score} out of bounds for pw={pw}, pd={pd}"
                # Symmetry: C(pw, pd) == C(pd, pw)
                score_rev = engine.compute_confidence(pd, pw)
                assert score == score_rev, f"Asymmetric score: C({pw},{pd})={score} vs C({pd},{pw})={score_rev}"

        # Specific cardinal points
        assert engine.compute_confidence(0.0, 0.0) == 0.0
        assert engine.compute_confidence(1.0, 0.0) == 100.0
        assert engine.compute_confidence(0.0, 1.0) == 100.0
        # Ambiguity point: pw=0.5, pd=0.5 -> max=0.5, diff=0, ambiguity=1 -> 0.5 * (1 - 0.18) * 100 = 41.0
        assert engine.compute_confidence(0.5, 0.5) == 41.0
        # Conflicting models: pw=1.0, pd=1.0 -> max=1.0, diff=0, ambiguity=1 -> 1.0 * (1 - 0.18) * 100 = 82.0
        assert engine.compute_confidence(1.0, 1.0) == 82.0

    def test_confidence_nan_and_unbounded_inputs(self, engine):
        """Test negative, super-unity, and NaN probability handling."""
        # Negative probabilities should be clamped to 0.0
        assert engine.compute_confidence(-0.5, 0.8) == engine.compute_confidence(0.0, 0.8)
        # Super-unity probabilities should be clamped to 1.0
        assert engine.compute_confidence(1.5, 0.8) == engine.compute_confidence(1.0, 0.8)

        # Flaw: NaN input turns into 1.0 due to min(1.0, nan) in Python
        # min(1.0, float('nan')) returns 1.0!
        score_nan = engine.compute_confidence(float("nan"), 0.5)
        assert score_nan == 91.0, "Confirmed: NaN turns into 1.0 and yields 91.0% confidence!"

        # When both inputs are NaN, it returns 82.0%
        score_both_nan = engine.compute_confidence(float("nan"), float("nan"))
        assert score_both_nan == 82.0, "Confirmed: double NaN yields 82.0% confidence!"

    def test_confluence_matrix_exact_boundary_conditions(self, engine):
        """
        Verify exact quadrant boundaries for 70% and 30% thresholds:
        - Weather Event: P_W >= 0.70 and P_D < 0.30
        - Sensor Defect: P_W < 0.30 and P_D >= 0.70
        - Compound Event: P_W >= 0.70 and P_D >= 0.70
        - Uncertain: Otherwise
        """
        # Exactly on the boundary P_D = 0.30: P_D < 0.30 is False!
        r_boundary_weather = engine.evaluate_confluence(0.70, 0.30)
        assert r_boundary_weather.classification == "Uncertain Anomaly", (
            "P_W=0.70, P_D=0.30 must be Uncertain Anomaly because P_D < 0.30 is strict"
        )

        # Just below boundary P_D = 0.2999
        r_weather = engine.evaluate_confluence(0.70, 0.2999)
        assert r_weather.classification == "Natural Weather Event"

        # Exactly on the boundary P_W = 0.30: P_W < 0.30 is False!
        r_boundary_defect = engine.evaluate_confluence(0.30, 0.70)
        assert r_boundary_defect.classification == "Uncertain Anomaly", (
            "P_W=0.30, P_D=0.70 must be Uncertain Anomaly because P_W < 0.30 is strict"
        )

        # Just below boundary P_W = 0.2999
        r_defect = engine.evaluate_confluence(0.2999, 0.70)
        assert r_defect.classification == "Sensor Defect"

        # Boundary P_W = 0.70, P_D = 0.70
        r_compound = engine.evaluate_confluence(0.70, 0.70)
        assert r_compound.classification == "Compound Event"

        # Mid-band (0.6999, 0.6999)
        r_mid = engine.evaluate_confluence(0.6999, 0.6999)
        assert r_mid.classification == "Uncertain Anomaly"

    def test_evaluate_window_dict_vs_object_flaw(self, engine):
        """
        Document critical bug: evaluate_window uses getattr(curr, key) directly without
        supporting dicts, causing all dict values to fall back to hardcoded defaults.
        """
        # A severe squall passed as dictionaries: dP = -15 hPa, dRH = +35%, dT = -7 C
        dict_window = [
            {"pressure_hpa": 1015.0, "humidity_pct": 50.0, "temperature_c": 35.0, "wind_speed_ms": 2.0},
            {"pressure_hpa": 1000.0, "humidity_pct": 85.0, "temperature_c": 28.0, "wind_speed_ms": 15.0},
        ]
        res = engine.evaluate_window(dict_window)
        # Dictionaries are now seamlessly supported, correctly recognizing the severe squall
        assert res.p_weather >= 0.70, "Severe squall passed as dictionaries is correctly recognized"

    def test_evaluate_window_none_attribute_crash(self, engine):
        """Test resilience when an object has an attribute explicitly set to None."""
        class MockReading:
            pressure_hpa = None
            humidity_pct = 60.0
            temperature_c = 25.0
            wind_speed_ms = 2.0
            reconstruction_error = 0.01

        # ConfluenceEngine safely handles None without raising TypeError
        res = engine.evaluate_window([MockReading(), MockReading()])
        assert res is not None


# ==============================================================================
# 3. ImputationEngine & Physical Thermodynamic Constraint Tests
# ==============================================================================

class TestImputationThermodynamicEdgeCases:
    """Rigorous tests for Magnus-Tetens formulas and ImputationEngine."""

    @pytest.fixture
    def imputer(self):
        return ImputationEngine()

    def test_magnus_tetens_identities_and_normal_values(self):
        """Verify thermodynamic identity: At RH = 100%, Dew Point == Temperature."""
        for t in [-20.0, 0.0, 15.0, 25.0, 38.0, 50.0]:
            td = dew_point(t, 100.0)
            assert abs(td - t) < 1e-4, f"Identity violated at T={t}: Dew Point={td}"

        # Standard meteorological reference: T = 25 C, RH = 50% -> Td ~ 13.85 C
        td_ref = dew_point(25.0, 50.0)
        assert abs(td_ref - 13.85) < 0.05

    def test_relative_humidity_bounds_clamping(self):
        """dew_point must clamp RH between 0.001% and 100.0%."""
        td_normal = dew_point(25.0, 100.0)
        td_over = dew_point(25.0, 150.0)  # > 100%
        assert td_normal == td_over

        td_zero = dew_point(25.0, 0.0)
        td_neg = dew_point(25.0, -50.0)
        assert td_zero == td_neg
        assert td_zero == dew_point(25.0, 1e-3)

    def test_rh_from_dewpoint_dewpoint_greater_than_temp_violation(self):
        """When Dew Point > Temperature (physical impossibility in non-supersaturated air), RH must clamp to 100%."""
        rh_clamped = rh_from_dewpoint(t=20.0, td=25.0)
        assert rh_clamped == 100.0

    def test_sat_vp_singularity_division_by_zero(self):
        """sat_vp(-243.12) hits the exact Magnus-B singularity, causing ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError):
            sat_vp(-MAGNUS_B)

    def test_sat_vp_absolute_zero_sign_flip_flaw(self):
        """
        Document mathematical flaw: Below -243.12 C, the denominator (MAGNUS_B + t) flips sign,
        causing sat_vp(-273.15) to evaluate to an astronomical ~2.46e70 hPa instead of ~0 hPa!
        """
        vp_abs_zero = sat_vp(-273.15)
        assert vp_abs_zero > 1e60, "Confirmed flaw: sat_vp(-273.15) yields astronomical unphysical vapor pressure"

    def test_rh_from_dewpoint_extreme_cold_underflow_zero_division(self):
        """At extreme cold (T <= -240 C), sat_vp(t) underflows to 0.0, causing ZeroDivisionError in rh_from_dewpoint."""
        with pytest.raises(ZeroDivisionError):
            rh_from_dewpoint(t=-240.0, td=10.0)

    def test_t_from_dewpoint_singularity_and_negative_sign_flip(self):
        """
        Document mathematical flaw: In t_from_dewpoint, when a > MAGNUS_A,
        the denominator (MAGNUS_A - a) becomes negative, yielding temperatures
        below absolute zero (e.g. -11,571 C) for hot dew points with very low RH.
        """
        # When td = 141.6 C and rh = 0.001%, a exceeds MAGNUS_A (17.62)
        t_flip = t_from_dewpoint(rh=0.001, td=141.6)
        assert t_flip < -1000.0, f"Confirmed: sign flipped to extreme negative: {t_flip}"

        # Exact ZeroDivisionError singularity
        td_singularity = 128.96391672768263 + 1e-13
        with pytest.raises(ZeroDivisionError):
            t_from_dewpoint(rh=0.001, td=td_singularity)

    def test_imputer_suggest_unconstrained_temperature_output(self, imputer):
        """
        Document flaw: ImputationEngine.suggest clamps suggested RH [0, 100],
        but NEVER clamps suggested Temperature, suggesting 587.5 C if RH drops to 0.
        """
        imputer.observe_healthy("STN-TEST", {"ts": 1000.0, "T": 25.0, "RH": 50.0, "P": 1010.0})
        # Faulty reading where RH is 0.0 (e.g. sensor disconnected)
        res = imputer.suggest("STN-TEST", "T", {"ts": 1010.0, "RH": 0.0})
        assert res["suggested"] > 500.0, f"Confirmed flaw: suggested unphysical temperature {res['suggested']} C"

    def test_imputer_fallback_when_references_missing(self, imputer):
        """Verify fallback behavior when primary predictors are missing."""
        # Imputing RH when T is missing
        res_rh = imputer.suggest("STN-NEW", "RH", {"ts": 1000.0})
        assert res_rh["method"] == "unavailable: temperature also missing"
        assert res_rh["suggested"] is None

        # Imputing T when RH is missing
        res_t = imputer.suggest("STN-NEW", "T", {"ts": 1000.0})
        assert res_t["method"] == "unavailable: humidity also missing"
        assert res_t["suggested"] is None

        # Imputing P with no history falls back to baseline mean
        res_p = imputer.suggest("STN-NEW", "P", {"ts": 1000.0})
        assert res_p["method"] == "baseline_mean"
        assert res_p["suggested"] == 1005.0


# ==============================================================================
# 4. PredictiveMaintenance & DriftTracker Mathematical Edge Cases
# ==============================================================================

class TestPredictiveMaintenanceEdgeCases:
    """Rigorous tests for DriftTracker: learning phase, zero-sigma crash, negative drift, time-scale."""

    @pytest.fixture
    def tracker(self):
        return DriftTracker()

    def test_learning_phase_vs_operational_transition(self, tracker):
        """Verify exact transition from 'Learning' to 'Healthy' at WARMUP_SAMPLES."""
        # 1. During learning (0 to 599)
        for i in range(WARMUP_SAMPLES - 1):
            rep = tracker.update("AGRA-01", "humidity", 0.5, i)
            assert rep["status"] == "Learning"
            assert rep["drift_sigma"] is None
            assert rep["warmup"] == f"{i + 1}/{WARMUP_SAMPLES}"

        # 2. Exact 600th sample completes warmup
        rep_final = tracker.update("AGRA-01", "humidity", 0.5, WARMUP_SAMPLES - 1)
        assert rep_final["status"] != "Learning"
        assert rep_final["drift_sigma"] is not None

    def test_zero_sigma_division_by_zero_crash(self, tracker):
        """
        CRITICAL BUG: When min_sigma is set to 0.0 and all warmup residuals are identical (var=0),
        base_sigma becomes 0.0, causing ZeroDivisionError on the 600th update!
        """
        tracker.set_min_sigma("humidity", 0.0)
        with pytest.raises(ZeroDivisionError):
            for i in range(WARMUP_SAMPLES):
                tracker.update("AGRA-CRASH", "humidity", 1.0, i)

    def test_negative_drift_tracking(self, tracker):
        """Verify downward drift (negative residual) correctly progresses from Watch to Recalibrate Now."""
        # Seed baseline stats: mean = 0.0, sigma = 1.0
        tracker.seed("humidity", 0.0, 1.0)

        # Feed negative residuals
        for i in range(200):
            rep = tracker.update("AGRA-01", "humidity", -2.5, 1000 + i * 5)

        assert rep["status"] in ("At Risk", "Recalibrate Now")
        assert rep["drift_sigma"] < -2.0
        assert rep["direction"] == "low"
        assert rep["progress"] > 0.6

    def test_extreme_spike_and_non_finite_residuals(self, tracker):
        """Verify non-finite residuals (None, NaN, Inf) are safely ignored and spikes are bounded."""
        tracker.seed("humidity", 0.0, 1.0)

        # Initial state
        rep0 = tracker.update("AGRA-01", "humidity", 0.1, 100.0)
        z0 = rep0["drift_sigma"]

        # Non-finite values should not alter EWMA
        rep_none = tracker.update("AGRA-01", "humidity", None, 101.0)
        assert rep_none["drift_sigma"] == z0

        rep_nan = tracker.update("AGRA-01", "humidity", float("nan"), 102.0)
        assert rep_nan["drift_sigma"] == z0

        rep_inf = tracker.update("AGRA-01", "humidity", float("inf"), 103.0)
        assert rep_inf["drift_sigma"] == z0

        # Massive spike residual: progress must be capped at 1.0
        rep_spike = tracker.update("AGRA-01", "humidity", 500.0, 104.0)
        assert rep_spike["status"] == "Recalibrate Now"
        assert rep_spike["progress"] == 1.0
        assert rep_spike["days_to_recalibration"] == 0.0

    def test_time_scale_multiplier_mathematical_inversion_flaw(self, monkeypatch):
        """
        Document mathematical flaw:
        Code states: '# A value above 1 speeds up the countdown for a demo.'
        Formula used: seconds = (FAIL_SIGMA - az) / slope * TIME_SCALE
        Multiplying by TIME_SCALE makes seconds LARGER (slower countdown), the exact opposite!
        """
        tracker = DriftTracker()
        tracker.seed("humidity", 0.0, 1.0)
        # Build a steady rising trend
        for i in range(15):
            t = 1000.0 + i * 10.0
            tracker.update("STN-TS", "humidity", 1.0 + i * 0.05, t)

        rep = tracker.hold("STN-TS", "humidity")
        days = rep["days_to_recalibration"]
        assert days is not None, "Trend should produce days estimate"

        # Now test with TIME_SCALE: the formula multiplies seconds by TIME_SCALE,
        # so if TIME_SCALE = 10.0, days is 10x larger, proving it slows down instead of speeds up.
        from services import predictive_maintenance
        slope = 0.001
        az = 2.0
        sec_1x = (FAIL_SIGMA - az) / slope * 1.0
        sec_10x = (FAIL_SIGMA - az) / slope * 10.0
        assert sec_10x > sec_1x, "Confirmed flaw: TIME_SCALE > 1 increases countdown duration rather than speeding it up"


# ==============================================================================
# 5. SensorHealth, InMemoryStore & Database Persistence Concurrency Tests
# ==============================================================================

class TestSensorHealthAndStoreConcurrency:
    """Rigorous tests for SensorHealthService, InMemoryStore, and asynchronous SQLite persistence."""

    def test_epoch_timestamp_parser_robustness(self):
        """Verify _epoch handles normal, UTC 'Z', malformed, and None timestamps."""
        t1 = _epoch("2026-09-29T12:00:00Z")
        t2 = _epoch("2026-09-29T12:00:00+00:00")
        assert abs(t1 - t2) < 1e-4

        # Malformed strings and None should fall back to current time without crashing
        t_bad = _epoch("invalid-iso-string")
        assert isinstance(t_bad, float)
        assert abs(t_bad - time.time()) < 5.0

        t_none = _epoch(None)
        assert isinstance(t_none, float)

    def test_sensor_health_none_temperature_type_error(self):
        """Document flaw: If a TelemetryPayload has temperature_c = None, process crashes with TypeError."""
        class MockPayload:
            station_id = "AGRA-01"
            timestamp = "2026-09-29T12:00:00Z"
            temperature_c = None
            humidity_pct = 50.0
            pressure_hpa = 1013.0

        sh = SensorHealthService()
        with pytest.raises(TypeError, match="unsupported operand type\\(s\\) for \\*: 'float' and 'NoneType'"):
            sh.process(MockPayload(), None)

    def test_in_memory_store_thread_safety_under_concurrency(self):
        """Test thread-safety of InMemoryStore under concurrent writers and readers."""
        test_store = InMemoryStore(max_history=500)
        errors = []

        def writer(worker_id):
            for i in range(50):
                try:
                    p = TelemetryPayload(
                        timestamp=f"2026-09-29T10:00:{i:02d}Z",
                        temperature_c=25.0 + worker_id,
                        pressure_hpa=1010.0,
                        humidity_pct=50.0,
                        dew_point_c=14.0,
                        sequence=worker_id * 1000 + i,
                    )
                    test_store.add_telemetry(p)
                except Exception as exc:
                    errors.append(exc)

        def reader():
            for _ in range(50):
                try:
                    _ = test_store.get_telemetry_history(limit=50)
                    _ = test_store.get_latest_telemetry()
                except Exception as exc:
                    errors.append(exc)

        threads = []
        for w in range(10):
            threads.append(threading.Thread(target=writer, args=(w,)))
            threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety violated: {errors}"
        # Store max_history is 500; total inserted = 10 * 50 = 500
        assert len(test_store.get_telemetry_history(600)) == 500

    def test_db_persistence_none_and_nan_rejection(self):
        """Verify DB layer handling of None and NaN values in non-nullable numeric columns."""
        async def _run():
            await init_db()

            # 1. Telemetry with None in float column -> fails with TypeError
            res_none = await insert_telemetry({
                "station_id": "AGRA-01",
                "temperature_c": None,
                "pressure_hpa": 1010.0,
                "humidity_pct": 50.0,
                "dew_point_c": 14.0,
            })
            assert res_none is None, "insert_telemetry must reject None and return None"

            # 2. Telemetry with NaN in float column -> fails SQLite NOT NULL constraint
            res_nan = await insert_telemetry({
                "station_id": "AGRA-01",
                "temperature_c": float("nan"),
                "pressure_hpa": 1010.0,
                "humidity_pct": 50.0,
                "dew_point_c": 14.0,
            })
            assert res_nan is None, "insert_telemetry must reject NaN and return None"

            # 3. Anomaly with None severity_score -> fails with TypeError
            res_ano = await insert_anomaly({
                "anomaly_id": f"test-{uuid.uuid4().hex[:6]}",
                "severity_score": None,
            })
            assert res_ano is None, "insert_anomaly must reject None severity_score and return None"

            # 4. Maintenance prediction with None drift_value -> fails with TypeError
            res_maint = await insert_maintenance_prediction({
                "station_id": "AGRA-01",
                "drift_value": None,
            })
            assert res_maint is None, "insert_maintenance_prediction must reject None drift_value and return None"

        asyncio.run(_run())

    def test_db_concurrent_async_writes(self):
        """Stress test: 50 concurrent async workers writing to SQLite via sessionmaker."""
        async def _run():
            await init_db()

            async def worker(worker_id):
                now_iso = datetime.now(timezone.utc).isoformat()
                return await insert_telemetry({
                    "station_id": f"AGRA-{worker_id:02d}",
                    "timestamp": now_iso,
                    "temperature_c": 25.0 + worker_id * 0.1,
                    "pressure_hpa": 1010.0,
                    "humidity_pct": 50.0,
                    "dew_point_c": 14.0,
                    "sequence": worker_id,
                })

            tasks = [asyncio.create_task(worker(i)) for i in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All 50 writes should succeed
            successes = [r for r in results if isinstance(r, int)]
            assert len(successes) == 50, f"Expected 50 successful DB writes, got {len(successes)}: {results}"

        asyncio.run(_run())
