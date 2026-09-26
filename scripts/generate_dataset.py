"""
SkyGuard AI — Weather Dataset Generator (Agra AWS Station)
Generates:
  1. data/train_baseline_normal.csv (10,000 rows, 10-min intervals, clean diurnal physics)
  2. data/test_fault_injections.csv (labeled evaluation dataset with injected anomalies)
"""

import os
import math
import random
import csv
from datetime import datetime, timedelta

def generate_datasets():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    start_date = datetime(2025, 9, 1, 0, 0, 0)
    num_samples = 10000

    print("Generating normal training baseline dataset (Agra AWS)...")
    
    records = []
    for i in range(num_samples):
        curr_time = start_date + timedelta(minutes=10 * i)
        
        # Diurnal phase: peak solar heating at 14:00 (2 PM), coolest at 05:00 AM
        hour_frac = curr_time.hour + curr_time.minute / 60.0
        # Phase shift so maximum is at 14.0
        phase = 2 * math.pi * ((hour_frac - 14.0) / 24.0)
        
        # Temperature: 24°C night to 36°C afternoon
        t_base = 30.0 + 6.0 * math.cos(phase) + random.gauss(0, 0.3)
        
        # Relative Humidity: Opposite of temperature (~45% afternoon, ~80% morning)
        # Cosine is aligned such that max RH is at morning (~05:00) and min RH at 14:00
        rh_base = 62.5 - 17.5 * math.cos(phase) + random.gauss(0, 0.8)
        rh_base = max(30.0, min(95.0, rh_base))
        
        # Pressure: Semidiurnal tidal oscillation around 1005 hPa
        p_base = 1005.0 + 1.8 * math.sin(4 * math.pi * (hour_frac / 24.0)) + random.gauss(0, 0.15)
        
        # Dew point approximation (Magnus formula)
        a, b = 17.27, 237.7
        alpha = ((a * t_base) / (b + t_base)) + math.log(rh_base / 100.0)
        td_base = (b * alpha) / (a - alpha)
        
        # Wind: Picks up in afternoon
        wind_speed = max(0.5, 3.0 + 2.0 * math.cos(phase) + random.gauss(0, 0.5))
        wind_dir = (180.0 + 40.0 * math.sin(phase) + random.gauss(0, 15.0)) % 360.0
        
        # Solar radiation: 0 at night, peak ~850 W/m² at noon
        solar = 0.0
        if 6.0 <= hour_frac <= 18.0:
            solar = 850.0 * math.sin(math.pi * (hour_frac - 6.0) / 12.0) + random.gauss(0, 20.0)
            solar = max(0.0, solar)
            
        records.append({
            "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_c": round(t_base, 2),
            "humidity_pct": round(rh_base, 2),
            "pressure_hpa": round(p_base, 2),
            "dew_point_c": round(td_base, 2),
            "wind_speed_ms": round(wind_speed, 2),
            "wind_dir_deg": round(wind_dir, 1),
            "solar_radiation_wm2": round(solar, 1),
            "label": "normal"
        })
        
    fieldnames = [
        "timestamp", "temperature_c", "humidity_pct", "pressure_hpa",
        "dew_point_c", "wind_speed_ms", "wind_dir_deg", "solar_radiation_wm2", "label"
    ]
    train_path = os.path.join(data_dir, "train_baseline_normal.csv")
    with open(train_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # Calculate Pearson correlation between Temperature and Relative Humidity
    temps = [r["temperature_c"] for r in records]
    rhs = [r["humidity_pct"] for r in records]
    n = len(temps)
    mean_t = sum(temps) / n
    mean_rh = sum(rhs) / n
    num = sum((t - mean_t) * (rh - mean_rh) for t, rh in zip(temps, rhs))
    den = math.sqrt(sum((t - mean_t) ** 2 for t in temps) * sum((rh - mean_rh) ** 2 for rh in rhs))
    corr = num / den if den > 0 else 0.0

    print(f"Generated {len(records)} rows of normal weather.")
    print(f"T-RH Physical Correlation: {corr:.2f} (Clean physical coupling: negative correlation)")
    print(f"Saved: {train_path}")

    # Generate Test Dataset with Fault Injections
    print("\nGenerating labeled fault test dataset...")
    test_samples = 3000
    test_start = start_date + timedelta(days=70)
    test_records = []
    counts = {}

    for i in range(test_samples):
        curr_time = test_start + timedelta(minutes=10 * i)
        hour_frac = curr_time.hour + curr_time.minute / 60.0
        phase = 2 * math.pi * ((hour_frac - 14.0) / 24.0)

        t_base = 30.0 + 6.0 * math.cos(phase) + random.gauss(0, 0.3)
        rh_base = 62.5 - 17.5 * math.cos(phase) + random.gauss(0, 0.8)
        p_base = 1005.0 + 1.8 * math.sin(4 * math.pi * (hour_frac / 24.0)) + random.gauss(0, 0.15)
        wind_speed = max(0.5, 3.0 + 2.0 * math.cos(phase) + random.gauss(0, 0.5))
        wind_dir = 180.0
        solar = max(0.0, 850.0 * math.sin(math.pi * (hour_frac - 6.0) / 12.0)) if 6.0 <= hour_frac <= 18.0 else 0.0

        label = "normal"

        # Injection 1: Severe Squall (Valid physical storm) — Rows 600 to 720
        if 600 <= i < 720:
            label = "valid_squall"
            progress = math.sin(math.pi * (i - 600) / 120)
            t_base -= 8.5 * progress
            p_base -= 11.5 * progress
            rh_base = min(96.0, rh_base + 35.0 * progress)
            wind_speed += 12.0 * progress

        # Injection 2: Capacitive Humidity Drift (+15% bias without thermal collapse) — Rows 1200 to 1440
        elif 1200 <= i < 1440:
            label = "capacitive_drift"
            rh_base = min(98.0, rh_base + 16.5)

        # Injection 3: Transient Heat Spike (+8°C jump in 10 mins) — Rows 2100 to 2120
        elif 2100 <= i < 2120:
            label = "heat_spike"
            t_base += 8.2

        # Recalculate dew point
        a, b = 17.27, 237.7
        alpha = ((a * t_base) / (b + t_base)) + math.log(max(1.0, rh_base) / 100.0)
        td_base = (b * alpha) / (a - alpha)

        test_records.append({
            "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_c": round(t_base, 2),
            "humidity_pct": round(rh_base, 2),
            "pressure_hpa": round(p_base, 2),
            "dew_point_c": round(td_base, 2),
            "wind_speed_ms": round(wind_speed, 2),
            "wind_dir_deg": round(wind_dir, 1),
            "solar_radiation_wm2": round(solar, 1),
            "label": label
        })
        counts[label] = counts.get(label, 0) + 1

    test_path = os.path.join(data_dir, "test_fault_injections.csv")
    with open(test_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_records)

    print(f"Generated {len(test_records)} test rows.")
    print(f"Label counts: {counts}")
    print(f"Saved: {test_path}")

if __name__ == "__main__":
    generate_datasets()
