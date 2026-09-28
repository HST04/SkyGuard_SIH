# SkyGuard AI — Team Task List (TASKS.md)

> **Sprint Objective:** Build and verify a two-laptop Split-Edge/Cloud system for Automatic Weather Stations (AWS) operating at 1 Hz.  
> **Repository:** `SkyGuard_SIH`  
> **Team Members:** Hanswarup, Yukti, Araz, Mudit, Harsh, Shreyansh.

---

## 1. Project Context & System Architecture

### What the Project Does
Automatic Weather Stations (AWS) in India monitor meteorological conditions across remote areas. Current systems rely on static thresholds (e.g., alert if relative humidity > 95%), which causes two major problems:
1. **False Alarms During Storms:** Severe weather causes rapid pressure drops and humidity spikes, triggering false alarms even though sensors are functioning normally.
2. **Undetected Sensor Drift:** Over time, sensors degrade (e.g., capacitive drift adding +15% humidity bias). Static thresholds miss this because readings remain within broad plausible limits, corrupting downstream weather models.
3. **Bandwidth Limitations:** Remote stations have limited network access. Continuous 24/7 raw streaming is inefficient.

### The System Design
- **Laptop 1 (On-Site Station):** Simulates weather station `AGRA-01`. Runs boundary checks, maintains a 2-hour circular ring buffer in memory, and transmits data over MQTT. When an anomaly occurs, it sends an incident burst with 2 hours of pre-anomaly context.
- **Cloud Backend:** 
  - Analyzes physical rates of change and thermodynamic coupling ($T \leftrightarrow P \leftrightarrow RH$).
  - Evaluates data using two supervised models: Model A (identifies natural storms) and Model B (identifies sensor defects).
  - Uses a deterministic Confluence Decision Matrix to classify the event and assign a confidence score (0–100%).
  - Tracks long-term sensor drift (predictive maintenance) and calculates corrected values for faulty sensors (imputation).
  - Stores records in Supabase PostgreSQL (with automatic local SQLite fallback) and streams updates over SSE at 1 Hz.
- **Laptop 2 (Control Room):** Displays a 4-tab web dashboard and an interactive 3D digital twin that targets culprit sensors during defects.

---

## 2. Task Allocation & Work Breakdown

Work is distributed across all 6 members with dedicated git branches. Hanswarup handles pull requests and branch merges in addition to his backend components.

| Member | Branch | Assigned Scope | Key Files |
|---|---|---|---|
| **Hanswarup** | `feat/hanswarup` | Pull requests & merge conflict resolution, Docker deployment, Multi-Scale Analyzer service, End-to-End integration test | `deploy/*`, `docker-compose.yml`, `backend/services/multi_scale_analyzer.py`, `backend/tests/test_e2e_pipeline.py` |
| **Yukti** | `feat/yukti` | Unified Google Colab training notebook, training Autoencoder, Model A, and Model B, exporting weights and evaluation plots | `notebooks/02_train_autoencoder.ipynb`, `backend/ml_artifacts/*` |
| **Araz** | `feat/araz` | Dataset generation quality check, Laptop 1 edge transmitter script (5 chaos modes, 2-hr ring buffer, context burst), edge tests | `scripts/generate_dataset.py`, `data/*.csv`, `backend/simulator/client.py`, `backend/tests/test_mqtt_stage6.py` |
| **Mudit** | `feat/mudit` | Database schema & async persistence (Supabase + SQLite fallback), Confluence Decision Matrix service | `backend/data/db.py`, `backend/data/store.py`, `backend/services/confluence_engine.py` |
| **Harsh** | `feat/harsh` | Predictive maintenance drift tracker, imputation service, telemetry ingestion pipeline orchestration, schema updates | `backend/services/predictive_maintenance.py`, `backend/services/imputation_engine.py`, `backend/services/telemetry_ingestion.py`, `backend/models/schemas.py` |
| **Shreyansh** | `feat/shreyansh` | Frontend data contracts, 4-tab dashboard refactor, Confluence alert banner, Maintenance panel, Imputation panel, 3D auto-zoom | `frontend/src/app/page.tsx`, `frontend/src/components/panels/*`, `frontend/src/lib/types.ts`, `frontend/src/stores/telemetryStore.ts` |

---

## 3. Team Coordination & Technical Handoffs

To avoid integration issues, members hand off components according to these contracts:

