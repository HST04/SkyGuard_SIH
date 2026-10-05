"""AWS IoT Edge Device HTTP Transmitter.
Formats telemetry into AWS IoT Greengrass / Core compliant JSON envelopes
and dispatches payloads via HTTP REST POST to teammate's ingestion endpoint.
"""

import math
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, Any, Optional
import requests

@dataclass
class TransmissionResult:
    success: bool
    status_code: Optional[int]
    message: str
    payload: Dict[str, Any]

class EdgeTransmitter:
    """Manages Automatic Weather Station (AWS) telemetry packaging and HTTP dispatch."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.endpoint_url = config.get("endpoint_url", "http://localhost:8000/api/v1/telemetry")
        self.device_id = config.get("device_id", "AGRA-01")
        self.firmware = config.get("firmware_version", "v2.1.0-aws-edge")
        self.timeout_sec = config.get("http_timeout_sec", 4.0)
        self.session = requests.Session()
        self.sequence_counter = 0

    def build_aws_payload(
        self,
        reading_data: Dict[str, Any],
        region_key: str,
        source_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Packages sensor telemetry into flattened TelemetryPayload format for backend ingestion."""
        regions = self.config.get("regions_metadata", {})
        meta = regions.get(region_key, {"display_name": region_key, "latitude": 20.0, "longitude": 77.0})

        gt = reading_data.get("_ground_truth", {})
        if source_metadata:
            gt.update(source_metadata)

        # Map active ground truth labels to backend fault_type
        active_labels = gt.get("active_labels", ["NORMAL"])
        fault_type = "normal"
        if any("CALIBRATION_DRIFT" in l for l in active_labels):
            fault_type = "temp_drift"
        elif any("STUCK" in l for l in active_labels):
            fault_type = "stuck_temp"
        elif any("ERRATIC_NOISE" in l or "noise" in l.lower() for l in active_labels):
            fault_type = "sensor_noise"
        elif any("STORM" in l or "squall" in l.lower() for l in active_labels):
            fault_type = "valid_squall"
        elif any("HEATWAVE" in l for l in active_labels):
            fault_type = "heatwave"
        elif any("COLD_SNAP" in l for l in active_labels):
            fault_type = "cold_snap"
        elif any("SPIKE" in l or "spike" in l.lower() for l in active_labels):
            fault_type = "heat_spike"
        elif any("NULL" in l or "drop" in l.lower() for l in active_labels):
            fault_type = "packet_drop"
        elif gt.get("status") not in (None, "NORMAL"):
            fault_type = active_labels[0].lower()

        temp = reading_data.get("temperature_c")
        if temp is None:
            temp = 25.0
        rh = reading_data.get("humidity_pct")
        if rh is None:
            rh = 60.0
        pressure = reading_data.get("pressure_hpa")
        if pressure is None:
            pressure = 1013.25

        # Magnus dew point calculation
        a, b = 17.27, 237.7
        rh_clamped = max(0.1, min(100.0, float(rh)))
        alpha = ((a * float(temp)) / (b + float(temp))) + math.log(rh_clamped / 100.0)
        dew_point = round((b * alpha) / (a - alpha), 2)

        self.sequence_counter += 1

        # Build unified payload supporting both flattened format and AWS IoT structure
        payload = {
            # Flattened format for FastAPI TelemetryPayload
            "station_id": self.device_id,
            "timestamp": reading_data.get("iso_time") or datetime.now(timezone.utc).isoformat(),
            "temperature_c": float(temp),
            "pressure_hpa": float(pressure),
            "humidity_pct": float(rh),
            "dew_point_c": dew_point,
            "wind_speed_ms": float(reading_data.get("wind_speed_mps") or 0.0),
            "wind_dir_deg": float(reading_data.get("wind_direction_deg") or 0.0),
            "solar_radiation_wm2": float(reading_data.get("solar_radiation_wm2") or 0.0),
            "sequence": self.sequence_counter,
            "source": "edge_simulator",
            "drop_flag": 0 if reading_data.get("temperature_c") is not None else 1,
            "fault_type": fault_type,

            # Standard AWS IoT Greengrass schema compatibility
            "deviceId": self.device_id,
            "isoTime": reading_data.get("iso_time") or datetime.now(timezone.utc).isoformat(),
            "location": {
                "region": meta.get("display_name", region_key),
                "latitude": meta.get("latitude", 20.0),
                "longitude": meta.get("longitude", 77.0),
            },
            "telemetry": {
                "temperature_c": float(temp),
                "relative_humidity_pct": float(rh),
                "pressure_hpa": float(pressure),
                "wind_speed_mps": float(reading_data.get("wind_speed_mps") or 0.0),
                "wind_direction_deg": float(reading_data.get("wind_direction_deg") or 0.0),
                "solar_radiation_wm2": float(reading_data.get("solar_radiation_wm2") or 0.0),
                "precipitation_mmh": float(reading_data.get("precipitation_mmh") or 0.0),
            },
            "device_health": {
                "battery_pct": reading_data.get("battery_pct"),
                "supply_voltage_v": reading_data.get("voltage_v"),
                "rssi_dbm": reading_data.get("rssi_dbm"),
                "firmware": self.firmware,
            },
            "_ground_truth": gt,
            "extra_data": {
                "region": meta.get("display_name", region_key),
                "latitude": meta.get("latitude", 20.0),
                "longitude": meta.get("longitude", 77.0),
                "battery_pct": reading_data.get("battery_pct"),
                "voltage_v": reading_data.get("voltage_v"),
                "rssi_dbm": reading_data.get("rssi_dbm"),
                "firmware": self.firmware,
                "_ground_truth": gt
            }
        }
        return payload

    def transmit(self, payload: Dict[str, Any]) -> TransmissionResult:
        """Sends HTTP POST to target endpoint with timeout protection."""
        try:
            response = self.session.post(
                self.endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json", "X-Edge-Device": self.device_id},
                timeout=self.timeout_sec,
            )
            if response.status_code in (200, 201, 202, 204):
                return TransmissionResult(
                    success=True,
                    status_code=response.status_code,
                    message=f"Delivered ({response.status_code})",
                    payload=payload,
                )
            else:
                return TransmissionResult(
                    success=False,
                    status_code=response.status_code,
                    message=f"HTTP {response.status_code}: {response.text[:60]}",
                    payload=payload,
                )
        except requests.exceptions.ConnectionError:
            return TransmissionResult(
                success=False,
                status_code=None,
                message="Connection refused (Target server offline)",
                payload=payload,
            )
        except requests.exceptions.Timeout:
            return TransmissionResult(
                success=False,
                status_code=None,
                message=f"HTTP Timeout (> {self.timeout_sec}s)",
                payload=payload,
            )
        except Exception as e:
            return TransmissionResult(
                success=False,
                status_code=None,
                message=f"Transmission error: {str(e)[:60]}",
                payload=payload,
            )
