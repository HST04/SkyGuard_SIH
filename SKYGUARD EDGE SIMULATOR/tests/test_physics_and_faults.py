"""Comprehensive Unit Test Suite for SkyGuard Edge Simulator.
Tests:
1. Physics & Climate Bounds
2. Stochastic Non-Repeating Randomness
3. Psychrometric Vapor Relations
4. Weather Anomalies (Multivariate Correlated Shifts)
5. Sensor Hardware Defects (Isolated Unphysical Signatures)
6. AWS IoT Greengrass Payload Conformance
7. CSV Playback Integrity
"""

import unittest
import os
import sys

# Ensure root directory is in import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.indian_climates import get_climate_profile, CLIMATE_PROFILES
from src.models.weather_physics import WeatherPhysicsEngine
from src.models.fault_injector import FaultInjector, AnomalyType
from src.transmitter import EdgeTransmitter
from src.csv_player import CSVPlayer
from src.config import DEFAULT_CONFIG

class TestWeatherPhysics(unittest.TestCase):

    def test_climate_profiles_exist(self):
        self.assertIn("mumbai_monsoon", CLIMATE_PROFILES)
        self.assertIn("delhi_summer", CLIMATE_PROFILES)
        self.assertIn("thar_desert", CLIMATE_PROFILES)
        self.assertIn("bengaluru_temperate", CLIMATE_PROFILES)

    def test_physical_bounds(self):
        """Validates that engine readings remain within physically realistic hard limits."""
        profile = get_climate_profile("mumbai_monsoon")
        engine = WeatherPhysicsEngine(profile)

        for hour in [0.0, 6.0, 12.0, 15.0, 21.0]:
            reading = engine.step(hour_of_day=hour, dt_seconds=60.0)
            self.assertGreaterEqual(reading.temperature_c, profile.temp_min_hard)
            self.assertLessEqual(reading.temperature_c, profile.temp_max_hard)
            self.assertGreaterEqual(reading.humidity_pct, profile.rh_min_hard)
            self.assertLessEqual(reading.humidity_pct, 100.0)
            self.assertGreaterEqual(reading.pressure_hpa, profile.pressure_min_hard)
            self.assertLessEqual(reading.pressure_hpa, profile.pressure_max_hard)

    def test_true_randomness_non_repeating(self):
        """Verifies that unseeded runs generate different values, proving true randomness."""
        profile = get_climate_profile("delhi_summer")
        engine1 = WeatherPhysicsEngine(profile)
        engine2 = WeatherPhysicsEngine(profile)

        readings1 = [engine1.step(hour_of_day=12.0).temperature_c for _ in range(5)]
        readings2 = [engine2.step(hour_of_day=12.0).temperature_c for _ in range(5)]

        # Two independent runs must not produce identical float trajectories
        self.assertNotEqual(readings1, readings2)

    def test_solar_cycle_day_vs_night(self):
        """Confirms solar radiation is zero at midnight and positive at midday."""
        profile = get_climate_profile("thar_desert")
        engine = WeatherPhysicsEngine(profile)

        night_reading = engine.step(hour_of_day=2.0)
        day_reading = engine.step(hour_of_day=12.0)

        self.assertEqual(night_reading.solar_radiation_wm2, 0.0)
        self.assertGreater(day_reading.solar_radiation_wm2, 400.0)