1. **Araz ➔ Yukti (Datasets):**  
   - Files: `data/train_baseline_normal.csv` (15,000 rows) and `data/test_fault_injections.csv` (4,000 rows).
   - Columns: `timestamp, station_id, temperature_c, humidity_pct, pressure_hpa, dew_point_c, wind_speed_ms, wind_dir_deg, solar_radiation_wm2, dT_dt, dP_dt, dRH_dt, drop_flag, weather_class, defect_class`.
   - Handoff: Araz confirms row counts and class labels; Yukti uploads the files to Colab.

2. **Yukti ➔ Hanswarup, Mudit, Harsh (Model Files):**  
   - Location: `backend/ml_artifacts/`
   - Files: `autoencoder.onnx`, `scaler.json`, `model_a_weather.pkl`, `model_b_defect.pkl`.
   - Handoff: Hanswarup ensures container dependencies support these models; Mudit and Harsh load them in `confluence_engine.py` and `anomaly_detector.py`.

3. **Hanswarup ➔ Mudit, Harsh (Physical Feature Analyzer):**  
   - File: `backend/services/multi_scale_analyzer.py`
   - Output: Object containing derivatives ($dT/dt, dP/dt, dRH/dt$), correlation ($\rho_{T,RH}$), and decoupling flag.
   - Handoff: Mudit uses these features in confluence logic; Harsh passes incoming windows through the analyzer in `telemetry_ingestion.py`.

4. **Harsh ➔ Shreyansh (SSE Telemetry Stream):**  
   - Endpoint: `GET /api/v1/telemetry/stream` (1 Hz EventSource)
   - Payload: Object containing `telemetry`, `confluence`, `maintenance`, and `imputation`.
   - Handoff: Shreyansh binds these exact keys to the TypeScript types in `frontend/src/lib/types.ts`.

5. **Hanswarup ➔ Araz (MQTT Broker):**  
   - Host & Port: Port `1883`, topic `skyguard/telemetry`.
   - Handoff: Hanswarup verifies Mosquitto is active; Araz runs `client.py` to publish packets.

6. **All Members ➔ Hanswarup (Pull Requests):**  
   - Process: Members push commits to their feature branch and open a PR into `main`.
   - Handoff: Hanswarup reviews changes, resolves conflicts, verifies tests, and merges.

---

## 4. Member Task Details

---

### HANSWARUP

#### Why this task is needed:
1. The backend needs to run reliably in containerized environments (Docker / Azure VM) with Mosquitto on port 1883 and FastAPI on port 8000.
2. Raw telemetry values do not indicate whether atmospheric changes are physically coupled. PRD Layer 2.1 requires a Multi-Scale Analyzer to calculate temporal rates of change ($dT/dt, dP/dt, dRH/dt$) and the thermodynamic correlation coefficient between temperature and humidity ($\rho_{T,RH}$). A positive correlation during stable pressure indicates physical sensor decoupling.
3. Code from 5 teammates must be integrated cleanly without breaking the central pipeline.

#### Tasks:
- [ ] **Task 1.1: Pull Request & Merge Management**
  - Review incoming PRs from `feat/yukti`, `feat/araz`, `feat/mudit`, `feat/harsh`, `feat/shreyansh`.
  - Resolve file conflicts in shared configuration files (`requirements.txt`, `schemas.py`).
  - Run `python backend/tests/test_engine.py` before and after merging into `main`.

- [ ] **Task 1.2: Docker & Cloud Deployment Configuration**
  - Create `deploy/mosquitto.conf` (port 1883, anonymous access, persistence).
  - Create `deploy/Dockerfile.backend` (Python 3.11-slim, system build dependencies, pip install, uvicorn on port 8000).
  - Update root `docker-compose.yml` to define both `mosquitto` and `backend` services.
  - Verify container startup:
    ```powershell
    docker compose up -d --build
    curl http://localhost:8000/health
    ```

- [ ] **Task 1.3: Multi-Scale Multivariate Analyzer (Layer 2.1)**
  - Create `backend/services/multi_scale_analyzer.py`:
    - Computes numerical derivatives over sliding windows: $dT/dt, dP/dt, dRH/dt, d^2P/dt^2$.
    - Computes correlation $\rho_{T,RH} = \text{corr}(T, RH)$.
    - Computes decoupling flag: `rho_T_RH > 0.0 and abs(dP_dt) < 2.0`.
    - Returns feature dictionary for Model A and Model B.
  - Verification:
    ```powershell
    python -c "from services.multi_scale_analyzer import multi_scale_analyzer; print('Analyzer ready')"
    ```

- [ ] **Task 1.4: End-to-End System Test**
  - Create `backend/tests/test_e2e_pipeline.py` verifying packet flow from ingestion ➔ multi-scale analyzer ➔ confluence engine ➔ maintenance ➔ DB write.

