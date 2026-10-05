import json
import os
from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "endpoint_url": "http://localhost:8000/api/telemetry",
    "device_id": "aws-edge-in-station-04",
    "firmware_version": "v2.1.0-greengrass",
    "default_region": "mumbai_monsoon",
    "transmission_interval_sec": 1.0,
    "http_timeout_sec": 2.0,
    "include_ground_truth_metadata": True,
    "regions_metadata": {
        "mumbai_monsoon": {
            "display_name": "India-West (Mumbai Monsoon)",
            "latitude": 19.0760,
            "longitude": 72.8777
        },
        "delhi_summer": {
            "display_name": "India-North (Delhi Summer Heatwave)",
            "latitude": 28.6139,
            "longitude": 77.2090
        },
        "thar_desert": {
            "display_name": "India-NorthWest (Thar Arid Desert)",
            "latitude": 26.9124,
            "longitude": 70.9083
        },
        "bengaluru_temperate": {
            "display_name": "India-South (Bengaluru Temperate)",
            "latitude": 12.9716,
            "longitude": 77.5946
        }
    }
}

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Loads configuration from JSON file or falls back to defaults."""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"[Warning] Error reading {config_path}: {e}. Using defaults.")
    return DEFAULT_CONFIG.copy()
