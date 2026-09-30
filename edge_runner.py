#!/usr/bin/env python3
"""
SkyGuard AI — Standalone Edge Station Telemetry Streamer & Physics Validator
=============================================================================
Simulates an Automatic Weather Station (AWS) edge node streaming 1 Hz telemetry
into the SkyGuard AI backend (http://localhost:8000/api/v1/telemetry/ingest).

Usage:
    python edge_runner.py                  # Interactive live streaming (press keys to change mode)
    python edge_runner.py --random         # Autonomous stochastic meteorological & fault simulation
    python edge_runner.py --scenario squall # Direct severe thunderstorm squall test (Zero False Alarm)
    python edge_runner.py --scenario drift  # Direct capacitive sensor drift test (Hardware Defect)
    python edge_runner.py --scenario nominal# Continuous clean diurnal baseline

Keyboard Shortcuts (during live stream):
    [N] : Normal Diurnal Baseline
    [S] : Severe Thunderstorm Squall (True-Negative: Zero False Alarm)
    [D] : Capacitive Sensor Drift (Hardware Anomaly)
    [F] : Stuck / Frozen Sensor (Flatline)
    [H] : Thermal Impulse Spike (+8°C)
    [R] : Toggle Autonomous Random Transitions
    [Q] : Quit
"""

import argparse
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

# Try importing msvcrt for non-blocking Windows keyboard input
WINDOWS_KEYBOARD = False
try:
    import msvcrt
    WINDOWS_KEYBOARD = True
except ImportError:
    pass

# ANSI Terminal Colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"

def calc_dew_point(t_c: float, rh: float) -> float:
    """Magnus-Tetens thermodynamic dew point formula."""
    rh = max(0.01, min(100.0, rh))
    a = 17.27
    b = 237.7
    alpha = ((a * t_c) / (b + t_c)) + math.log(rh / 100.0)
    td = (b * alpha) / (a - alpha)
    return round(td, 2)