---

### YUKTI

#### Why this task is needed:
1. Static threshold rules cannot reliably differentiate natural storm dynamics from hardware failures.
2. The project requires three specific models:
   - **1D-CNN Autoencoder:** Learns multi-sensor normal baselines; high reconstruction error ($> 0.042$) flags an anomaly.
   - **Model A (Weather Classifier):** Learns multi-channel storm signatures (pressure plunge, cooling, humidity surge) to identify valid weather events ($P(\text{Weather})$).
   - **Model B (Sensor Defect Classifier):** Trained on injected fault patterns (flatlines, drift, impulse spikes, noise bursts, dropouts) to identify defect types ($P(\text{Defect})$).
3. Evaluators need visual evaluation plots (loss curves, error separation, confusion matrix) to assess model performance.

#### Tasks:
- [ ] **Task 2.1: Unified Google Colab Training Notebook**
  - Create `notebooks/02_train_autoencoder.ipynb`:
    - Ingest `data/train_baseline_normal.csv` and `data/test_fault_injections.csv`.
    - Model 1: Train 1D-CNN Autoencoder on 12-timestep windows (8 features). Export to `backend/ml_artifacts/autoencoder.onnx` (< 200 KB) and `scaler.json`.
    - Model 2: Train Model A (LightGBM/RandomForest) to classify `nominal` vs `squall`. Export to `backend/ml_artifacts/model_a_weather.pkl`.
    - Model 3: Train Model B (LightGBM/RandomForest) on injected defect patterns (`none`, `frozen_value`, `capacitive_drift`, `impulse_spike`, `noise_burst`, `packet_dropout`). Export to `backend/ml_artifacts/model_b_defect.pkl`.
    - Generate 3 plots: Loss curve, reconstruction error separation, and confluence confusion matrix. Save to `backend/ml_artifacts/plots/`.

- [ ] **Task 2.2: Colab Execution & Model Artifact Export**
  - Run notebook in Google Colab.
  - Download outputs and place them in `backend/ml_artifacts/`.
  - Verification:
    ```powershell
    python -c "import os; p='backend/ml_artifacts'; assert os.path.exists(f'{p}/autoencoder.onnx'); assert os.path.exists(f'{p}/model_a_weather.pkl'); assert os.path.exists(f'{p}/model_b_defect.pkl'); assert os.path.exists(f'{p}/scaler.json'); print('Models verified')"
    ```

---

### ARAZ

#### Why this task is needed:
1. Labeled sensor failure datasets from field stations do not exist in standard meteorological archives. The dataset generator creates clean Indian baseline weather (Agra AWS) and injects the 5 failure modes to train and test the models.
2. For the live demonstration, **Laptop 1 acts as the physical weather station**. Araz provides the emulator script with live keyboard triggers to demonstrate how the system reacts in real time to both natural storms and sensor defects.
3. The emulator implements a 2-hour circular ring buffer in memory and sends incident bursts on anomalies, demonstrating network bandwidth savings.

#### Tasks:
- [ ] **Task 3.1: Dataset Quality Check & Handoff**
  - Run `python scripts/generate_dataset.py` to ensure `train_baseline_normal.csv` (15,000 rows) and `test_fault_injections.csv` (4,000 rows) are generated.
  - Run verification check:
    ```powershell
    python -c "import pandas as pd; df = pd.read_csv('data/test_fault_injections.csv'); print(df['defect_class'].value_counts()); print(df['weather_class'].value_counts())"
    ```
  - Confirm files are ready for Yukti.

- [ ] **Task 3.2: Laptop 1 Edge Weather Station Emulator**
  - Update `backend/simulator/client.py`:
    - Connects to MQTT broker (`--host`, port 1883, topic `skyguard/telemetry`).
    - Evaluates Layer 1.1 IMD boundary checks locally.
    - Maintains a 2-hour circular ring buffer (120 samples at 1 Hz).
    - Terminal Chaos Keys:
      - `1`: Heat Spike (+8°C jump in 10s)
      - `2`: Capacitive Drift (+15% RH bias over warm baseline)
      - `3`: Severe Thunderstorm (-11 hPa drop, 94% RH, -8°C cool, wind +12 m/s)
      - `4`: Frozen Sensor (RH flatlines at 84.2%)
      - `0`: Reset to Nominal Baseline
    - On anomaly, publishes an MQTT Incident Burst (trigger packet + past 12 samples of context).
    - Displays clean color-coded status line in the terminal.
  - Verification:
    ```powershell
    python backend/tests/test_mqtt_stage6.py
    ```