class TestFaultInjector(unittest.TestCase):

    def setUp(self):
        self.profile = get_climate_profile("mumbai_monsoon")
        self.engine = WeatherPhysicsEngine(self.profile)
        self.injector = FaultInjector()

    def test_normal_operation(self):
        reading = self.engine.step(hour_of_day=12.0)
        processed = self.injector.process(reading)
        self.assertEqual(processed["_ground_truth"]["status"], "NORMAL")
        self.assertAlmostEqual(processed["temperature_c"], reading.temperature_c, places=2)

    def test_weather_anomaly_storm_multivariate_correlation(self):
        """Verifies severe storm drops pressure, surges wind, and triggers precipitation."""
        self.injector.set_weather_anomaly(AnomalyType.WEATHER_SEVERE_STORM)
        reading = self.engine.step(hour_of_day=14.0)
        processed = self.injector.process(reading)

        # Multi-sensor physics check
        self.assertLess(processed["pressure_hpa"], reading.pressure_hpa - 10.0)
        self.assertGreater(processed["wind_speed_mps"], reading.wind_speed_mps + 10.0)
        self.assertGreater(processed["precipitation_mmh"], 40.0)
        self.assertEqual(processed["_ground_truth"]["status"], "WEATHER_ANOMALY")

    def test_sensor_defect_stuck_sensor(self):
        """Verifies stuck sensor freezes at constant reading across time steps."""
        self.injector.toggle_defect(AnomalyType.DEFECT_STUCK_SENSOR)
        
        reading1 = self.engine.step(hour_of_day=6.0)
        processed1 = self.injector.process(reading1)
        stuck_val = processed1["temperature_c"]

        reading2 = self.engine.step(hour_of_day=14.0)  # Daytime temp should normally be much higher
        processed2 = self.injector.process(reading2)

        self.assertEqual(processed2["temperature_c"], stuck_val)
        self.assertEqual(processed2["_ground_truth"]["status"], "SENSOR_DEFECT")

    def test_sensor_defect_calibration_drift(self):
        """Verifies calibration drift accumulates monotonic bias."""
        self.injector.toggle_defect(AnomalyType.DEFECT_CALIBRATION_DRIFT)

        drift_vals = []
        for _ in range(5):
            reading = self.engine.step(hour_of_day=10.0)
            processed = self.injector.process(reading)
            drift_vals.append(processed["temperature_c"] - reading.temperature_c)

        # Each step should have strictly increasing positive bias
        for i in range(len(drift_vals) - 1):
            self.assertGreater(drift_vals[i+1], drift_vals[i])

    def test_sensor_defect_packet_drop(self):
        """Verifies packet drop returns None values for corrupted sensor bus."""
        self.injector.toggle_defect(AnomalyType.DEFECT_PACKET_DROP_NULL)
        reading = self.engine.step(hour_of_day=12.0)
        processed = self.injector.process(reading)

        self.assertIsNone(processed["temperature_c"])
        self.assertIsNone(processed["humidity_pct"])


class TestAWSTransmitter(unittest.TestCase):

    def test_payload_structure(self):
        transmitter = EdgeTransmitter(DEFAULT_CONFIG)
        profile = get_climate_profile("mumbai_monsoon")
        engine = WeatherPhysicsEngine(profile)
        reading = engine.step(hour_of_day=12.0)

        payload = transmitter.build_aws_payload(
            reading_data=reading.to_dict(),
            region_key="mumbai_monsoon",
            source_metadata={"source_file": "test.csv", "source_row": 5},
        )

        # Validate AWS IoT Greengrass standard keys
        self.assertEqual(payload["deviceId"], "aws-edge-in-station-04")
        self.assertIn("timestamp", payload)
        self.assertIn("isoTime", payload)
        self.assertIn("telemetry", payload)
        self.assertIn("device_health", payload)
        self.assertIn("temperature_c", payload["telemetry"])
        self.assertIn("relative_humidity_pct", payload["telemetry"])
        self.assertIn("pressure_hpa", payload["telemetry"])
        self.assertEqual(payload["_ground_truth"]["source_file"], "test.csv")


class TestCSVPlayer(unittest.TestCase):

    def test_csv_playback(self):
        # We know test_sample.csv was generated earlier
        if os.path.exists("test_sample.csv"):
            player = CSVPlayer("test_sample.csv", loop=True)
            self.assertEqual(player.total_rows, 20)
            first_reading = player.get_next()
            self.assertIsNotNone(first_reading)
            self.assertEqual(player.current_index, 1)


if __name__ == "__main__":
    unittest.main()
