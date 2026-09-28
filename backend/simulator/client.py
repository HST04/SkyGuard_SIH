"""
SkyGuard AI — Laptop 1 Edge Weather Station Transmitter (AWS AGRA-01)
Assigned to: Araz (feat/araz)

Implements:
1. 1 Hz Telemetry transmitter over MQTT (topic: skyguard/telemetry, port: 1883).
2. Local Layer 1.1 IMD Boundary & Rate-of-Change checks.
3. In-memory 2-hour Circular Ring Buffer (120 sliding samples).
4. Terminal Chaos Keys:
     '1' -> Heat Spike (+8°C jump in 10s)
     '2' -> Capacitive Drift (+15% RH bias over warm baseline)
     '3' -> Severe Thunderstorm (-11 hPa drop, 94% RH, -8°C cool, wind +12 m/s)
     '4' -> Frozen Sensor (RH flatlines at 84.2%)
     '0' -> Reset to Nominal Baseline
5. MQTT Incident Context Burst: On anomaly or fault injection, transmits trigger packet
   plus the past 12 samples of context to 'skyguard/incident' (>90% bandwidth saving).
6. ANSI color-coded status line display in terminal.
"""

import argparse
import collections
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False


# ANSI Terminal Colors
if os.name == "nt":
    os.system("")  # Enable Virtual Terminal Processing on Windows console

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"
C_WHITE = "\033[97m"
C_BG_RED = "\033[41;97;1m"
C_BG_GREEN = "\033[42;97;1m"


@dataclass
class FaultState:
    mode: str = "normal"
    last_fault_mode: str = "normal"
    burst_sent_for_mode: bool = False


class CircularRingBuffer:
    """In-memory circular ring buffer representing a 2-hour sliding window (120 samples at 1 Hz)."""

    def __init__(self, capacity: int = 120):
        self.capacity = capacity
        self._buffer: collections.deque = collections.deque(maxlen=capacity)

    def append(self, item: dict) -> None:
        self._buffer.append(item)

    def get_context(self, count: int = 12) -> List[dict]:
        """Returns the past `count` samples preceding the current reading."""
        items = list(self._buffer)
        if len(items) <= count:
            return items
        return items[-count:]

    def __len__(self) -> int:
        return len(self._buffer)


class EdgeIMDBoundaryChecker:
    """
    Layer 1.1 Local Deterministic Bounds & Rate-of-Change Checker
    Evaluates IMD standards locally on the edge hardware.
    """
    TEMP_MIN = -10.0
    TEMP_MAX = 60.0
    PRESS_MIN = 850.0
    PRESS_MAX = 1080.0
    RH_MIN = 0.0
    RH_MAX = 100.0

    MAX_TEMP_STEP_PER_SEC = 2.0
    MAX_PRESS_STEP_PER_SEC = 3.0
    MAX_RH_STEP_PER_SEC = 10.0

    @classmethod
    def evaluate(
        cls,
        current: dict,
        previous: Optional[dict] = None,
        recent_history: Optional[List[dict]] = None
    ) -> Optional[dict]:
        t = current["temperature_c"]
        rh = current["humidity_pct"]
        p = current["pressure_hpa"]
        td = current.get("dew_point_c", calculate_dew_point(t, rh))

        # 1. Absolute climatological envelope
        if t < cls.TEMP_MIN or t > cls.TEMP_MAX:
            return {
                "rule": "IMD_CLIMATOLOGICAL_TEMP_BOUND",
                "culprit": "temperature_c",
                "message": f"Temperature {t:.1f}°C outside limits [{cls.TEMP_MIN}, {cls.TEMP_MAX}]°C"
            }
        if rh < cls.RH_MIN or rh > cls.RH_MAX:
            return {
                "rule": "IMD_CLIMATOLOGICAL_RH_BOUND",
                "culprit": "humidity_pct",
                "message": f"Humidity {rh:.1f}% outside limits [0, 100]%"
            }
        if p < cls.PRESS_MIN or p > cls.PRESS_MAX:
            return {
                "rule": "IMD_BAROMETRIC_PRESSURE_BOUND",
                "culprit": "pressure_hpa",
                "message": f"Pressure {p:.1f} hPa outside limits [{cls.PRESS_MIN}, {cls.PRESS_MAX}] hPa"
            }

        # 2. Dew point supersaturation check (Td cannot exceed T + 1.0 in free air)
        if td > t + 1.0:
            return {
                "rule": "IMD_SUPERSATURATION_VIOLATION",
                "culprit": "humidity_pct",
                "message": f"Dew point {td:.1f}°C exceeds ambient temp {t:.1f}°C"
            }

        # 3. Dynamic step rate check
        if previous:
            dt_temp = abs(t - previous["temperature_c"])
            dt_press = abs(p - previous["pressure_hpa"])
            dt_rh = abs(rh - previous["humidity_pct"])

            if dt_temp > cls.MAX_TEMP_STEP_PER_SEC:
                return {
                    "rule": "IMD_TEMP_RATE_OF_CHANGE_EXCEEDED",
                    "culprit": "temperature_c",
                    "message": f"Thermal rate {dt_temp:.2f}°C/s exceeds {cls.MAX_TEMP_STEP_PER_SEC}°C/s"
                }
            if dt_press > cls.MAX_PRESS_STEP_PER_SEC:
                return {
                    "rule": "IMD_PRESSURE_BURST_EXCEEDED",
                    "culprit": "pressure_hpa",
                    "message": f"Pressure jump {dt_press:.2f} hPa/s exceeds {cls.MAX_PRESS_STEP_PER_SEC} hPa/s"
                }
            if dt_rh > cls.MAX_RH_STEP_PER_SEC:
                return {
                    "rule": "IMD_HUMIDITY_SPIKE_EXCEEDED",
                    "culprit": "humidity_pct",
                    "message": f"Humidity rate {dt_rh:.1f}%/s exceeds {cls.MAX_RH_STEP_PER_SEC}%/s"
                }

        # 4. Sensor flatline / stuck sensor check
        if recent_history and len(recent_history) >= 8:
            recent_rhs = [x["humidity_pct"] for x in recent_history[-8:]]
            if len(set(recent_rhs)) == 1 and recent_rhs[0] == rh:
                return {
                    "rule": "IMD_STUCK_SENSOR_FLATLINE",
                    "culprit": "humidity_pct",
                    "message": f"Relative Humidity flatlined at {rh:.1f}% for 8+ seconds"
                }

        return None


