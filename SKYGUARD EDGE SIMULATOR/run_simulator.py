#!/usr/bin/env python3
"""=============================================================================
SKYGUARD AWS EDGE SENSOR SIMULATOR - RUNNER
=============================================================================
Simulates an AWS IoT Greengrass / Core edge meteorological station.
Supports:
1. Streaming directly from a verified, judge-inspected CSV dataset (--csv)
2. Live real-time generative physical stochastic simulation
3. Interactive hotkeys for real-time fault injection (storms, stuck sensor, drift, noise)
4. Resilient HTTP REST POST dispatch to teammate's anomaly detection backend
============================================================================="""

import argparse
import os
import sys
import time

# Ensure Windows terminal supports UTF-8 characters without cp1252 crash
if sys.platform.startswith("win"):
    import io
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rich.console import Console
from rich.live import Live

# Ensure root directory is in import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import random
from collections import deque

from src.config import load_config
from src.models.indian_climates import get_climate_profile
from src.models.weather_physics import WeatherPhysicsEngine
from src.models.fault_injector import FaultInjector, AnomalyType
from src.transmitter import EdgeTransmitter
from src.csv_player import CSVPlayer
from src.tui import EdgeSimulatorTUI

class AutoChaosManager:
    """
    Orchestrates stochastic state transitions between:
    1. Clean nominal atmospheric baseline
    2. Physical multivariate weather anomalies (storm, heatwave, cold snap)
    3. Hardware sensor defects (stuck sensor, calibration drift, noise spike, null reading)

    Ensures states dwell for a configurable period (default ~35s) so that the
    anomaly detection pipeline, charts, and 3D twin show the transitions distinctly.
    """
    def __init__(self, fault_injector: FaultInjector, duration_sec: float = 35.0, enabled: bool = False):
        self.fault_injector = fault_injector
        self.duration_sec = duration_sec
        self.enabled = enabled
        self.current_state_name = "Nominal Baseline"
        self.time_in_state = 0.0
        self.state_countdown = duration_sec
        self.is_nominal_phase = True
        self.last_fault_applied: Optional[str] = None

        # Pool of diverse supported faults & anomalies
        self.fault_pool = [
            ("WEATHER_ANOMALY", AnomalyType.WEATHER_SEVERE_STORM, "Severe Squall Downdraft"),
            ("WEATHER_ANOMALY", AnomalyType.WEATHER_HEATWAVE, "Extreme Convective Heatwave"),
            ("WEATHER_ANOMALY", AnomalyType.WEATHER_COLD_SNAP, "Cold Snap Front"),
            ("SENSOR_DEFECT", AnomalyType.DEFECT_STUCK_SENSOR, "RTD Sensor Stuck / Flatline"),
            ("SENSOR_DEFECT", AnomalyType.DEFECT_CALIBRATION_DRIFT, "Capacitive Hygrometer Drift"),
            ("SENSOR_DEFECT", AnomalyType.DEFECT_ERRATIC_NOISE, "Electrical EMI Noise Spikes"),
            ("SENSOR_DEFECT", AnomalyType.DEFECT_OUTLIER_SPIKE, "Transducer Impulse Spike"),
            ("SENSOR_DEFECT", AnomalyType.DEFECT_PACKET_DROP_NULL, "I2C Bus Null Packet Drop"),
        ]
        self.recent_fault_indices = deque(maxlen=4)

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        if not self.enabled:
            self.fault_injector.clear_all()
            self.current_state_name = "Nominal Baseline (Manual)"
            self.is_nominal_phase = True
        else:
            self.time_in_state = 0.0
            self.state_countdown = self.duration_sec
            self.is_nominal_phase = True
            self.current_state_name = "Nominal Baseline"
        return self.enabled

    def tick(self, dt: float):
        if not self.enabled:
            return

        self.time_in_state += dt
        self.state_countdown = max(0.0, self.duration_sec - self.time_in_state)

        if self.time_in_state >= self.duration_sec:
            self.time_in_state = 0.0
            self.state_countdown = self.duration_sec

            if self.is_nominal_phase:
                # Transition from Nominal -> Random Anomaly / Defect
                available_indices = [i for i in range(len(self.fault_pool)) if i not in self.recent_fault_indices]
                if not available_indices:
                    available_indices = list(range(len(self.fault_pool)))
                chosen_idx = random.choice(available_indices)
                self.recent_fault_indices.append(chosen_idx)

                category, anomaly_type, label = self.fault_pool[chosen_idx]
                self.fault_injector.clear_all()
                if category == "WEATHER_ANOMALY":
                    self.fault_injector.set_weather_anomaly(anomaly_type)
                else:
                    self.fault_injector.toggle_defect(anomaly_type)

                self.current_state_name = label
                self.last_fault_applied = label
                self.is_nominal_phase = False
            else:
                # Transition from Anomaly/Defect back to Nominal Baseline
                self.fault_injector.clear_all()
                self.current_state_name = "Nominal Baseline"
                self.is_nominal_phase = True