---

### MUDIT

#### Why this task is needed:
1. Telemetry and anomaly events must be stored for historical record-keeping. The system needs to support cloud Supabase PostgreSQL while guaranteeing a local SQLite fallback (`skyguard.db`) so the application continues running even without internet access.
2. The system requires a deterministic decision mechanism rather than arbitrary thresholds. Mudit implements the Confluence Decision Matrix (PRD Section 5.5) which reconciles Model A ($P(\text{Weather})$) and Model B ($P(\text{Defect})$) into a clear classification with a mathematical confidence score.

#### Tasks:
- [ ] **Task 4.1: Database Layer (Supabase PostgreSQL + SQLite Fallback)**
  - Create `backend/data/db.py`:
    - Connects using `DATABASE_URL` from `.env`, falls back to `sqlite+aiosqlite:///./skyguard.db`.
    - Tables: `telemetry_records`, `anomaly_incidents`, `maintenance_predictions`, `operator_feedback`.
    - Function `init_db()` to auto-create tables if missing.
  - Update `backend/data/store.py` to persist incoming readings and incidents asynchronously without blocking memory operations.
  - Verification:
    ```powershell
    python -c "import asyncio; from data.db import init_db; asyncio.run(init_db()); print('DB verified')"
    ```

- [ ] **Task 4.2: Classification Confluence Decision Matrix Engine (Layer 2.3)**
  - Create `backend/services/confluence_engine.py`:
    - Loads `model_a_weather.pkl` and `model_b_defect.pkl` from `backend/ml_artifacts/`.
    - Decision Matrix Rules:
      - $P(\text{Weather}) \ge 0.70$ and $P(\text{Defect}) < 0.30 \implies$ `Natural Weather Event` (no operator alarm)
      - $P(\text{Weather}) < 0.30$ and $P(\text{Defect}) \ge 0.70 \implies$ `Sensor Defect` (operator alarm)
      - $P(\text{Weather}) \ge 0.70$ and $P(\text{Defect}) \ge 0.70 \implies$ `Compound Event` (warning)
      - Otherwise $\implies$ `Uncertain Anomaly` (triage)
    - Confidence formula: $\max(P_D, P_W) \times (1.0 - |P_D - P_W| \times 0.20)$
  - Verification:
    ```powershell
    python -c "from services.confluence_engine import confluence_engine; print(confluence_engine.evaluate_confluence(0.05, 0.94, 'capacitive_drift'))"
    ```

---

### HARSH

#### Why this task is needed:
1. Detecting failures only after they happen causes gaps in weather records. The Predictive Maintenance Engine (PRD Section 3.4) tracks cumulative sensor drift using an Exponentially Weighted Moving Average (EWMA), alerting operators weeks before complete failure.
2. When a sensor fails, downstream numerical weather prediction models need substitute values. The Imputation Module (PRD Section 3.5) reconstructs the faulty channel from healthy correlated channels.
3. All backend processing stages must execute in a consistent order on each 1-second packet and be broadcast over SSE to the frontend.

#### Tasks:
- [ ] **Task 5.1: Predictive Maintenance Engine (Layer 3.4)**
  - Create `backend/services/predictive_maintenance.py`:
    - Tracks daily EWMA residual drift ($\lambda = 0.2$) for Temperature, Humidity, and Pressure.
    - Warning threshold at $2.0\sigma \implies$ flags status as "At Risk".
    - Estimates days to recalibration: $\max(1, \lfloor(\text{tolerance} - \text{drift}) / \text{drift\_rate}\rfloor)$.

- [ ] **Task 5.2: Imputation & Correction Module (Layer 3.5)**
  - Create `backend/services/imputation_engine.py`:
    - When Confluence confirms a `Sensor Defect`, estimates true value from surviving healthy channels.
    - Returns `{ "culprit": sensor_name, "reported_value": val, "suggested_value": corrected_val, "mae": 0.45 }`.

- [ ] **Task 5.3: Pipeline Ingestion Orchestration & Schemas**
  - Update `backend/models/schemas.py` with `ConfluenceResult`, `MaintenanceResult`, `ImputationResult`.
  - Update `backend/services/telemetry_ingestion.py` to route incoming packets sequentially through:
    1. IMD Physics Rule Check
    2. Multi-Scale Analyzer
    3. Autoencoder Reconstruction Error & SHAP
    4. Confluence Decision Engine
    5. Predictive Maintenance Drift Tracker
    6. Imputation Module (if defect confirmed)
  - Broadcast full payload over SSE and persist to store.
  - Verification:
    ```powershell
    python backend/tests/test_engine.py
    ```