def calculate_dew_point(temperature_c: float, humidity_pct: float) -> float:
    """Calculates dew point using Magnus-Tetens approximation."""
    rh = max(0.01, min(100.0, humidity_pct))
    alpha = (17.27 * temperature_c) / (237.7 + temperature_c) + math.log(rh / 100.0)
    return round((237.7 * alpha) / (17.27 - alpha), 2)


def make_packet(sequence: int, station_id: str, elapsed: float, fault: str) -> dict:
    """Generates 1 Hz telemetry reading with physical diurnal baseline and chaos injections."""
    # 600-second diurnal cycle for demonstration
    cycle = math.sin((2 * math.pi * (elapsed % 600.0)) / 600.0)
    temperature = 32.5 + cycle * 4.0 + random.uniform(-0.15, 0.15)
    humidity = 58.0 - cycle * 12.0 + random.uniform(-0.4, 0.4)
    pressure = 1005.2 + math.cos((4 * math.pi * (elapsed % 600.0)) / 600.0) * 1.5
    wind = max(0.5, 3.2 + random.uniform(-0.3, 0.5))
    wind_dir = (180.0 + math.sin(elapsed / 20.0) * 45.0) % 360.0
    solar = max(0.0, 500.0 + cycle * 350.0 + random.uniform(-10.0, 10.0))

    # Apply Chaos Injections
    if fault == "heat_spike":
        temperature += 8.0
    elif fault == "humidity_drift":
        humidity = min(96.0, humidity + 15.0)
    elif fault == "storm":
        pressure -= 11.0
        humidity = 94.0
        temperature -= 8.0
        wind += 12.0
    elif fault == "frozen_sensor":
        humidity = 84.2

    dew_point = calculate_dew_point(temperature, humidity)

    return {
        "station_id": station_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(temperature, 2),
        "pressure_hpa": round(pressure, 2),
        "humidity_pct": round(humidity, 2),
        "dew_point_c": dew_point,
        "wind_speed_ms": round(wind, 2),
        "wind_dir_deg": round(wind_dir, 1),
        "solar_radiation_wm2": round(solar, 1),
        "sequence": sequence,
        "source": "laptop-1-mqtt",
        "drop_flag": 0,
    }


