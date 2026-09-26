"""Interactive MQTT weather-station transmitter for Laptop 1."""

import argparse
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import paho.mqtt.client as mqtt


@dataclass
class FaultState:
    mode: str = "normal"


def calculate_dew_point(temperature_c: float, humidity_pct: float) -> float:
    rh = max(0.01, min(100.0, humidity_pct))
    alpha = (17.27 * temperature_c) / (237.7 + temperature_c) + math.log(rh / 100.0)
    return round((237.7 * alpha) / (17.27 - alpha), 2)


def make_packet(sequence: int, station_id: str, elapsed: float, fault: str) -> dict:
    cycle = math.sin((2 * math.pi * (elapsed % 600.0)) / 600.0)
    temperature = 32.5 + cycle * 4.0 + random.uniform(-0.15, 0.15)
    humidity = 58.0 - cycle * 12.0 + random.uniform(-0.4, 0.4)
    pressure = 1005.2 + math.cos((4 * math.pi * (elapsed % 600.0)) / 600.0) * 1.5
    wind = max(0.5, 3.2 + random.uniform(-0.3, 0.5))
    solar = max(0.0, 500.0 + cycle * 350.0 + random.uniform(-10.0, 10.0))

    if fault == "heat_spike":
        temperature += 8.0
    elif fault == "humidity_drift":
        humidity = min(96.0, humidity + 15.0)
    elif fault == "storm":
        pressure -= 11.0
        humidity = 94.0
        temperature -= 8.0
        wind += 8.0

    return {
        "station_id": station_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(temperature, 2),
        "pressure_hpa": round(pressure, 2),
        "humidity_pct": round(humidity, 2),
        "dew_point_c": calculate_dew_point(temperature, humidity),
        "wind_speed_ms": round(wind, 2),
        "wind_dir_deg": round((180.0 + math.sin(elapsed / 20.0) * 45.0) % 360.0, 1),
        "solar_radiation_wm2": round(solar, 1),
        "sequence": sequence,
        "source": "laptop-1-mqtt",
        "drop_flag": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("MQTT_BROKER_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", "1883")))
    parser.add_argument("--topic", default=os.getenv("MQTT_TOPIC", "skyguard/telemetry"))
    parser.add_argument("--station-id", default=os.getenv("STATION_ID", "AGRA-01"))
    parser.add_argument("--interval", type=float, default=1.0)
    return parser.parse_args()


def read_key() -> Optional[str]:
    if os.name == "nt":
        import msvcrt

        if msvcrt.kbhit():
            return msvcrt.getwch()
        return None

    import select

    ready, _, _ = select.select([sys.stdin], [], [], 0)
    return sys.stdin.read(1) if ready else None


def set_fault(key: str, state: FaultState) -> None:
    modes = {
        "1": ("heat_spike", "FAULT INJECTED: HEAT SPIKE (+8 C)"),
        "2": ("humidity_drift", "FAULT INJECTED: CAPACITIVE DRIFT (+15% RH)"),
        "3": ("storm", "SCENARIO INJECTED: SEVERE THUNDERSTORM"),
        "0": ("normal", "RESET TO NORMAL"),
    }
    if key in modes:
        state.mode, message = modes[key]
        print(f"\n>>> {message}")


def main() -> int:
    args = parse_args()
    state = FaultState()
    connected = False

    def on_connect(
        _client: mqtt.Client,
        _userdata: object,
        _flags: object,
        reason_code: mqtt.ReasonCode,
        _properties: Optional[mqtt.Properties],
    ) -> None:
        nonlocal connected
        connected = not reason_code.is_failure
        if connected:
            print(f"[TX] Connected to MQTT broker {args.host}:{args.port}")
        else:
            print(f"[TX] MQTT connection rejected: {reason_code}")

    def on_disconnect(
        _client: mqtt.Client,
        _userdata: object,
        _disconnect_flags: object,
        reason_code: mqtt.ReasonCode,
        _properties: Optional[mqtt.Properties],
    ) -> None:
        nonlocal connected
        connected = False
        if reason_code != mqtt.MQTT_ERR_SUCCESS:
            print(f"[TX] MQTT disconnected ({reason_code}); retrying automatically")

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"skyguard-laptop1-{os.getpid()}",
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect_async(args.host, args.port, keepalive=60)
    client.loop_start()

    sequence = 1000
    started = time.monotonic()
    print("[TX] Keys: 1=heat spike, 2=humidity drift, 3=storm, 0=normal, Ctrl+C=stop")
    try:
        while True:
            key = read_key()
            if key:
                set_fault(key, state)

            packet = make_packet(
                sequence,
                args.station_id,
                time.monotonic() - started,
                state.mode,
            )
            if connected:
                result = client.publish(args.topic, json.dumps(packet), qos=1)
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    print(f"[TX] Publish failed: {mqtt.error_string(result.rc)}")
            status = "NORMAL" if state.mode == "normal" else state.mode.upper()
            print(
                f"[TX SEQ #{sequence}] Station {args.station_id}: "
                f"Temp={packet['temperature_c']:.1f} C | "
                f"Humidity={packet['humidity_pct']:.1f}% | Status={status}"
            )
            sequence += 1

            deadline = time.monotonic() + args.interval
            while time.monotonic() < deadline:
                key = read_key()
                if key:
                    set_fault(key, state)
                time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[TX] Stopping transmitter")
    finally:
        client.disconnect()
        client.loop_stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