def run_simulator(
    csv_path: str = None,
    endpoint_url: str = None,
    region_key: str = None,
    device_id: str = None,
    interval_sec: float = None,
    loop: bool = True,
    auto_chaos: bool = False,
    chaos_duration: float = 35.0,
):
    config = load_config()

    if endpoint_url:
        config["endpoint_url"] = endpoint_url
    if device_id:
        config["device_id"] = device_id
    if interval_sec is not None:
        config["transmission_interval_sec"] = interval_sec
    if region_key:
        config["default_region"] = region_key

    active_region = config.get("default_region", "mumbai_monsoon")
    profile = get_climate_profile(active_region)
    interval = config.get("transmission_interval_sec", 1.0)

    # Initialize components
    fault_injector = FaultInjector()
    transmitter = EdgeTransmitter(config)

    # Check source mode: CSV dataset vs Live Physics Engine
    csv_player = None
    physics_engine = None

    if csv_path:
        if not os.path.exists(csv_path):
            print(f"[Error] Specified CSV file not found: {csv_path}")
            sys.exit(1)
        csv_player = CSVPlayer(csv_path, loop=loop)
        source_desc = f"CSV File: {os.path.basename(csv_path)} ({csv_player.total_rows} rows)"
    else:
        physics_engine = WeatherPhysicsEngine(profile)
        source_desc = f"Live Physics Engine ({profile.display_name})"

    chaos_mgr = AutoChaosManager(fault_injector, duration_sec=chaos_duration, enabled=auto_chaos)

    tui = EdgeSimulatorTUI(
        device_id=config.get("device_id", "aws-edge-in-station-04"),
        region_display=profile.display_name,
        endpoint_url=config.get("endpoint_url"),
        source_desc=source_desc,
        fault_injector=fault_injector,
        initial_interval_sec=interval,
        auto_chaos=chaos_mgr,
    )

    console = Console(force_terminal=True)
    console.print(f"[bold cyan]Launching SkyGuard AWS Edge Simulator...[/]")
    time.sleep(0.5)

    try:
        # Reduced refresh_per_second from 12 to 2 to eliminate screen flicker on Windows
        with Live(tui.render(), console=console, refresh_per_second=2, screen=True) as live:
            start_hour = 8.0
            tick_counter = 0

            while not tui.should_exit:
                tui.check_hotkeys()
                if tui.should_exit:
                    break

                if tui.is_paused:
                    live.update(tui.render())
                    time.sleep(0.1)
                    continue

                # Advance auto-chaos state machine if enabled
                chaos_mgr.tick(interval)

                # 1. Fetch next baseline telemetry
                source_meta = None
                if csv_player:
                    reading = csv_player.get_next()
                    if reading is None:
                        # End of file in non-loop mode
                        break
                    source_meta = csv_player.get_source_metadata()
                    source_desc = f"CSV File: {os.path.basename(csv_path)} (Row {csv_player.current_index}/{csv_player.total_rows})"
                    tui.source_desc = source_desc
                else:
                    current_hour = (start_hour + tick_counter * (interval / 60.0)) % 24.0
                    reading = physics_engine.step(hour_of_day=current_hour, dt_seconds=interval)

                baseline_dict = reading.to_dict()

                # 2. Process through fault injector (weather anomaly or sensor defect overlay)
                processed_dict = fault_injector.process(reading)

                # 3. Format into AWS IoT Greengrass payload
                payload = transmitter.build_aws_payload(
                    reading_data=processed_dict,
                    region_key=active_region,
                    source_metadata=source_meta,
                )

                # 4. Transmit via HTTP POST to teammate's backend
                result = transmitter.transmit(payload)

                # 5. Update TUI state and logs
                tui.log_transmission(result)
                tui.update_telemetry(baseline_dict, processed_dict, source_meta)
                live.update(tui.render())

                tick_counter += 1

                # Sub-second responsive sleep while listening to hotkeys
                remaining_time = tui.interval_sec
                while remaining_time > 0 and not tui.should_exit:
                    step_sleep = min(0.08, remaining_time)
                    time.sleep(step_sleep)
                    remaining_time -= step_sleep
                    tui.check_hotkeys()

    except KeyboardInterrupt:
        pass

    console.print("[bold yellow]\nSkyGuard Edge Simulator stopped cleanly.[/]")

def main():
    parser = argparse.ArgumentParser(description="SkyGuard AWS Edge Device Simulator")
    parser.add_argument("--csv", type=str, default=None, help="Path to verified CSV dataset to stream")
    parser.add_argument("--url", type=str, default=None, help="Target ingestion HTTP endpoint URL")
    parser.add_argument("--interval", type=float, default=None, help="Transmission interval in seconds")
    parser.add_argument("--region", type=str, default=None, help="Indian climate region key")
    parser.add_argument("--device-id", type=str, default=None, help="AWS IoT device ID")
    parser.add_argument("--no-loop", action="store_true", help="Do not loop CSV file upon reaching EOF")
    parser.add_argument("-c", "--auto-chaos", action="store_true", help="Enable automatic random cycling through nominal and fault states")
    parser.add_argument("--chaos-duration", type=float, default=35.0, help="Dwell time in seconds per chaos state (default: 35.0s)")

    args = parser.parse_args()
    run_simulator(
        csv_path=args.csv,
        endpoint_url=args.url,
        region_key=args.region,
        device_id=args.device_id,
        interval_sec=args.interval,
        loop=not args.no_loop,
        auto_chaos=args.auto_chaos,
        chaos_duration=args.chaos_duration,
    )

if __name__ == "__main__":
    main()
