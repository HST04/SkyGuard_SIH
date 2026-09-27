# 🚀 SkyGuard AI — 48-Hour Rapid Submission Master Execution Checklist (TASKS.md)

> **Submission Deadline:** 2 Days (48 Hours)  
> **Sprint Objective:** Build, integrate, verify, and record a **two-laptop Split-Edge/Cloud demonstration** proving the full **SkyGuard AI Architecture** (Dual-Model Confluence, Predictive Maintenance, Imputation, and 3D Digital Twin) operating LIVE in real time at 1 Hz.
>
> **The Real-Time Split-Edge/Cloud Experience:**
> 1. **Laptop 1 (Hardware AWS Station / Edge Node):** Emulates on-site weather station `AGRA-01` running an ESP32 architecture profile: Layer 1.1 IMD Plausibility filter and Layer 1.2 Outlier detection, buffering normal data locally in a rolling ring buffer and transmitting incident bursts with a pre-anomaly context window over MQTT to the cloud when anomalies occur.
> 2. **Cloud (Azure VM + Supabase PostgreSQL with SQLite Fallback):** Real-time evaluations conducted by the **2.0 Cloud Analytics Layer**: Multi-Scale Analyzer feeds **Model A (Weather Classifier)** and **Model B (Sensor Defect Classifier, trained on synthetic fault injections)** into the **Classification Confluence Decision Matrix**, calculating exact confidence scores (0–100%), live SHAP attributions, Predictive Maintenance horizons (EWMA drift), and Imputed parameter values.
> 3. **Laptop 2 (IMD Central Control Room):** Displays the **Tabbed Live Operator Dashboard** in real time — active waveform metrics, Confluence Decision Banner, dynamic SHAP attribution bars, Sensor Health recalibration forecast, interactive Imputation recovery widget, and a 3D Digital Twin that auto-zooms into the culprit sensor the instant a defect is confirmed.
> 4. **Google Colab:** Dedicated single notebook for training the 1D-CNN Autoencoder, Model A (Weather Classifier), and Model B (Defect Classifier with synthetic faults), exporting weights, and producing benchmark curves for evaluation.
>
> **Team Rules:** 6 team members. **Zero human syntax writing.** Humans copy-paste AI prompts, set up accounts, review outputs, click cloud buttons, and run verification commands.

---

## 📌 Complete Split-Edge/Cloud System Architecture

```
  ┌─────────────────────────────────────────┐               ┌─────────────────────────────────────────────────────────┐
  │                LAPTOP 1                 │               │                        LAPTOP 2                         │
  │     "On-Site Hardware AWS (AGRA-01)"    │               │               "IMD Central Control Room"                │
  │                                         │               │                                                         │
  │  Python Edge Simulator (ESP32 Profile)  │               │  Next.js 14 Tabbed Dashboard & 3D Digital Twin          │
  │  - 1 Hz Telemetry Poll                  │               │  ┌───────────────────────────────────────────────────┐  │
  │  - Layer 1.1 IMD Boundary Rule Check    │               │  │ TAB 1: LIVE ML & CONFLUENCE BANNER                │  │
  │  - Layer 1.2 Outlier Filter             │               │  │ - MSE Waveform vs Threshold Line (tau = 0.042)    │  │
  │  - Layer 1.3 Rolling 2-Hour Ring Buffer │               │  │ - Confluence Status: Sensor Defect (92.4% Conf)   │  │
  │  - Interactive Chaos Keys:              │               │  │ TAB 2: EXPLAINABLE AI (SHAP HUB)                  │  │
  │    [1] Heat Spike (+8°C jump)           │               │  │ - Dynamic feature attribution bars & text reason  │  │
  │    [2] Capacitive Drift (+15% RH bias)  │               │  │ TAB 3: SENSOR HEALTH & PREDICTIVE MAINTENANCE     │  │
  │    [3] Severe Squall (-11 hPa, 94% RH)  │               │  │ - EWMA drift tracker; "Calibration due < 2 Weeks" │  │
  │    [4] Frozen Sensor (flatline)         │               │  │ TAB 4: IMPUTATION & DATA RECOVERY MODULE          │  │
  │    [0] Reset to Baseline Normal         │               │  │ - Suggested corrected value + "Accept & Impute"   │  │
  └────────────────────┬────────────────────┘               │  └───────────────────────────────────────────────────┘  │
                       │                                    │  - 3D Digital Twin Camera Lerp to Culprit Sensor        │
                       │ MQTT Uplink (Port 1883)            └───────────────────────────▲─────────────────────────────┘
                       ▼                                                                │
  ┌─────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────────┐
  │                                        AZURE VIRTUAL MACHINE (CLOUD CORE)                                         │
  │                                                                                                                   │
  │   ┌───────────────────────────┐                     ┌─────────────────────────────────────────────────────────┐   │
  │   │  Mosquitto MQTT Broker    │────────────────────▶│                  FastAPI Engine Core                    │   │
  │   │        (Port 1883)        │                     │                                                         │   │
  │   └───────────────────────────┘                     │  1. Multi-Scale Multivariate Analyzer (Short & Long)    │   │
  │                                                     │  2. Dual Models: Model A (Weather) & Model B (Defect)   │   │
  │                                                     │  3. Classification Confluence Matrix & Confidence Scorer│   │
  │                                                     │  4. Live SHAP Attribution Generator & Text Diagnostic   │   │
  │                                                     │  5. Predictive Maintenance Engine (EWMA Drift Horizon)  │   │
  │                                                     │  6. Imputation Engine (Surviving-Sensor Reconstruction) │   │
  │                                                     │  7. SSE Real-Time Event Broadcaster (1 Hz Stream)       │   │
  │                                                     └───────────────────────────┬─────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────┘
                                                                                    │
                                                                                    ▼ SQL (TLS) with local fallback
                                                                       ┌─────────────────────────┐
                                                                       │   SUPABASE POSTGRESQL   │
                                                                       │  - telemetry_records    │
                                                                       │  - anomaly_incidents    │
                                                                       │  - maintenance_forecasts│
                                                                       │  - operator_feedback   │
                                                                       │  (Fallback: SQLite db)  │
                                                                       └─────────────────────────┘
```