---

### SHREYANSH

#### Why this task is needed:
1. Laptop 2 serves as the IMD Central Control Room screen during the presentation. An unorganized interface makes it difficult for evaluators to see the system's capabilities.
2. Organizing the inspection area into 4 distinct tabs provides a structured view:
   - Tab 1: Live ML & Confluence Decision
   - Tab 2: Explainable AI (SHAP attributions & diagnostic message)
   - Tab 3: Sensor Health & Calibration Horizon
   - Tab 4: Imputation & Data Recovery ("Accept & Impute" button)
3. The 3D Digital Twin must auto-focus on the faulty sensor shield when a defect is detected to provide visual clarity.

#### Tasks:
- [x] **Task 6.1: Frontend Data Contracts & Store**
  - Update `frontend/src/lib/types.ts` to add interfaces for `ConfluenceResult`, `MaintenanceResult`, `ImputationResult`.
  - Update `frontend/src/stores/telemetryStore.ts` to store these fields from incoming SSE messages.

- [x] **Task 6.2: Tabbed Dashboard Panels & Refactor**
  - Create `frontend/src/components/panels/ConfluenceAlertBanner.tsx`:
    - Badges: `Natural Weather Event` (Emerald Green), `Sensor Defect` (Rose Red pulse), `Compound Event` (Amber Orange).
    - Gauges for Model A $P(\text{Weather})$ and Model B $P(\text{Defect})$.
  - Create `frontend/src/components/panels/PredictiveMaintenancePanel.tsx`:
    - Visualizes EWMA drift bar, status badge ("Healthy" / "At Risk"), and days-to-calibration countdown.
  - Create `frontend/src/components/panels/ImputationPanel.tsx`:
    - Shows reported corrupt value vs suggested imputed value, with an interactive "Accept & Impute" button.
  - Refactor `frontend/src/app/page.tsx` into 4 tabs:
    `[Live ML & Confluence] | [Explainable AI (SHAP)] | [Maintenance] | [Data Repair]`
  - Ensure 3D camera smoothly auto-zooms to the culprit sensor on anomaly.
  - Verification:
    ```powershell
    cd frontend; npm run dev
    ```
    Open `http://localhost:3000` and verify tabs and 3D camera targeting.

---

## 5. Team Rehearsal & Verification Matrix

Run this test sequence across both laptops before recording the showcase video:

| Step | Action on Laptop 1 (Araz) | Expected on Laptop 2 (Shreyansh) | Verification |
|---|---|---|---|
| **1** | Run `client.py` Normal Mode (`0`) | 3D Twin is **Green**; MSE $\approx 0.015$; Confluence says "Nominal Baseline" | [ ] Pass |
| **2** | Press key `3` (Severe Thunderstorm) | Pressure plunges (-11 hPa), humidity surges (94%); Model A reports $P(\text{Weather}) = 0.96$; Station stays **Green** (Zero False Alarm) | [ ] Pass |
| **3** | Press key `2` (Capacitive Drift) | MSE climbs ($0.018 \to 0.048$); Station turns **Red**; Camera auto-zooms to Humidity sensor | [ ] Pass |
| **4** | Check Tab 1 & Tab 2 | Banner displays `Sensor Defect (92.4% Confidence)`; SHAP bar highlights Humidity (88%) | [ ] Pass |
| **5** | Check Tab 3 (Maintenance) | Panel shows cumulative drift: *"Calibration due in < 2 Weeks"* | [ ] Pass |
| **6** | Check Tab 4 (Imputation) | Shows `Reported: 84.2% -> Suggested: 42.6%`; Click "Accept & Impute" button | [ ] Pass |
| **7** | Press key `0` (Reset Normal) | Station smoothly returns to **Green** overview | [ ] Pass |

---

## 6. Showcase Recording Plan (5-Minute Dual-Screen Video)

- `[0:00 - 0:45]` System introduction and split-edge/cloud architecture overview.
- `[0:45 - 1:45]` Thunderstorm test: key `3` on Laptop 1 shows station staying green with zero false alarms.
- `[1:45 - 3:00]` Capacitive drift test: key `2` on Laptop 1 triggers red alert, camera zooms to sensor, confluence confirms defect.
- `[3:00 - 3:45]` Tabs 2, 3, and 4: Explainable AI SHAP breakdown, predictive maintenance drift horizon, and live imputation.
- `[3:45 - 4:30]` Google Colab: Model A/B evaluation curves and confusion matrix.
- `[4:30 - 5:00]` Summary of operational impact.
