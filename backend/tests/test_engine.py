import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timezone
from models.schemas import TelemetryPayload
from services.rule_engine import IMDPhysicsRuleEngine, calculate_dew_point
from services.anomaly_detector import anomaly_detector

def test_dew_point_calculation():
    # At T=30°C and RH=50%, dew point should be around ~18.4°C
    td = calculate_dew_point(30.0, 50.0)
    assert 17.0 <= td <= 20.0

def test_imd_rules_normal():
    payload = TelemetryPayload(
        timestamp=datetime.now(timezone.utc).isoformat(),
        temperature_c=32.0,
        pressure_hpa=1005.0,
        humidity_pct=60.0,
        dew_point_c=calculate_dew_point(32.0, 60.0),
        sequence=1
    )
    res = IMDPhysicsRuleEngine.evaluate(payload, [])
    assert res is None

def test_imd_rules_hard_rh_bound():
    payload = TelemetryPayload(
        timestamp=datetime.now(timezone.utc).isoformat(),
        temperature_c=32.0,
        pressure_hpa=1005.0,
        humidity_pct=115.0, # Physical impossibility
        dew_point_c=25.0,
        sequence=2
    )
    res = IMDPhysicsRuleEngine.evaluate(payload, [])
    assert res is not None
    assert "humidity" in res["culprit"]

def test_imd_rules_temp_step_rate():
    prev = TelemetryPayload(
        timestamp=datetime.now(timezone.utc).isoformat(),
        temperature_c=30.0,
        pressure_hpa=1005.0,
        humidity_pct=60.0,
        dew_point_c=20.0,
        sequence=1
    )
    curr = TelemetryPayload(
        timestamp=datetime.now(timezone.utc).isoformat(),
        temperature_c=37.5, # Sudden +7.5°C jump in 1 second
        pressure_hpa=1005.0,
        humidity_pct=60.0,
        dew_point_c=20.0,
        sequence=2
    )
    res = IMDPhysicsRuleEngine.evaluate(curr, [prev])
    assert res is not None
    assert "temperature" in res["culprit"]

def test_anomaly_detector_drift():
    # Normal window
    window = [
        TelemetryPayload(
            timestamp=datetime.now(timezone.utc).isoformat(),
            temperature_c=33.0,
            pressure_hpa=1005.0,
            humidity_pct=55.0,
            dew_point_c=22.0,
            sequence=i
        ) for i in range(12)
    ]
    # Injected subtle capacitive decoupling: RH surges to 88% while T stays 38°C
    window[-1].temperature_c = 38.0
    window[-1].humidity_pct = 88.0
    
    event = anomaly_detector.evaluate_window(window)
    assert event is not None
    assert event.anomaly_type == "ai_anomaly"
    assert "humidity" in event.culprit_sensors
    assert len(event.shap_values) > 0

if __name__ == "__main__":
    test_dew_point_calculation()
    test_imd_rules_normal()
    test_imd_rules_hard_rh_bound()
    test_imd_rules_temp_step_rate()
    test_anomaly_detector_drift()
    print("All backend tests passed successfully!")