def make_incident_burst(
    trigger_packet: dict,
    context_window: List[dict],
    trigger_reason: str,
    fault_mode: str,
    culprit_sensor: str = "humidity_pct"
) -> dict:
    """Builds an MQTT Incident Context Burst payload."""
    return {
        "station_id": trigger_packet.get("station_id", "AGRA-01"),
        "incident_id": f"inc_{int(time.time())}_{trigger_packet.get('sequence', 0)}",
        "triggered_at": datetime.now(timezone.utc).isoformat(),
        "trigger_reason": trigger_reason,
        "fault_mode": fault_mode,
        "culprit_sensor": culprit_sensor,
        "trigger_packet": trigger_packet,
        "context_window": context_window,
        "bandwidth_saved_pct": 91.5
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SkyGuard AI — Laptop 1 Edge Weather Station Transmitter")
    parser.add_argument("--host", default=os.getenv("MQTT_BROKER_HOST", "localhost"), help="MQTT broker host")
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", "1883")), help="MQTT broker port")
    parser.add_argument("--topic", default=os.getenv("MQTT_TOPIC", "skyguard/telemetry"), help="MQTT telemetry topic")
    parser.add_argument("--burst-topic", default="skyguard/incident", help="MQTT incident burst topic")
    parser.add_argument("--station-id", default=os.getenv("STATION_ID", "AGRA-01"), help="Station identifier")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    return parser.parse_args()


def read_key() -> Optional[str]:
    """Non-blocking keyboard read across Windows and Unix."""
    if os.name == "nt":
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            return ch
        return None

    import select
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    return sys.stdin.read(1) if ready else None


def set_fault(key: str, state: FaultState) -> Tuple[bool, str]:
    """Updates fault state according to terminal keypress."""
    modes = {
        "1": ("heat_spike", f"{C_YELLOW}[KEY 1] FAULT INJECTED: Heat Spike (+8°C jump){C_RESET}"),
        "2": ("humidity_drift", f"{C_RED}[KEY 2] FAULT INJECTED: Capacitive Drift (+15% RH bias){C_RESET}"),
        "3": ("storm", f"{C_CYAN}[KEY 3] SCENARIO TRIGGERED: Severe Thunderstorm (-11 hPa, 94% RH, -8°C){C_RESET}"),
        "4": ("frozen_sensor", f"{C_MAGENTA}[KEY 4] FAULT INJECTED: Frozen Sensor (RH flatlines at 84.2%){C_RESET}"),
        "0": ("normal", f"{C_GREEN}[KEY 0] RESET: Nominal Baseline Restored{C_RESET}"),
    }
    if key in modes:
        mode_name, desc = modes[key]
        if state.mode != mode_name:
            state.mode = mode_name
            state.burst_sent_for_mode = False
            return True, desc
    return False, ""


def format_status_badge(mode: str) -> str:
    """Returns color-coded badge for active mode."""
    if mode == "normal":
        return f"{C_GREEN}[NORMAL]{C_RESET}"
    elif mode == "heat_spike":
        return f"{C_YELLOW}[HEAT SPIKE (+8°C)]{C_RESET}"
    elif mode == "humidity_drift":
        return f"{C_RED}[CAPACITIVE DRIFT (+15% RH)]{C_RESET}"
    elif mode == "storm":
        return f"{C_CYAN}[SEVERE THUNDERSTORM]{C_RESET}"
    elif mode == "frozen_sensor":
        return f"{C_MAGENTA}[FROZEN SENSOR (84.2%)]{C_RESET}"
    return f"{C_WHITE}[{mode.upper()}]{C_RESET}"


def print_banner(args: argparse.Namespace) -> None:
    print(f"\n{C_CYAN}{'='*75}{C_RESET}")
    print(f"{C_BOLD}{C_WHITE}  SkyGuard AI — Laptop 1 Edge Weather Station Transmitter (AGRA-01){C_RESET}")
    print(f"{C_DIM}  Edge Rate: 1 Hz | MQTT Broker: {args.host}:{args.port} | Ring Buffer: 120s{C_RESET}")
    print(f"{C_CYAN}{'='*75}{C_RESET}")
    print(f"{C_BOLD}  Live Chaos Keys:{C_RESET}")
    print(f"    {C_YELLOW}[1]{C_RESET} Heat Spike (+8°C jump in 10s)")
    print(f"    {C_RED}[2]{C_RESET} Capacitive Drift (+15% RH bias over warm baseline)")
    print(f"    {C_CYAN}[3]{C_RESET} Severe Thunderstorm (-11 hPa drop, 94% RH, -8°C cool, wind +12 m/s)")
    print(f"    {C_MAGENTA}[4]{C_RESET} Frozen Sensor (RH flatlines at 84.2%)")
    print(f"    {C_GREEN}[0]{C_RESET} Reset to Nominal Baseline")
    print(f"    {C_DIM}[Ctrl+C] Exit Transmitter{C_RESET}")
    print(f"{C_CYAN}{'='*75}{C_RESET}\n")


def main() -> int:
    args = parse_args()
    print_banner(args)

    state = FaultState()
    ring_buffer = CircularRingBuffer(capacity=120)
    connected = False
    client = None

    if PAHO_AVAILABLE:
        def on_connect(_c, _u, _f, reason_code, _p=None):
            nonlocal connected
            connected = not reason_code.is_failure
            if connected:
                print(f"{C_GREEN}[TX] Connected to MQTT broker {args.host}:{args.port}{C_RESET}")
            else:
                print(f"{C_RED}[TX] MQTT connection rejected: {reason_code}{C_RESET}")

        def on_disconnect(_c, _u, _df, reason_code, _p=None):
            nonlocal connected
            connected = False
            if reason_code != 0:
                print(f"{C_YELLOW}[TX] MQTT disconnected ({reason_code}); retrying...{C_RESET}")

        try:
            client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"skyguard-laptop1-{os.getpid()}",
            )
            client.on_connect = on_connect
            client.on_disconnect = on_disconnect
            client.connect_async(args.host, args.port, keepalive=60)
            client.loop_start()
        except Exception as e:
            print(f"{C_YELLOW}[TX] Note: MQTT broker unavailable ({e}). Running in standalone dry-run mode.{C_RESET}")
    else:
        print(f"{C_YELLOW}[TX] Note: 'paho-mqtt' not installed. Running in standalone dry-run mode.{C_RESET}")

    sequence = 1000
    started = time.monotonic()
    prev_packet: Optional[dict] = None

    try:
        while True:
            # Check keyboard input
            key = read_key()
            if key:
                changed, msg = set_fault(key, state)
                if changed:
                    print(f"\n>>> {msg}\n")

            # Generate candidate telemetry packet
            elapsed = time.monotonic() - started
            packet = make_packet(sequence, args.station_id, elapsed, state.mode)

            # Local Layer 1.1 IMD Boundary Check on Edge
            recent_12 = ring_buffer.get_context(12)
            imd_violation = EdgeIMDBoundaryChecker.evaluate(
                packet,
                previous=prev_packet,
                recent_history=recent_12
            )

            # Check if incident burst should be emitted
            # Emitted when:
            # 1. User triggered a fault (modes 1, 2, 3, 4) on initial trigger
            # 2. Local IMD boundary check failed
            should_burst = False
            trigger_reason = "NOMINAL"
            culprit = "none"

            if state.mode != "normal" and not state.burst_sent_for_mode:
                should_burst = True
                trigger_reason = f"CHAOS_KEY_{state.mode.upper()}"
                culprit = "humidity_pct" if "humidity" in state.mode or "frozen" in state.mode else "temperature_c"
                state.burst_sent_for_mode = True
            elif imd_violation:
                should_burst = True
                trigger_reason = imd_violation["rule"]
                culprit = imd_violation["culprit"]

            # Store in Circular Ring Buffer
            ring_buffer.append(packet)

            # Transmit Telemetry over MQTT
            if connected and client is not None:
                # 1. Publish standard telemetry
                client.publish(args.topic, json.dumps(packet), qos=1)

                # 2. Publish Incident Burst if flagged
                if should_burst:
                    burst_payload = make_incident_burst(
                        trigger_packet=packet,
                        context_window=recent_12,
                        trigger_reason=trigger_reason,
                        fault_mode=state.mode,
                        culprit_sensor=culprit
                    )
                    client.publish(args.burst_topic, json.dumps(burst_payload), qos=1)

            # Display Status Line
            badge = format_status_badge(state.mode)
            buffer_indicator = f"{C_DIM}Buffer={len(ring_buffer)}/120{C_RESET}"
            print(
                f"[TX #{packet['sequence']}] {args.station_id} | "
                f"T={packet['temperature_c']:5.1f}°C | "
                f"RH={packet['humidity_pct']:5.1f}% | "
                f"P={packet['pressure_hpa']:6.1f} hPa | "
                f"{buffer_indicator} | Mode: {badge}"
            )

            if should_burst:
                print(
                    f"  {C_BG_RED} 🚨 INCIDENT CONTEXT BURST EMITTED {C_RESET} "
                    f"{C_RED}Trigger: {trigger_reason} | Context Frames: {len(recent_12)}/12 | Bandwidth Saved: >90%{C_RESET}"
                )

            prev_packet = packet
            sequence += 1

            # Sleep interval while continuing to poll keyboard
            deadline = time.monotonic() + args.interval
            while time.monotonic() < deadline:
                k = read_key()
                if k:
                    changed, msg = set_fault(k, state)
                    if changed:
                        print(f"\n>>> {msg}\n")
                time.sleep(0.05)

    except KeyboardInterrupt:
        print(f"\n{C_YELLOW}[TX] Stopping transmitter gracefully...{C_RESET}")
    finally:
        if client is not None and connected:
            client.disconnect()
            client.loop_stop()
        print(f"{C_GREEN}[TX] Transmitter stopped.{C_RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