class EdgeStationRunner:
    def __init__(self, endpoint: str, station_id: str = "AGRA-01", mode: str = "nominal", random_transitions: bool = False):
        self.endpoint = endpoint
        self.station_id = station_id
        self.mode = mode.lower()
        self.random_transitions = random_transitions
        self.seq = 1000
        self.tick = 0

        # Meteorological base state (Agra AWS Regional Profile)
        self.base_temp = 30.0
        self.base_rh = 62.5
        self.base_p = 1005.0
        self.base_ws = 3.2
        self.base_solar = 270.0

        # Mode timer for auto-transitions in random mode
        self.mode_ticks_remaining = 30

        # Smooth transition offsets for clean physical continuity
        self.current_temp_offset = 0.0
        self.current_rh_offset = 0.0
        self.current_p_offset = 0.0
        self.current_ws_offset = 0.0

    def print_banner(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*78}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.WHITE} SkyGuard AI — Edge Station Telemetry Streamer & Physics Harness{Colors.RESET}")
        print(f"{Colors.DIM} Target: {self.endpoint}  |  Station: {self.station_id}{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*78}{Colors.RESET}")
        print(f"{Colors.YELLOW} Hotkeys:{Colors.RESET} [0/N] Nominal | [1/H] Heat Spike | [2/D] Sensor Drift | [3/S] Storm Squall | [4/F] Frozen | [R] Random | [Q] Quit\n")

    def read_keyboard(self):
        """Reads non-blocking keypress if available on Windows."""
        if not WINDOWS_KEYBOARD:
            return
        while msvcrt.kbhit():
            ch = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            if ch == 'q':
                print(f"\n{Colors.YELLOW}[EdgeRunner] Streaming stopped by user.{Colors.RESET}")
                sys.exit(0)
            elif ch in ('0', 'n'):
                self.mode = "nominal"
                self.random_transitions = False
                print(f"\n{Colors.GREEN}>>> SWITCHED MODE: [Nominal Diurnal Baseline]{Colors.RESET}")
            elif ch in ('3', 's'):
                self.mode = "squall"
                self.random_transitions = False
                print(f"\n{Colors.BLUE}>>> INJECTING SCENARIO: [Severe Thunderstorm Squall - Zero False Alarm]{Colors.RESET}")
            elif ch in ('2', 'd'):
                self.mode = "drift"
                self.random_transitions = False
                print(f"\n{Colors.RED}>>> INJECTING SCENARIO: [Capacitive Humidity Drift - Hardware Defect]{Colors.RESET}")
            elif ch in ('4', 'f'):
                self.mode = "freeze"
                self.random_transitions = False
                print(f"\n{Colors.MAGENTA}>>> INJECTING SCENARIO: [Stuck / Frozen Sensor Flatline]{Colors.RESET}")
            elif ch in ('1', 'h'):
                self.mode = "spike"
                self.random_transitions = False
                print(f"\n{Colors.YELLOW}>>> INJECTING SCENARIO: [Thermal Impulse Spike (+8°C)]{Colors.RESET}")
            elif ch == 'r':
                self.random_transitions = not self.random_transitions
                status = "ENABLED" if self.random_transitions else "DISABLED"
                print(f"\n{Colors.CYAN}>>> AUTONOMOUS RANDOM CHAOS: {status}{Colors.RESET}")

    def generate_packet(self) -> dict:
        self.tick += 1
        self.seq += 1

        # Check random mode transition
        if self.random_transitions:
            self.mode_ticks_remaining -= 1
            if self.mode_ticks_remaining <= 0:
                choices = ["nominal", "nominal", "nominal", "squall", "drift", "freeze"]
                self.mode = random.choice(choices)
                self.mode_ticks_remaining = random.randint(15, 35)
                color = Colors.GREEN if self.mode == "nominal" else (Colors.BLUE if self.mode == "squall" else Colors.RED)
                print(f"\n{color}>>> [Autonomous Transition] New Mode: {self.mode.upper()} for {self.mode_ticks_remaining}s{Colors.RESET}")

        # Target offsets for active mode
        tgt_t, tgt_p, tgt_rh, tgt_ws = 0.0, 0.0, 0.0, 0.0
        if self.mode == "squall":
            tgt_t = -7.8
            tgt_p = -10.5
            tgt_rh = 32.0
            tgt_ws = 8.5
        elif self.mode == "drift":
            tgt_rh = 16.5
        elif self.mode == "spike":
            tgt_t = 7.5
            tgt_rh = -4.0

        # Slew offsets smoothly to avoid artificial single-tick discontinuity
        self.current_temp_offset += (tgt_t - self.current_temp_offset) * 0.5
        self.current_p_offset += (tgt_p - self.current_p_offset) * 0.5
        self.current_rh_offset += (tgt_rh - self.current_rh_offset) * 0.5
        self.current_ws_offset += (tgt_ws - self.current_ws_offset) * 0.5

        # Diurnal solar curve (600s synthetic day cycle)
        diurnal = math.sin((2 * math.pi * (self.tick % 600)) / 600)
        temp = self.base_temp + (diurnal * 4.2) + self.current_temp_offset + random.uniform(-0.02, 0.02)
        rh = min(96.0, max(15.0, self.base_rh - (diurnal * 12.0) + self.current_rh_offset + random.uniform(-0.04, 0.04)))
        p = self.base_p + (math.cos((4 * math.pi * (self.tick % 600)) / 600) * 1.5) + self.current_p_offset + random.uniform(-0.01, 0.01)
        ws = max(0.5, self.base_ws + self.current_ws_offset + random.uniform(-0.04, 0.04))
        solar = max(0.0, self.base_solar + (diurnal * 250.0) + random.uniform(-2.0, 2.0))
        if self.mode == "squall":
            solar = max(0.0, solar * 0.15)
        elif self.mode == "spike":
            solar = min(1000.0, solar + 150.0)

        if self.mode == "freeze":
            rh = 55.00

        wind_dir = (180.0 + (math.sin(self.tick / 15.0) * 45.0)) % 360.0
        td = calc_dew_point(temp, rh)
        now_iso = datetime.now(timezone.utc).isoformat()

        # Local IMD physics boundary check on edge hardware
        imd_passed = bool(
            -10.0 <= temp <= 60.0
            and 0.0 <= rh <= 100.0
            and 850.0 <= p <= 1080.0
            and td <= temp + 1.0
        )

        return {
            "station_id": self.station_id,
            "timestamp": now_iso,
            "temperature_c": round(temp, 2),
            "humidity_pct": round(rh, 2),
            "pressure_hpa": round(p, 2),
            "dew_point_c": td,
            "wind_speed_ms": round(ws, 2),
            "wind_dir_deg": round(wind_dir, 1),
            "solar_radiation_wm2": round(solar, 1),
            "sequence": self.seq,
            "source": "edge-runner-cli",
            "drop_flag": 0,
            "imd_passed": imd_passed,
        }

    def send_packet(self, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def run(self):
        self.print_banner()
        print(f"{Colors.DIM}Connecting to SkyGuard AI ingestion pipeline...{Colors.RESET}\n")

        consecutive_errors = 0
        while True:
            self.read_keyboard()
            pkt = self.generate_packet()

            try:
                t0 = time.perf_counter()
                resp = self.send_packet(pkt)
                latency = (time.perf_counter() - t0) * 1000
                consecutive_errors = 0

                # Extract response metadata
                reconstruction_error = resp.get("reconstruction_error", 0.015)
                conf = resp.get("confluence", {})
                classification = conf.get("classification", "Nominal Baseline")
                conf_score = conf.get("confidence_score", 98.0)
                defect_type = conf.get("defect_type", "none")

                # Format terminal display
                time_str = datetime.now().strftime("%H:%M:%S")
                seq_str = f"#{pkt['sequence']}"
                readings = f"T={pkt['temperature_c']:4.1f}°C  RH={pkt['humidity_pct']:4.1f}%  P={pkt['pressure_hpa']:6.1f}hPa  Td={pkt['dew_point_c']:4.1f}°C"

                # Color-code classification
                imd_badge = f"{Colors.GREEN}[IMD: PASS]{Colors.RESET}" if pkt.get("imd_passed", True) else f"{Colors.BG_RED}{Colors.WHITE} [IMD: FAIL] {Colors.RESET}"

                if classification == "Natural Weather Event":
                    status_badge = f"{Colors.BG_BLUE}{Colors.WHITE} NATURAL WEATHER: ZERO FALSE ALARM {Colors.RESET}"
                    mse_color = Colors.CYAN
                elif classification == "Sensor Defect":
                    status_badge = f"{Colors.BG_RED}{Colors.WHITE} HARDWARE DEFECT: {defect_type.upper()} {Colors.RESET}"
                    mse_color = Colors.RED
                elif classification == "Compound Event":
                    status_badge = f"{Colors.YELLOW} STORM + SENSOR DEGRADATION {Colors.RESET}"
                    mse_color = Colors.YELLOW
                else:
                    status_badge = f"{Colors.GREEN} STATION HEALTHY (NOMINAL) {Colors.RESET}"
                    mse_color = Colors.GREEN

                mse_str = f"{mse_color}MSE={reconstruction_error:.4f}{Colors.RESET}"
                conf_str = f"Conf={conf_score:.1f}%"
                lat_str = f"{Colors.DIM}{latency:3.0f}ms{Colors.RESET}"

                print(f"[{time_str}] {seq_str} | {readings} | {imd_badge} | {mse_str} | {conf_str} | {status_badge} | {lat_str}")

            except urllib.error.URLError as e:
                consecutive_errors += 1
                if consecutive_errors == 1:
                    print(f"{Colors.RED}[Connection Error] Backend not reachable at {self.endpoint}. Is uvicorn running? ({e}){Colors.RESET}")
                elif consecutive_errors % 5 == 0:
                    print(f"{Colors.DIM}[Waiting for backend at {self.endpoint}...] (attempt {consecutive_errors}){Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[Error] {e}{Colors.RESET}")

            time.sleep(1.0)

def main():
    parser = argparse.ArgumentParser(description="SkyGuard AI — Edge Station Telemetry Streamer & Physics Validator")
    parser.add_argument("--endpoint", default="http://localhost:8000/api/v1/telemetry/ingest", help="Backend telemetry ingestion endpoint")
    parser.add_argument("--station", default="AGRA-01", help="Weather station ID")
    parser.add_argument("--scenario", default="nominal", choices=["nominal", "squall", "drift", "freeze", "spike"], help="Initial scenario to stream")
    parser.add_argument("--random", action="store_true", help="Start in autonomous random chaos mode")
    args = parser.parse_args()

    runner = EdgeStationRunner(
        endpoint=args.endpoint,
        station_id=args.station,
        mode=args.scenario,
        random_transitions=args.random
    )
    runner.run()

if __name__ == "__main__":
    main()
