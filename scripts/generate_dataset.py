"""
SkyGuard AI — Comprehensive Weather & Fault Dataset Generator (Agra AWS Station)
Revised & Updated according to PRD v2.1 and ML Strat v2.0.

Generates:
  1. data/train_baseline_normal.csv (15,000 timesteps, 10-min cadence, clean diurnal physics)
  2. data/test_fault_injections.csv (Multi-class evaluation dataset with dual labels:
     weather_class: 'nominal' | 'squall'
     defect_class: 'none' | 'frozen_value' | 'capacitive_drift' | 'impulse_spike' | 'noise_burst' | 'packet_dropout')
"""

import os
import math
import random
import csv
from datetime import datetime, timedelta

def calculate_dew_point(t_c: float, rh_pct: float) -> float:
    """Magnus-Tetens formula for physically consistent dew point."""
    rh = max(0.01, min(100.0, rh_pct))
    a, b = 17.27, 237.7
    alpha = ((a * t_c) / (b + t_c)) + math.log(rh / 100.0)
    td = (b * alpha) / (a - alpha)
    # Physical sanity: dew point cannot exceed air temperature + 0.5C
    return min(t_c + 0.5, round(td, 2))

def generate_datasets():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)

    start_date = datetime(2025, 9, 1, 0, 0, 0)
    num_train_samples = 15000

    print("=====================================================================")
    print("SkyGuard AI: Generating Revised Normal Baseline Dataset (Agra AWS)...")
    print("=====================================================================")

    train_records = []
    prev_t, prev_p, prev_rh = None, None, None

    for i in range(num_train_samples):
        curr_time = start_date + timedelta(minutes=10 * i)
        hour_frac = curr_time.hour + curr_time.minute / 60.0
        phase = 2 * math.pi * ((hour_frac - 14.0) / 24.0)

        # Diurnal Temperature: 22°C night to 38°C afternoon peak (mean 30.0, amplitude 8.0)
        t_base = 30.0 + 8.0 * math.cos(phase) + random.gauss(0, 0.25)

        # Relative Humidity: Inversely coupled (40% afternoon to 85% morning)
        rh_base = 62.5 - 22.5 * math.cos(phase) + random.gauss(0, 0.6)
        rh_base = max(35.0, min(92.0, rh_base))

        # Barometric Pressure: Semidiurnal tidal oscillation between 1002 and 1008 hPa
        p_base = 1005.0 + 2.5 * math.sin(4 * math.pi * (hour_frac / 24.0)) + random.gauss(0, 0.12)

        # Dew point
        td_base = calculate_dew_point(t_base, rh_base)

        # Wind & Solar
        wind_speed = max(0.5, 3.2 + 2.2 * math.cos(phase) + random.gauss(0, 0.4))
        wind_dir = (180.0 + 35.0 * math.sin(phase) + random.gauss(0, 10.0)) % 360.0
        solar = 0.0
        if 6.0 <= hour_frac <= 18.0:
            solar = max(0.0, 850.0 * math.sin(math.pi * (hour_frac - 6.0) / 12.0) + random.gauss(0, 15.0))

        # Physical derivatives
        dt_dt = 0.0 if prev_t is None else round(t_base - prev_t, 3)
        dp_dt = 0.0 if prev_p is None else round(p_base - prev_p, 3)
        drh_dt = 0.0 if prev_rh is None else round(rh_base - prev_rh, 3)

        prev_t, prev_p, prev_rh = t_base, p_base, rh_base

        train_records.append({
            "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            "station_id": "AGRA-01",
            "temperature_c": round(t_base, 2),
            "humidity_pct": round(rh_base, 2),
            "pressure_hpa": round(p_base, 2),
            "dew_point_c": round(td_base, 2),
            "wind_speed_ms": round(wind_speed, 2),
            "wind_dir_deg": round(wind_dir, 1),
            "solar_radiation_wm2": round(solar, 1),
            "dT_dt": dt_dt,
            "dP_dt": dp_dt,
            "dRH_dt": drh_dt,
            "drop_flag": 0,
            "weather_class": "nominal",
            "defect_class": "none"
        })

    train_fieldnames = [
        "timestamp", "station_id", "temperature_c", "humidity_pct", "pressure_hpa",
        "dew_point_c", "wind_speed_ms", "wind_dir_deg", "solar_radiation_wm2",
        "dT_dt", "dP_dt", "dRH_dt", "drop_flag", "weather_class", "defect_class"
    ]

    train_path = os.path.join(data_dir, "train_baseline_normal.csv")
    with open(train_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=train_fieldnames)
        writer.writeheader()
        writer.writerows(train_records)

    # Compute correlation
    temps = [r["temperature_c"] for r in train_records]
    rhs = [r["humidity_pct"] for r in train_records]
    n = len(temps)
    mean_t, mean_rh = sum(temps) / n, sum(rhs) / n
    num = sum((t - mean_t) * (rh - mean_rh) for t, rh in zip(temps, rhs))
    den = math.sqrt(sum((t - mean_t) ** 2 for t in temps) * sum((rh - mean_rh) ** 2 for rh in rhs))
    corr = num / den if den > 0 else 0.0

    print(f"Generated {len(train_records)} rows of normal baseline weather.")
    print(f"T-RH Physical Correlation: {corr:.3f} (Requirement: r < -0.70)")
    print(f"Saved: {train_path}\n")

    # Generate Multi-Class Test Dataset with Fault Injections
    print("=====================================================================")
    print("SkyGuard AI: Generating Revised Fault & Squall Evaluation Dataset...")
    print("=====================================================================")

    test_samples = 4000
    test_start = start_date + timedelta(days=105)
    test_records = []
    weather_counts = {}
    defect_counts = {}

    prev_t, prev_p, prev_rh = None, None, None

    for i in range(test_samples):
        curr_time = test_start + timedelta(minutes=10 * i)
        hour_frac = curr_time.hour + curr_time.minute / 60.0
        phase = 2 * math.pi * ((hour_frac - 14.0) / 24.0)

        t_base = 30.0 + 8.0 * math.cos(phase) + random.gauss(0, 0.25)
        rh_base = 62.5 - 22.5 * math.cos(phase) + random.gauss(0, 0.6)
        rh_base = max(35.0, min(92.0, rh_base))
        p_base = 1005.0 + 2.5 * math.sin(4 * math.pi * (hour_frac / 24.0)) + random.gauss(0, 0.12)
        wind_speed = max(0.5, 3.2 + 2.2 * math.cos(phase) + random.gauss(0, 0.4))
        wind_dir = 180.0
        solar = max(0.0, 850.0 * math.sin(math.pi * (hour_frac - 6.0) / 12.0)) if 6.0 <= hour_frac <= 18.0 else 0.0
        drop_flag = 0

        weather_class = "nominal"
        defect_class = "none"

        # 1. Severe Squall / Thunderstorm (Rows 400 to 520) - Model A True-Negative test
        if 400 <= i < 520:
            weather_class = "squall"
            defect_class = "none"
            prog = math.sin(math.pi * (i - 400) / 120.0)
            t_base -= 8.5 * prog
            p_base -= 12.0 * prog
            rh_base = min(96.0, rh_base + 32.0 * prog)
            wind_speed += 14.0 * prog

        # 2. Frozen Sensor Flatline (Rows 800 to 920) - Model B Defect
        elif 800 <= i < 920:
            weather_class = "nominal"
            defect_class = "frozen_value"
            rh_base = 84.2 # locked constant regardless of temperature climb

        # 3. Capacitive Calibration Drift (Rows 1400 to 1640) - Model B Defect
        elif 1400 <= i < 1640:
            weather_class = "nominal"
            defect_class = "capacitive_drift"
            prog = (i - 1400) / 240.0
            rh_base = min(98.0, rh_base + 15.0 * min(1.0, 0.5 + prog))

        # 4. Impulse Spike Defect (Rows 2100 to 2110) - Model B Defect
        elif 2100 <= i < 2110:
            weather_class = "nominal"
            defect_class = "impulse_spike"
            t_base += 8.2 # Sudden thermal impulse

        # 5. High-Frequency Gaussian Noise Burst (Rows 2600 to 2750) - Model B Defect
        elif 2600 <= i < 2750:
            weather_class = "nominal"
            defect_class = "noise_burst"
            p_base += random.gauss(0, 4.5) # Heavy uncoordinated noise on barometric channel

        # 6. Intermittent Packet Dropout (Rows 3200 to 3300) - Model B Defect
        elif 3200 <= i < 3300:
            weather_class = "nominal"
            defect_class = "packet_dropout"
            drop_flag = 1
            # Forward fill previous value (stale packet)
            if prev_t is not None:
                t_base, rh_base, p_base = prev_t, prev_rh, prev_p

        td_base = calculate_dew_point(t_base, rh_base)

        dt_dt = 0.0 if prev_t is None else round(t_base - prev_t, 3)
        dp_dt = 0.0 if prev_p is None else round(p_base - prev_p, 3)
        drh_dt = 0.0 if prev_rh is None else round(rh_base - prev_rh, 3)

        prev_t, prev_p, prev_rh = t_base, p_base, rh_base

        test_records.append({
            "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            "station_id": "AGRA-01",
            "temperature_c": round(t_base, 2),
            "humidity_pct": round(rh_base, 2),
            "pressure_hpa": round(p_base, 2),
            "dew_point_c": round(td_base, 2),
            "wind_speed_ms": round(wind_speed, 2),
            "wind_dir_deg": round(wind_dir, 1),
            "solar_radiation_wm2": round(solar, 1),
            "dT_dt": dt_dt,
            "dP_dt": dp_dt,
            "dRH_dt": drh_dt,
            "drop_flag": drop_flag,
            "weather_class": weather_class,
            "defect_class": defect_class
        })

        weather_counts[weather_class] = weather_counts.get(weather_class, 0) + 1
        defect_counts[defect_class] = defect_counts.get(defect_class, 0) + 1

    test_path = os.path.join(data_dir, "test_fault_injections.csv")
    with open(test_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=train_fieldnames)
        writer.writeheader()
        writer.writerows(test_records)

    print(f"Generated {len(test_records)} evaluation rows.")
    print("Weather Classes in Test Set:")
    for k, v in weather_counts.items():
        print(f"  - {k}: {v} rows")
    print("Defect Classes in Test Set:")
    for k, v in defect_counts.items():
        print(f"  - {k}: {v} rows")
    print(f"Saved: {test_path}")
    print("=====================================================================")

if __name__ == "__main__":
    generate_datasets()