---

## 📅 48-Hour Rapid Submission Roadmap

| Period | Milestone | Tasks | Key Deliverable |
|---|---|---|---|
| **Day 1: Hours 0–6** | Foundation & Cloud Plumbing | **Task 1 & Task 2** | Supabase DB tables live (with auto SQLite fallback); Azure VM running Mosquitto + FastAPI. |
| **Day 1: Hours 6–12** | Data Science & Colab Training | **Task 3 & Task 4** | Synthetic weather & fault dataset generated; Colab notebook trains Autoencoder, Model A & Model B; artifacts downloaded. |
| **Day 1: Hours 12–24** | Cloud Confluence & Maintenance Engine | **Task 5** | FastAPI implements Multi-Scale Analyzer, Confluence Matrix, Predictive Maintenance & Imputation. |
| **Day 2: Hours 25–34** | Edge Simulation & Tabbed Dashboard | **Task 6 & Task 7** | Laptop 1 running Python Edge transmitter with ring buffer & chaos keys; Laptop 2 showing full tabbed UI. |
| **Day 2: Hours 34–40** | Full Integration Smoke Testing | **Task 8** | End-to-end multi-laptop rehearsal passing all 5 failure/weather scenarios. |
| **Day 2: Hours 40–48** | Video Production & Submission | **Task 9** | 5-Minute high-impact demonstration video recorded, edited, and submitted. |

---

## 📋 Step-by-Step Task Checklist

---

### Task 1: Supabase Database Setup & Schema (with Local SQLite Fallback)

- **Owner:** Backend / DB Lead (Estimated time: 45 mins)
- **Priority:** Must Have (Critical Path)
- **Files Touched:** `backend/data/db.py`, `backend/data/store.py`, `backend/requirements.txt`, `backend/.env`

#### 1. Why This Step Exists & What It Does
Automatic Weather Stations generate time-series telemetry 24/7. When sensor anomalies or hardware failures occur, every incident must be audited with its confidence score, culprit sensor, and operator feedback. This task connects FastAPI to a cloud Supabase PostgreSQL database while guaranteeing a zero-crash local SQLite fallback (`sqlite+aiosqlite:///./skyguard.db`) if cloud internet is absent.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Connect the SkyGuard AI FastAPI backend to Supabase PostgreSQL using SQLAlchemy and asyncpg with automatic SQLite fallback:
1. Create `backend/data/db.py`:
   - Read DATABASE_URL from environment. If not provided or if connecting fails, seamlessly fall back to 'sqlite+aiosqlite:///./skyguard.db'.
   - Table `telemetry_records`:
       id (String/UUID PK), recorded_at (DateTime), station_id (String), temperature_c (Float), pressure_hpa (Float), humidity_pct (Float), dew_point_c (Float), wind_speed_ms (Float), solar_radiation_wm2 (Float), sequence (Integer), edge_status (String).
   - Table `anomaly_incidents`:
       incident_id (String PK), detected_at (DateTime), station_id (String), final_classification (String: 'Natural Weather Event', 'Sensor Defect', 'Compound Event', 'Uncertain Anomaly'), confidence_score (Float), model_a_weather_prob (Float), model_b_defect_prob (Float), culprit_sensor (String), shap_attributions (JSON/Text), text_justification (Text), imputed_value (Float, nullable), status (String), resolution_note (Text, nullable), resolved_at (DateTime, nullable).
   - Table `maintenance_predictions`:
       id (String PK), station_id (String), sensor_name (String), cumulative_drift (Float), health_status (String: 'Healthy', 'At Risk'), estimated_days_to_calibration (Integer), updated_at (DateTime).
   - Table `operator_feedback`:
       id (String PK), incident_id (String), label (String: 'false_alarm', 'confirmed_defect'), note (Text, nullable), created_at (DateTime).
   - Async function `init_db()` to automatically create tables if missing.
