# SkyGuard AWS Edge Device Simulator

A lightweight, high-fidelity **AWS IoT Edge Station Simulator** for demonstrating real-time weather anomaly detection vs. sensor hardware failure detection.

Built specifically for live hackathons, product demos, and technical judge evaluations.

---

## Key Features

1. **Transparent, Zero-Cheating Dataset Generator (`generate_dataset.py`)**:
   - Run live on screen in front of judges to show exact mathematical equations.
   - Computes authentic, non-repeating stochastic weather data using:
     - **Diurnal Solar Cycle** (Zenith angle radiative transfer)
     - **Magnus-Tetens Psychrometric Equation** (Relative humidity inverse correlation with temperature)
     - **Ornstein-Uhlenbeck Process** (Mean-reverting Gaussian random walk)
   - Calibrated against real **India Meteorological Department (IMD)** regional profiles (Mumbai Monsoon, Delhi Summer Heatwave, Thar Desert Arid, Bengaluru Temperate).
   - Generates a tamper-evident CSV with row counts and SHA-256 integrity checksum.

2. **Verified File Streaming (`run_simulator.py --csv <filename>`)**:
   - The simulator explicitly verifies on screen: `Source: CSV File: <filename> (Row X/Total)`.
   - Judges can cross-reference the open CSV against the outgoing telemetry stream line by line.

3. **Interactive Live Hotkey Injections**:
   - Clearly demonstrates the difference between **Real Weather Anomalies** (multivariate, physically correlated across pressure, wind, temperature, rain) and **Sensor Hardware Defects** (unphysical single-sensor flatlines, drifts, or electrical jitter).
   - Instant zero-latency hotkeys:
     - `[1]` Severe Storm (Weather Anomaly)
     - `[2]` Heatwave (Weather Anomaly)
     - `[3]` Cold Snap (Weather Anomaly)
     - `[4]` Stuck Temperature Sensor (Hardware Defect)
     - `[5]` Sensor Calibration Drift (Hardware Defect)
     - `[6]` High-Frequency Noise Spike (Hardware Defect)
     - `[7]` Packet Drop / Null Reading (Hardware Defect)
     - `[0]` Reset All to Normal Meteorological Operation
     - `[+]` / `[-]` Speed Up / Slow Down Playback Rate
     - `[Space]` Pause / Resume
     - `[Q]` Quit

4. **AWS IoT Greengrass / Core Compliant Payload**:
   - Formatted in standard AWS IoT JSON envelope with `deviceId`, `timestamp`, `isoTime`, `location`, `telemetry`, and `device_health` (battery %, voltage, RSSI).
   - Transmits via HTTP REST POST to your teammate's ingestion endpoint with graceful offline retry handling.

---

## Directory Structure

```
SKYGUARD EDGE SIMULATOR/
├── generate_dataset.py          # Standalone transparent dataset generator for judges
├── run_simulator.py             # Main edge simulator runner with interactive TUI
├── main.py                      # Alias to run_simulator.py
├── mock_receiver.py             # Optional local HTTP receiver for testing
├── config.json                  # Default endpoint, device ID, and climate metadata
├── HOW_THE_GENERATOR_WORKS.md   # Layman's explanation & 60-second judge presentation pitch
├── requirements.txt             # Minimal dependencies (rich, requests)
├── src/
│   ├── config.py                # Configuration loader
│   ├── csv_player.py            # CSV reader with row & verification tracking
│   ├── transmitter.py           # AWS IoT JSON formatter & HTTP POST dispatcher
│   ├── tui.py                   # Terminal UI dashboard with Windows hotkey capture
│   └── models/
│       ├── indian_climates.py   # IMD meteorological regional profiles
│       ├── weather_physics.py   # Diurnal, psychrometric & Ornstein-Uhlenbeck engine
│       └── fault_injector.py    # Weather anomaly vs sensor defect injector
└── tests/
    └── test_physics_and_faults.py # Automated unit test suite (11 test cases)
```

---

## Quickstart Guide

### 1. Installation
Install requirements (requires Python 3.9+):
```bash
pip install -r requirements.txt
```

### 2. Generate a Dataset Live (Step 1 of Judge Demo)
Run the generator interactively:
```bash
python generate_dataset.py
```
*Choose a region (e.g., `1` for Mumbai Monsoon), enter row count (e.g., `120`), and name the file `judge_demo.csv`.*

Or run via CLI flags:
```bash
python generate_dataset.py --region mumbai_monsoon --rows 120 --output judge_demo.csv
```

### 3. Stream the CSV through the AWS Edge Simulator (Step 2 of Judge Demo)
```bash
python run_simulator.py --csv judge_demo.csv
```
*The simulator will stream the exact CSV rows to your teammate's endpoint, displaying live readings, source file verification, and active status.*

### 4. (Optional) Run Local Mock Ingestion Server
If testing standalone without your teammate's backend running:
```bash
python mock_receiver.py --port 8000
```

---

## Configuration (`config.json`)

To point to your teammate's backend server, edit `config.json` or pass `--url`:
```json
{
  "endpoint_url": "http://localhost:8000/api/telemetry",
  "device_id": "aws-edge-in-station-04",
  "default_region": "mumbai_monsoon",
  "transmission_interval_sec": 1.0,
  "http_timeout_sec": 2.0
}
```

Or pass via command line:
```bash
python run_simulator.py --csv judge_demo.csv --url http://192.168.1.50:5000/ingest --interval 0.5
```

---

## Running Automated Tests

Run the full unit test suite:
```bash
python -m unittest discover -s tests
```
*(All 11 tests cover physical limits, stochastic non-repeating randomness, multi-sensor weather anomalies, single-sensor faults, and AWS payload format).*
