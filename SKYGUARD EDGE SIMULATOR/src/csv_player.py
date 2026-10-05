"""CSV Dataset Playback Reader.
Reads pre-generated meteorological CSV datasets row-by-row for verified streaming
to the AWS Edge transmitter, cross-referencing file line numbers with transmitted payloads.
"""

import csv
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.models.weather_physics import WeatherReading

class CSVPlayer:
    """Streams weather readings from a CSV file with line tracking and verification metadata."""

    def __init__(self, csv_filepath: str, loop: bool = True):
        self.csv_filepath = csv_filepath
        self.loop = loop
        self.rows: List[Dict[str, str]] = []
        self.current_index = 0
        self.load_csv()

    def load_csv(self):
        """Loads and parses all records from the target CSV file."""
        if not os.path.exists(self.csv_filepath):
            raise FileNotFoundError(f"CSV file not found: {self.csv_filepath}")

        with open(self.csv_filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.rows = list(reader)

        if not self.rows:
            raise ValueError(f"CSV file {self.csv_filepath} contains no data rows!")

    @property
    def total_rows(self) -> int:
        return len(self.rows)

    @property
    def filename(self) -> str:
        return os.path.basename(self.csv_filepath)

    def get_next(self) -> Optional[WeatherReading]:
        """Returns the next row converted to a WeatherReading object."""
        if self.current_index >= len(self.rows):
            if self.loop:
                self.current_index = 0
            else:
                return None

        row = self.rows[self.current_index]
        self.current_index += 1

        # Use fresh timestamp for real-time edge transmission
        now_utc = datetime.now(timezone.utc)
        timestamp_ms = int(now_utc.timestamp() * 1000)
        iso_time = now_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"

        return WeatherReading(
            timestamp_ms=timestamp_ms,
            iso_time=iso_time,
            temperature_c=float(row.get("temperature_c", 25.0)),
            humidity_pct=float(row.get("humidity_pct", 60.0)),
            pressure_hpa=float(row.get("pressure_hpa", 1013.0)),
            wind_speed_mps=float(row.get("wind_speed_mps", 4.0)),
            wind_direction_deg=float(row.get("wind_direction_deg", 180.0)),
            solar_radiation_wm2=float(row.get("solar_radiation_wm2", 0.0)),
            precipitation_mmh=float(row.get("precipitation_mmh", 0.0)),
            battery_pct=float(row.get("battery_pct", 95.0)),
            voltage_v=float(row.get("voltage_v", 3.8)),
            rssi_dbm=int(row.get("rssi_dbm", -65)),
        )

    def get_source_metadata(self) -> Dict[str, Any]:
        """Returns current verification metadata to embed into outgoing payloads."""
        return {
            "source_file": self.filename,
            "source_row": self.current_index,
            "total_rows": self.total_rows,
        }