2. Update `backend/data/store.py` to persist incoming telemetry readings, anomaly incidents, and maintenance forecasts to `db.py` in non-blocking background tasks while preserving fast in-memory caching.
3. Update `backend/requirements.txt` to include: sqlalchemy>=2.0.0, asyncpg>=0.29.0, aiosqlite>=0.19.0, psycopg2-binary>=2.9.9.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Go to [supabase.com](https://supabase.com) and click **Sign Up** (free tier).
- [ ] Click **New Project**, name it `skyguard-db`, choose a password (e.g., `SkyGuard2026!`), and select nearest region.
- [ ] In Supabase $\to$ **Project Settings** $\to$ **Database** $\to$ **Connection String** $\to$ **URI**, copy the URL.
- [ ] Create `backend/.env` and paste:
  ```env
  DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
  ```
  *(Note: If you skip Supabase, SkyGuard automatically creates and uses `skyguard.db` locally!)*

#### 4. How to Test & Verify
- **Test Command (PowerShell / Terminal):**
  ```powershell
  cd backend
  python -c "import asyncio; from data.db import init_db; asyncio.run(init_db()); print('Database tables verified successfully!')"
  ```
- **Expected Result:** Output prints `Database tables verified successfully!`. In Supabase Table Editor (or local `skyguard.db`), verify `telemetry_records`, `anomaly_incidents`, `maintenance_predictions`, and `operator_feedback` exist.

---

### Task 2: Azure VM & Mosquitto MQTT Broker Provisioning

- **Owner:** Cloud / DevOps Lead (Estimated time: 45 mins)
- **Priority:** Must Have (Critical Path)
- **Files Touched:** `deploy/Dockerfile.backend`, `deploy/mosquitto.conf`, `docker-compose.yml`

#### 1. Why This Step Exists & What It Does
In a Split-Edge/Cloud architecture, remote weather stations communicate over lightweight MQTT messaging. This task sets up the cloud hub (or local Docker container) running Eclipse Mosquitto on port `1883` and the FastAPI backend on port `8000`.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Create the production deployment configuration for SkyGuard AI on an Azure Ubuntu VM:
1. `deploy/mosquitto.conf`:
   listener 1883 0.0.0.0
   allow_anonymous true
   persistence true
   persistence_location /mosquitto/data/
   log_dest stdout

2. `deploy/Dockerfile.backend`:
   - Base image: python:3.10-slim
   - Install build-essential and curl
   - Copy backend/ and install backend/requirements.txt
   - Expose port 8000
   - Command: uvicorn main:app --host 0.0.0.0 --port 8000

3. Update root `docker-compose.yml`:
   - Service `mosquitto`: image `eclipse-mosquitto:2`, ports ["1883:1883"], mounts ./deploy/mosquitto.conf
   - Service `backend`: builds deploy/Dockerfile.backend, ports ["8000:8000"], env_file: backend/.env, environment: [MQTT_BROKER_HOST=mosquitto, MQTT_ENABLED=true]
   - backend depends_on mosquitto
```

#### 3. Human Work (Portal Clicks & Copy-Pasting)
- [ ] In [portal.azure.com](https://portal.azure.com), create a Virtual Machine:
  - Name: `skyguard-vm` | Image: **Ubuntu 22.04 LTS** | Size: **Standard_B2s** (~$1/day from student credit).
  - Save `skyguard-vm_key.pem`.
- [ ] In VM **Networking** $\to$ **Inbound port rules**: allow destination ports `1883,8000,22`.
- [ ] Note down the VM's **Public IP Address** (e.g., `20.120.45.67`).
- [ ] Connect via SSH and run Docker Compose:
  ```powershell
  ssh -i "path\to\skyguard-vm_key.pem" azureuser@<VM_PUBLIC_IP>
  ```
  ```bash
  sudo apt-get update && sudo apt-get install -y docker.io docker-compose git
  git clone https://github.com/<your-username>/SkyGuard_SIH.git && cd SkyGuard_SIH
  sudo docker-compose up -d --build
  ```

#### 4. How to Test & Verify
- **Test Command:** Open `http://<VM_PUBLIC_IP>:8000/health` in your browser.
- **Expected Result:** JSON response returns:
  ```json
  { "status": "healthy", "service": "SkyGuard AI - AWS Anomaly Detection Engine", "mqtt_enabled": true }
  ```

---

### Task 3: Comprehensive Synthetic Weather & Fault Dataset Generator

- **Owner:** Data Science Lead (Estimated time: 45 mins)
- **Priority:** Must Have (ML Data Foundation)
- **Files Touched:** `scripts/generate_dataset.py`, `data/train_baseline_normal.csv`, `data/test_fault_injections.csv`

#### 1. Why This Step Exists & What It Does
Real-world Automatic Weather Stations rarely fail in front of loggers, meaning labeled multi-sensor failure datasets are virtually non-existent in meteorology. To train **Model A (Weather Classifier)** and **Model B (Sensor Defect Classifier)** without real defect logs, we mathematically inject the 5 canonical sensor fault archetypes (frozen flatline, impulse spike, noise burst, capacitive drift, packet dropout) into realistic Indian meteorological baseline data (modeled on IMD Agra climatology).

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Update `scripts/generate_dataset.py` to produce comprehensive training and evaluation datasets for Dual-Model Confluence:
1. Normal Weather Generator (train_baseline_normal.csv):
   - Station: AGRA-01 (Agra agro-meteorological zone).
   - Generates 15,000 timesteps at 10-minute cadence.
   - Realistic diurnal cycles: Temperature (22°C night to 38°C afternoon peak at 14:00).
   - Thermodynamic Relative Humidity inversely coupled: 40% (afternoon) to 85% (morning).
   - Semi-diurnal barometric pressure oscillations: 1002 to 1008 hPa.
   - Physically consistent dew point Td <= T + 0.5°C using Magnus-Tetens formula.
   - Physical derivatives: dT_dt, dP_dt, dRH_dt.
2. Multi-Class Evaluation Dataset (test_fault_injections.csv):
   Includes labels for Model A (weather_class) and Model B (defect_class):
   - NOMINAL_DIURNAL (weather_class: 'nominal', defect_class: 'none')
   - SEVERE_THUNDERSTORM / SQUALL (weather_class: 'squall', defect_class: 'none': pressure plunge -12 hPa, humidity surge to 94%, temperature drop -8°C, high wind)
   - FROZEN_VALUE (weather_class: 'nominal', defect_class: 'frozen_value': RH invariant at 84.2% for 4 hours while T cycles)
   - CAPACITIVE_DRIFT (weather_class: 'nominal', defect_class: 'capacitive_drift': progressive +15% humidity bias over warm baseline)
   - IMPULSE_SPIKE (weather_class: 'nominal', defect_class: 'impulse_spike': sudden +8°C single-point jump)
   - NOISE_BURST (weather_class: 'nominal', defect_class: 'noise_burst': high-frequency Gaussian noise on single channel)
   - PACKET_DROPOUT (weather_class: 'nominal', defect_class: 'packet_dropout': missing/stale packets)
3. Outputs verification statistics: confirms T-RH negative correlation (r < -0.7) and prints row count per class.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Run the dataset generator script:
  ```powershell
  python scripts/generate_dataset.py
  ```
- [ ] Verify both `data/train_baseline_normal.csv` and `data/test_fault_injections.csv` are created inside `data/`.

#### 4. How to Test & Verify
- **Test Command (PowerShell / Terminal):**
  ```powershell
  python -c "import pandas as pd; df = pd.read_csv('data/test_fault_injections.csv'); print('Classes in Test Set:'); print(df['defect_class'].value_counts()); print(df['weather_class'].value_counts())"
  ```
- **Expected Result:** Output displays counts for all 5 defect classes (`frozen_value`, `capacitive_drift`, `impulse_spike`, `noise_burst`, `packet_dropout`) and weather classes (`nominal`, `squall`).

---

### Task 4: All-in-One Google Colab ML Training (Autoencoder + Model A + Model B)

- **Owner:** Machine Learning Lead (Estimated time: 60 mins)
- **Priority:** Must Have (Core ML Brain)
- **Files Touched:** `notebooks/02_train_autoencoder.ipynb`, `backend/ml_artifacts/*`

#### 1. Why This Step Exists & What It Does
Our system uses a **Split-Edge/Cloud ML Pipeline**:
1. A **1D-CNN Autoencoder** (or Quantized PyOD) that checks reconstruction error on the edge/cloud ($\tau = 0.042$).
2. **Model A (Weather Classifier)**: Predicts probability of natural weather storms $P(\text{Weather})$.
3. **Model B (Sensor Defect Classifier)**: Predicts probability of hardware failure $P(\text{Defect})$ and identifies the defect type.
This task creates a single, push-button Google Colab notebook that trains all three models in 2 minutes, exports lightweight ONNX and scikit-learn models to `backend/ml_artifacts/`, and saves publication-grade evaluation graphs for your presentation slides and video!

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Create `notebooks/02_train_autoencoder.ipynb` as a unified all-in-one Google Colab training notebook for SkyGuard AI:
1. Load `data/train_baseline_normal.csv` and `data/test_fault_injections.csv`.
2. Model 1: 1D-CNN Autoencoder (Edge Outlier & Cloud Reconstruction Error):
   - Sliding window of 12 timesteps across 8 features (T, RH, P, Td, dT_dt, dP_dt, dRH_dt, drop_flag).
   - Fit RobustScaler and export normalization factors to `scaler.json`.
   - Compact architecture: Conv1D(16) -> Conv1D(8) -> Bottleneck(8) -> ConvTranspose1D(16) -> Output(8).
   - Train for 15 epochs with Adam optimizer.
   - Export to `backend/ml_artifacts/autoencoder.onnx` (< 200 KB).
3. Model 2: Model A (Weather Classifier):
   - Train LightGBM/RandomForest on 12-timestep statistical summary features to classify 'nominal' vs 'squall' vs 'heatwave'.
   - Outputs P(Weather) in [0.0, 1.0].
   - Export to `backend/ml_artifacts/model_a_weather.pkl`.
4. Model 3: Model B (Sensor Defect Classifier):
   - Train LightGBM/RandomForest on synthetic injected fault signatures to classify defect types ('none', 'frozen_value', 'capacitive_drift', 'impulse_spike', 'noise_burst', 'packet_dropout').
   - Outputs P(Defect) in [0.0, 1.0] and winning defect label.
   - Export to `backend/ml_artifacts/model_b_defect.pkl`.
5. Evaluation & Presentation Visuals:
   - Generate Plot 1: Loss & Validation Curve.
   - Generate Plot 2: Reconstruction Error Separation (showing Normal & Storm < 0.030, while Drift > 0.045).
   - Generate Plot 3: Confluence Confusion Matrix (Model A vs Model B accuracy > 94%).
   - Save all plots as PNGs in `backend/ml_artifacts/plots/`.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Open [colab.research.google.com](https://colab.research.google.com) $\to$ **Upload Notebook** $\to$ Select `notebooks/02_train_autoencoder.ipynb`.
- [ ] Click the left 📁 folder icon. Drag & drop `data/train_baseline_normal.csv` and `data/test_fault_injections.csv`.
- [ ] Click **Runtime** $\to$ **Run all** (runs in ~90 seconds).
- [ ] Download the generated folder/files and place them into `backend/ml_artifacts/`:
  - `autoencoder.onnx`
  - `model_a_weather.pkl`
  - `model_b_defect.pkl`
  - `scaler.json`
  - Evaluation plots (save for pitch deck and video!).

#### 4. How to Test & Verify
- **Test Command (PowerShell / Terminal):**
  ```powershell
  python -c "import os; p = 'backend/ml_artifacts'; assert os.path.exists(f'{p}/autoencoder.onnx'); assert os.path.exists(f'{p}/model_a_weather.pkl'); assert os.path.exists(f'{p}/model_b_defect.pkl'); assert os.path.exists(f'{p}/scaler.json'); print('ALL ML ARTIFACTS VERIFIED SUCCESSFULLY!')"
  ```
- **Expected Result:** Output displays `ALL ML ARTIFACTS VERIFIED SUCCESSFULLY!`.

---

### Task 5: Cloud Analytics Core: Confluence Decision Matrix, Maintenance & Imputation

- **Owner:** Backend Lead (Estimated time: 60 mins)
- **Priority:** Must Have (Full Documentation Alignment)
- **Files Touched:** `backend/services/confluence_engine.py`, `backend/services/predictive_maintenance.py`, `backend/services/imputation_engine.py`, `backend/services/anomaly_detector.py`, `backend/services/telemetry_ingestion.py`, `backend/models/schemas.py`

#### 1. Why This Step Exists & What It Does
This task implements the heart of the 2.0 Cloud Analytics Layer promised in PRD Section 1 & 5:
1. **Classification Confluence Engine**: Evaluates Model A ($P(\text{Weather})$) and Model B ($P(\text{Defect})$) through the deterministic Decision Matrix, assigning status: `Natural Weather Event`, `Sensor Defect`, `Compound Event`, or `Uncertain Anomaly` with an exact mathematical confidence score ($0-100\%$).
2. **Predictive Maintenance Engine (3.4)**: Tracks long-term EWMA drift to forecast sensor recalibration deadlines weeks in advance.
3. **Imputation & Correction Module (3.5)**: When a sensor defect is confirmed, reconstructs the corrupted parameter from healthy cross-correlated channels.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Implement the complete 2.0 Cloud Analytics Layer in the FastAPI backend:
1. Create `backend/services/confluence_engine.py`:
   - Loads `model_a_weather.pkl` and `model_b_defect.pkl` (with graceful heuristic fallback if models are loading).
   - Implements PRD Section 5.5 Decision Matrix:
     - P(Weather) >= 0.70 and P(Defect) < 0.30 -> "Natural Weather Event" (Severity: Nominal, Operator Alert: False)
     - P(Weather) < 0.30 and P(Defect) >= 0.70 -> "Sensor Defect" (Severity: High, Operator Alert: True)
     - P(Weather) >= 0.70 and P(Defect) >= 0.70 -> "Compound Event" (Severity: Warning, Operator Alert: True)
     - Otherwise -> "Uncertain Anomaly" (Severity: Moderate, Operator Alert: Triage)
   - Computes Confidence Score: max(P(Defect), P(Weather)) * (1.0 - abs(P(Defect) - P(Weather)) * 0.20)
2. Create `backend/services/predictive_maintenance.py`:
   - Fulfills Layer 3.4 (Objective 6): Maintains EWMA residual drift over time for Temperature, Humidity, and Pressure.
   - When cumulative drift breaches 2.0 sigma, transitions status to "At Risk".
   - Computes: estimated_days_to_calibration = max(1, int((tolerance - current_drift) / daily_drift_rate)).
3. Create `backend/services/imputation_engine.py`:
   - Fulfills Layer 3.5: When a sensor defect is confirmed, estimates the true value using healthy correlated parameters (e.g., estimating True RH from ambient Temperature and diurnal curve).
   - Returns: { "culprit": sensor_name, "reported_value": val, "suggested_imputed_value": corrected_val, "mae_confidence": 0.45 }
4. Update `backend/services/telemetry_ingestion.py`:
   - Every 1 Hz packet is evaluated through:
     1. IMD Rule Engine (Layer 1.1)
     2. 1D-CNN Reconstruction Error & SHAP (Layer 1.2 / 2.4)
     3. Dual-Model Confluence Engine (Layer 2.3)
     4. Predictive Maintenance Drift Tracker (Layer 3.4)
     5. Imputation Module if Defect Confirmed (Layer 3.5)
   - Attaches `confluence`, `maintenance`, and `imputation` payloads to the 1 Hz SSE stream and persists to `store.py` / `db.py`.
5. Update `backend/models/schemas.py` with the corresponding Pydantic models.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Pull latest code or rebuild Docker on Azure VM:
  ```bash
  sudo docker-compose up -d --build
  ```

#### 4. How to Test & Verify
- **Test Command (PowerShell / Terminal):**
  ```powershell
  python -c "from services.confluence_engine import confluence_engine; res = confluence_engine.evaluate_confluence(p_weather=0.05, p_defect=0.92, defect_type='capacitive_drift'); print('Confluence Output:', res)"
  ```
- **Expected Result:** Output displays:
  `Confluence Output: {'classification': 'Sensor Defect', 'confidence_score': 88.3, 'severity': 'High', 'operator_alert': True}`.

---

### Task 6: Laptop 1 Edge Weather Station Emulator (Ring Buffer & Chaos Keys)

- **Owner:** Edge / Hardware Lead (Estimated time: 45 mins)
- **Priority:** Must Have (Critical Path for Laptop 1)
- **Files Touched:** `backend/simulator/client.py`

#### 1. Why This Step Exists & What It Does
Laptop 1 represents the physical Automatic Weather Station `AGRA-01` in the field. It streams 1 Hz telemetry over MQTT to the cloud and maintains an internal **2-hour circular ring buffer**. The presenter presses keyboard keys live on camera (`1`, `2`, `3`, `4`, `0`) to inject physical faults and prove that the cloud AI correctly separates natural storms from sensor defects.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Update `backend/simulator/client.py` to act as the full ESP32 Edge Device Emulator for Laptop 1:
1. Connects to MQTT broker (--host on port 1883). Default topic: `skyguard/telemetry`.
2. Emulates Layer 1.1 IMD Plausibility and maintains an internal 2-hour circular ring buffer (120 samples).
3. Normal mode: Emits 1 Hz diurnal weather packets for station AGRA-01.
4. Interactive Chaos Keys (live terminal listeners):
   - Key '1': Heat Spike (+8°C jump in 10s) -> tests IMD step limit
   - Key '2': Capacitive Drift (+15% RH bias while temp remains warm) -> tests Model B Defect detection
   - Key '3': Severe Thunderstorm / Squall (-11 hPa drop, 94% RH, -8°C cool, wind +12 m/s) -> tests Model A True-Negative weather classification
   - Key '4': Frozen Sensor (RH flatlines at 84.2% indefinitely) -> tests Frozen Value detection
   - Key '0': Reset to Nominal Baseline
5. When an anomaly occurs, transmits an MQTT Incident Burst containing the trigger packet and the last 12 samples of context history.
6. Displays clean live terminal logging with colors showing Seq #, Temperature, Humidity, Pressure, and Active Fault Mode.
```

#### 3. Human Work (No Syntax Writing)
- [ ] On **Laptop 1**, ensure requirements are installed:
  ```powershell
  pip install paho-mqtt
  ```
- [ ] Run the transmitter pointing to your Azure VM (or local server IP):
  ```powershell
  python backend/simulator/client.py --host <VM_PUBLIC_IP>
  ```

#### 4. How to Test & Verify
- **Test Steps:**
  1. Watch Laptop 1's terminal: verify `[TX SEQ #...]` logs tick once every second.
  2. Press key `2` (Drift): terminal prints `>>> FAULT ACTIVE: CAPACITIVE DRIFT (+15% RH)`.
  3. Press key `3` (Storm): terminal prints `>>> SCENARIO ACTIVE: SEVERE THUNDERSTORM`.
  4. Press key `0`: terminal prints `>>> RESET TO BASELINE NORMAL`.

---

### Task 7: Laptop 2 Tabbed Operator Dashboard & 3D Digital Twin

- **Owner:** Frontend Lead (Estimated time: 60 mins)
- **Priority:** Must Have (Visual Showcase for Laptop 2)
- **Files Touched:** `frontend/src/app/page.tsx`, `frontend/src/lib/types.ts`, `frontend/src/components/panels/ConfluenceAlertBanner.tsx`, `frontend/src/components/panels/PredictiveMaintenancePanel.tsx`, `frontend/src/components/panels/ImputationPanel.tsx`

#### 1. Why This Step Exists & What It Does
Laptop 2 is the IMD Central Control Room screen. To prevent visual clutter and give the presentation a world-class polish, the inspector sidebar is structured into clean tabs:
- **Tab 1: Live ML & Confluence**: Real-time MSE sparkline + Confluence Decision Banner (`Sensor Defect | Confidence: 92.4%`).
- **Tab 2: Explainable AI (SHAP)**: Dynamic feature attribution bars and plain-English justification.
- **Tab 3: Sensor Health & Maintenance**: EWMA drift tracker and countdown: *"Pressure Sensor Calibration due in < 2 Weeks"*.
- **Tab 4: Imputation & Recovery**: Suggested corrected reading ($84.2\% \to 42.6\%\,\text{RH}$) with an interactive "Accept & Impute" button.
The 3D Digital Twin stays on the left and auto-zooms into the culprit sensor the moment an anomaly is confirmed!

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Update the Next.js frontend to implement the Tabbed Operator Dashboard:
1. Update `frontend/src/lib/types.ts` to include:
   - ConfluenceResult: { classification: string, confidence_score: number, severity: string, operator_alert: boolean, model_a_prob: number, model_b_prob: number }
   - MaintenanceResult: { sensor_name: string, cumulative_drift: number, health_status: 'Healthy' | 'At Risk', days_to_calibration: number }
   - ImputationResult: { culprit: string, reported_value: number, suggested_value: number, mae: number }
2. Create `frontend/src/components/panels/ConfluenceAlertBanner.tsx`:
   - Displays real-time classification banner with high-impact color badges:
     - "Natural Weather Event" -> Emerald Green ("Zero False Alarm - Natural Storm Recognized")
     - "Sensor Defect" -> Rose Red Pulse ("Hardware Defect Confirmed - Confidence: 92%")
     - "Compound Event" -> Amber Orange ("Extreme Weather + Sensor Stress")
   - Shows Model A P(Weather) and Model B P(Defect) mini gauges side-by-side.
3. Create `frontend/src/components/panels/PredictiveMaintenancePanel.tsx`:
   - Fulfills Layer 3.4: Visualizes cumulative EWMA drift bar, status badge ("Healthy" or "At Risk"), and estimated days to recalibration (< 2 Weeks).
4. Create `frontend/src/components/panels/ImputationPanel.tsx`:
   - Fulfills Layer 3.5: Shows Reported Corrupt Value vs Suggested Imputed Value.
   - Includes interactive "Accept & Impute" button that updates the local telemetry store.
5. In `frontend/src/app/page.tsx`:
   - Organize the right-hand panel into a sleek Tabbed Interface:
     [Live ML & Confluence] | [XAI (SHAP)] | [Maintenance] | [Imputation]
   - Ensure the 3D Digital Twin smoothly auto-zooms into the culprit sensor when Confluence fires a Sensor Defect alert.
```

#### 3. Human Work (No Syntax Writing)
- [ ] On **Laptop 2**, start the Next.js development server:
  ```powershell
  cd frontend
  npm run dev
  ```
- [ ] Open `http://localhost:3000` in Google Chrome and press `F11` for full screen.

#### 4. How to Test & Verify
- **Test Steps:**
  1. Open `http://localhost:3000`. Verify the 3D Digital Twin renders smoothly with spinning anemometer.
  2. Click through the 4 tabs: **Live ML & Confluence**, **XAI (SHAP)**, **Maintenance**, and **Imputation**.
  3. Verify all panels render with clean styling and zero React console errors.

---

### Task 8: End-to-End Two-Laptop Smoke Test & Verification Gate

- **Owner:** Entire Team (Estimated time: 30 mins)
- **Priority:** Must Have (Pre-Recording Gate)
- **Files Touched:** None (Testing only)

#### 1. Why This Step Exists & What It Does
Before recording the final submission video, this 30-minute rehearsal verifies that all scenarios work seamlessly across both laptops without a single bug or freeze.

#### 2. Test Execution Checklist

| Step | Action on Laptop 1 | Expected Output on Laptop 2 (Dashboard) | Status |
|---|---|---|---|
| **Step 1** | Run `client.py` in Normal Mode | 3D Twin is **Green**; Reconstruction MSE $\approx 0.015$; Confluence says "Nominal Baseline" | [ ] Pass |
| **Step 2** | Press key `3` (Severe Thunderstorm) | Pressure plunges (-11 hPa), humidity surges (94%); Model A reports $P(\text{Weather}) = 0.96$; Station stays **Green** (Zero False Alarm!) | [ ] Pass |
| **Step 3** | Press key `2` (Capacitive Drift) | MSE climbs live ($0.018 \to 0.048$); crosses threshold; Station turns **Red**; Camera auto-zooms to Humidity sensor shield! | [ ] Pass |
| **Step 4** | Check Tab 1 & Tab 2 | Banner displays `Sensor Defect (92.4% Confidence)`; SHAP bar identifies Humidity as 88% driver with plain-English justification | [ ] Pass |
| **Step 5** | Check Tab 3 (Maintenance) | Panel shows cumulative drift and warns: *"Calibration due in < 2 Weeks"* | [ ] Pass |
| **Step 6** | Check Tab 4 (Imputation) | Shows `Reported RH: 84.2% -> Suggested Imputed RH: 42.6%`; Click "Accept & Impute" | [ ] Pass |
| **Step 7** | Press key `0` (Reset Normal) | Station smoothly transitions back to **Green** overview | [ ] Pass |

---

### Task 9: Video Presentation Recording & Pitch Storyboard

- **Owner:** Entire Team (Estimated time: 60 mins)
- **Priority:** Must Have (Final Hackathon Deliverable)
- **Deliverable:** 3 to 5-Minute Video File (`SkyGuard_AI_SIH_Showcase.mp4`)

#### 1. Recording Setup
- Place **Laptop 1** (Terminal Edge Simulator) and **Laptop 2** (3D Digital Twin + Tabbed Inspector) side-by-side on a desk, or use OBS Studio to capture both screens simultaneously.

#### 2. Timed 5-Minute Pitch Script

```
[0:00 - 0:45] INTRODUCTION & SPLIT-EDGE/CLOUD ARCHITECTURE
- Show both laptops side-by-side.
- "Welcome to SkyGuard AI. On Laptop 1, we emulate an on-site Automatic Weather Station (AGRA-01)
   running edge boundary rules and context ring buffering. On our cloud Azure VM, our dual-model
   confluence engine evaluates anomalies in real time. On Laptop 2, our IMD control room monitors
   the live digital twin."

[0:45 - 1:45] TEST 1: TRUE NEGATIVE STORM (ZERO FALSE ALARMS)
- Presenter presses [3] on Laptop 1.
- "Watch the live telemetry: pressure plunges by 11 hPa and humidity surges to 94%. In traditional
   systems, static threshold rules fire false alarms during storms. But watch Laptop 2: our station
   remains GREEN! Model A recognizes natural squall line physics with 96% confidence. Zero false alarms!"

[1:45 - 3:00] TEST 2: SILENT CAPACITIVE DRIFT & CONFLUENCE TRIAGE
- Presenter presses [2] on Laptop 1 to inject subtle +15% capacitive drift.
- "Now we inject silent capacitive drift—the hardest failure to catch. Watch the MSE waveform climb:
   0.021... 0.035... 0.048! It crosses our operational threshold!"
- "Immediately, the 3D twin flashes RED and the camera auto-focuses onto the humidity sensor shield!
   The Confluence Banner confirms: Sensor Defect with 92.4% Confidence!"

[3:00 - 3:45] EXPLAINABLE AI & ACTIVE RECOVERY (TABS 2, 3, 4)
- Click Tab 2 (SHAP): "Our Explainable AI Hub breaks down the exact feature contributions: 88% humidity."
- Click Tab 3 (Maintenance): "Our predictive maintenance engine tracks long-term EWMA drift, warning us
   two weeks before complete sensor breakdown."
- Click Tab 4 (Imputation): "And our imputation module immediately reconstructs the corrupted data
   from healthy correlated channels: 84.2% is corrected to 42.6%. We click Accept, keeping the meteorological record unbroken."

[3:45 - 4:30] DATA SCIENCE DEPTH (GOOGLE COLAB)
- Switch briefly to Google Colab: show 1D-CNN loss curves, Model A/B evaluation confusion matrix,
   and correlation heatmaps proving >94% precision.

[4:30 - 5:00] CONCLUSION & IMPACT
- "SkyGuard AI: Moving India's weather network from blind thresholds to real-time explainable intelligence."
```

---

## 🛡️ Zero-Cost Guardrails & Emergency Local Fallback

| Component | Cloud Setup | Emergency Local Fallback (If Cloud Fails) |
|---|---|---|
| **Broker** | Azure VM Mosquitto (`<VM_IP>:1883`) | Local Docker Mosquitto (`localhost:1883`) |
| **Backend** | Azure VM Docker (`<VM_IP>:8000`) | Local Terminal: `cd backend; python main.py` |
| **Database** | Supabase Cloud PostgreSQL | Local SQLite (`skyguard.db`) created automatically! |
| **Frontend** | Laptop 2 (`localhost:3000`) | Local Terminal: `cd frontend; npm run dev` |

> [!IMPORTANT]
> **Total Out-of-Pocket Cost: $0.00.** If cloud WiFi or Azure VM is ever unavailable during recording, simply run the system locally on Laptop 2 in 10 seconds. It works 100% offline!
