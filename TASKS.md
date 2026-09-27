# 🚀 SkyGuard AI — 5-Day Master Execution Checklist (TASKS.md)

> **Sprint Objective:** Build, test, and record a **two-laptop edge-to-cloud demonstration** showing a **Split-Edge/Cloud Machine Learning pipeline operating LIVE in real time** at 1 Hz.  
>
> **The Real-Time ML Experience:**
> 1. **Laptop 1 (Hardware AWS Station / Edge Node):** Emulates on-site weather station `AGRA-01` running an ESP32 architecture profile: Layer 1.1 IMD Plausibility filter and Layer 1.2 Quantized PyOD/TFLite Micro outlier detection, buffering normal data locally and transmitting incident bursts with a pre-anomaly context window over MQTT to the cloud.
> 2. **Cloud (Azure VM + Supabase):** Real-time evaluations conducted by the **2.0 Cloud Analytics Layer**: Multi-Scale Multivariate Analyzer feeds **Model A (Weather Classifier)** and **Model B (Sensor Defect Classifier, trained on synthetic fault injections)** into the **Classification Confluence Decision Matrix**, calculating exact confidence scores, live SHAP attributions, Predictive Maintenance horizons, and Imputed parameter values.
> 3. **Laptop 2 (IMD Control Room):** Displays the **Live ML Pipeline Monitor** in real time — active waveform metrics, dynamic SHAP attribution bars, Sensor Health recalibration forecast, suggested imputed parameters, and an interactive 3D Digital Twin that auto-zooms into the culprit sensor the instant a defect is confirmed.
> 4. **Google Colab:** Dedicated environment for training Model A on weather phenomena, injecting synthetic defects to train Model B, exporting weights, and producing benchmark curves for evaluation.
>
> **Team Rules:** 6 team members. **Zero human syntax writing.** Humans copy-paste AI prompts, set up accounts, review outputs, click cloud buttons, and run test commands.

---

## 📌 Live Real-Time Split-Edge/Cloud Architecture

```
  ┌─────────────────────────┐               ┌─────────────────────────────────────────┐
  │        LAPTOP 1         │               │                LAPTOP 2                 │
  │ "On-Site Hardware AWS"  │               │        "IMD Central Control Room"       │
  │                         │               │                                         │
  │  Python Edge Simulator  │               │  Next.js Dashboard & 3D Digital Twin   │
  │  - 1 Hz Telemetry       │               │  ┌───────────────────────────────────┐  │
  │  - Keyboard Chaos Keys: │               │  │ LIVE ML PIPELINE MONITOR (1 Hz)   │  │
  │    [1] Heat Spike       │               │  │ - Real-Time MSE Error Waveform    │  │
  │    [2] Capacitive Drift │               │  │ - Threshold Line (tau = 0.042)    │  │
  │    [3] Squall Line      │               │  │ - Live SHAP Attribution Bars      │  │
  │    [0] Reset Normal     │               │  │ - Inference Latency: ~2.4 ms      │  │
  └────────────┬────────────┘               │  └───────────────────────────────────┘  │
               │                            │  - 3D Twin Auto-Camera Lerp to Culprit  │
               │ MQTT (Port 1883)           └────────────────────▲────────────────────┘
               ▼                                                 │
  ┌──────────────────────────────────────────────────────────────┴────────────────────┐
  │                        AZURE VIRTUAL MACHINE (CLOUD CORE)                         │
  │                                                                                   │
  │   ┌─────────────────────┐            ┌────────────────────────────────────────┐   │
  │   │  Mosquitto Broker   │───────────▶│         FastAPI Engine Core            │   │
  │   │     (Port 1883)     │            │                                        │   │
  │   └─────────────────────┘            │  1. Multi-Scale Analyzer (Short/Long)  │   │
  │                                      │  2. Dual Models (A: Weather, B: Defect)│   │
  │                                      │  3. Confluence & Confidence Scoring    │   │
  │                                      │  4. Live SHAP Attribution (XAI Hub)    │   │
  │                                      │  5. Predictive Maintenance & Imputation│   │
  │                                      │  6. SSE Broadcaster (1 Hz ML Feed)     │   │
  │                                      └───────────────────┬────────────────────┘   │
  └──────────────────────────────────────────────────────────┼────────────────────────┘
                                                             │
                                                             ▼ SQL (TLS)
                                                ┌─────────────────────────┐
                                                │   SUPABASE POSTGRESQL   │
                                                │  - telemetry_records    │
                                                │  - anomaly_events       │
                                                │  - operator_feedback   │
                                                └─────────────────────────┘
```

---

## 📅 5-Day Master Roadmap

| Day | Focus | Target Tasks | Unlocked Deliverable |
|---|---|---|---|
| **Day 1** | Cloud & DB Foundation | Task 1 & Task 2 | Supabase PostgreSQL active; Azure VM running Mosquitto + FastAPI. |
| **Day 2** | Data Engineering & ML Training | Task 3 & Task 4 | High-fidelity dataset generated; 1D-CNN trained in Colab & exported to ONNX. |
| **Day 3** | Live Ingestion & Edge Hardware | Task 5 & Task 6 | Real-time ONNX inference in backend; Laptop 1 streaming over MQTT. |
| **Day 4** | Real-Time UI & System Smoke Test | Task 7 & Task 8 | Laptop 2 showing live MSE waveform; 100% end-to-end integration verified. |
| **Day 5** | Rehearsal & Video Production | Task 9 | 5-Minute presentation video recorded, edited, and submitted. |

---

## 📋 Step-by-Step Task Checklist

---

### Task 1: Supabase Database Setup & Schema

- **Owner:** Any Team Member (Estimated time: 45 mins)
- **Priority:** Must Have (Critical Path)
- **Files Touched:** `backend/data/db.py`, `backend/data/store.py`, `backend/requirements.txt`

#### 1. What to Build
Connect FastAPI to a free cloud Supabase PostgreSQL database to store telemetry history, detected anomalies with their reconstruction MSE, and operator feedback.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Connect the SkyGuard AI FastAPI backend to Supabase PostgreSQL using SQLAlchemy and asyncpg:
1. Create `backend/data/db.py`:
   - Connect using DATABASE_URL from environment (fallback to sqlite+aiosqlite:///./skyguard.db if not set).
   - Table `telemetry_records`: id (UUID), recorded_at (timestamp), station_id (str), temperature_c (float), pressure_hpa (float), humidity_pct (float), dew_point_c (float), wind_speed_ms (float), sequence (int).
   - Table `anomaly_events`: anomaly_id (str PK), detected_at (timestamp), station_id (str), anomaly_type (str), severity_score (float), reconstruction_error (float), culprit_sensors (json/text), diagnostic_message (text), status (str), resolution_note (text).
   - Table `operator_feedback`: id (UUID), anomaly_id (str), label (str), note (text), created_at (timestamp).
   - Function `init_db()` to automatically create tables if missing.
2. Update `backend/data/store.py` so that all incoming readings, anomalies, and feedback are written to the database asynchronously while maintaining in-memory caching for live 1 Hz reads.
3. Update `backend/requirements.txt` with asyncpg>=0.29.0, psycopg2-binary>=2.9.9, sqlalchemy>=2.0.0, and aiosqlite>=0.19.0.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Go to [supabase.com](https://supabase.com) and click **Sign Up** (free tier).
- [ ] Click **New Project**, name it `skyguard-db`, choose a password and the nearest region.
- [ ] In Supabase $\to$ **Project Settings** $\to$ **Database** $\to$ **Connection String** $\to$ **URI**, copy the URL.
- [ ] Paste it into `backend/.env`:
  ```env
  DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
  ```

#### 4. How to Test & Verify
- **Test Command (PowerShell / Terminal):**
  ```powershell
  cd backend
  python -c "import asyncio; from data.db import init_db; asyncio.run(init_db()); print('Database tables verified successfully!')"
  ```
- **Expected Result:** Output displays `Database tables verified successfully!`. In Supabase Table Editor, verify `telemetry_records` and `anomaly_events` are created.

---

### Task 2: Azure VM & Mosquitto Broker Provisioning

- **Owner:** Any Team Member (Estimated time: 60 mins)
- **Priority:** Must Have (Critical Path)
- **Files Touched:** `deploy/Dockerfile.backend`, `deploy/mosquitto.conf`, `docker-compose.yml`

#### 1. What to Build
Provision an Ubuntu VM in Azure using student credits. Configure Docker Compose to run Mosquitto MQTT broker on port `1883` and FastAPI on port `8000`.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Create the deployment configuration files for SkyGuard AI on an Azure Ubuntu VM:
1. `deploy/mosquitto.conf`:
   listener 1883 0.0.0.0
   allow_anonymous true
   persistence true
   persistence_location /mosquitto/data/
   log_dest stdout

2. `deploy/Dockerfile.backend`:
   - Base image: python:3.10-slim
   - Install system build tools needed for numpy and onnxruntime
   - Copy backend/ and install requirements.txt
   - Expose port 8000
   - Command: uvicorn main:app --host 0.0.0.0 --port 8000

3. `docker-compose.yml` at repository root:
   - Service `mosquitto`: image `eclipse-mosquitto:2`, ports ["1883:1883"], mounts deploy/mosquitto.conf
   - Service `backend`: builds deploy/Dockerfile.backend, ports ["8000:8000"], environment variables for DATABASE_URL and CORS_ORIGINS="*"
   - Depends on mosquitto
```

#### 3. Human Work (Portal Clicks & Copy-Pasting)
- [ ] In [portal.azure.com](https://portal.azure.com), create a Virtual Machine:
  - Name: `skyguard-vm` | Image: **Ubuntu 22.04 LTS** | Size: **Standard_B2s** (~$1/day from student credit).
  - Save `skyguard-vm_key.pem`.
- [ ] In VM **Networking** $\to$ **Add inbound port rule**: allow destination ports `1883,8000,22`.
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
  { "status": "healthy", "service": "SkyGuard AI - AWS Anomaly Detection Engine" }
  ```

---

### Task 3: Synthetic Dataset Generation & Physical Validation

- **Owner:** Any Team Member (Estimated time: 45 mins)
- **Priority:** Must Have (Data Foundation)
- **Files Touched:** `scripts/generate_dataset.py`, `data/train_baseline_normal.csv`, `data/test_fault_injections.csv`

#### 1. What to Build
A standalone data generation script that synthesizes realistic weather telemetry modeled on India Meteorological Department (IMD) climatological data for Agra (North Indian plains). Generates two CSV datasets:
1. `train_baseline_normal.csv`: 10,000 clean 10-minute timesteps exhibiting diurnal cycles, inverse T-RH thermodynamic coupling, barometric tides, and solar radiation.
2. `test_fault_injections.csv`: Labeled test set containing known anomalies (heat spikes, severe squalls, capacitive humidity drift, and stuck sensors).

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Create `scripts/generate_dataset.py` that generates training and test datasets for SkyGuard AI:
1. Normal Diurnal Generator:
   - Station: AGRA-01 (Agra agro-meteorological zone).
   - Generates 10,000 timesteps at 10-minute cadence.
   - Diurnal Temperature curve: 24°C to 38°C peak at 14:00.
   - Relative Humidity inversely coupled to Temperature: 40% (afternoon) to 85% (early morning).
   - Barometric Pressure with semi-diurnal tides: 1002 to 1008 hPa.
   - Magnus Dew Point calculation: Td <= T + 0.5.
   - Calculated derivatives: dT_dt, dP_dt, dRH_dt.
   - Output: `data/train_baseline_normal.csv`.
2. Fault Injection Generator:
   - Output: `data/test_fault_injections.csv` with labeled columns:
     - Normal baseline periods (label = 'normal')
     - Severe Thunderstorm Squall true-negative test (label = 'valid_squall': pressure drops -12 hPa, humidity surges to 92%, temp drops -8°C)
     - Subtle +15% Capacitive Drift (label = 'capacitive_drift': humidity drifts upward while temperature remains warm)
     - Instant Heat Spike (label = 'heat_spike': +8°C jump in 10 min)
     - Stuck Sensor (label = 'stuck_humidity': flatline at 100% RH)
3. Generate a validation summary: check that zero normal timesteps violate physical bounds and verify negative correlation between T and RH.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Run the generator script in your terminal:
  ```powershell
  python scripts/generate_dataset.py
  ```
- [ ] Confirm `train_baseline_normal.csv` and `test_fault_injections.csv` are created inside `data/`.

#### 4. How to Test & Verify
- **Test Command (PowerShell / Terminal):**
  ```powershell
  python -c "import pandas as pd; df = pd.read_csv('data/train_baseline_normal.csv'); print('Normal Rows:', len(df)); print('T-RH Correlation:', df['temperature_c'].corr(df['humidity_pct'])); assert df['temperature_c'].corr(df['humidity_pct']) < -0.7, 'Physics error: T and RH must be negatively correlated'"
  ```
- **Expected Result:** Terminal outputs `Normal Rows: 10000` and `T-RH Correlation: -0.85` (confirming realistic physical inverse coupling).

---

### Task 4: 1D-CNN Autoencoder Training & ONNX Export (Google Colab)

- **Owner:** Any Team Member (Estimated time: 45 mins)
- **Priority:** Must Have (Core ML Engine)
- **Files Touched:** `notebooks/02_train_autoencoder.ipynb`, `backend/ml_artifacts/autoencoder.onnx`, `backend/ml_artifacts/scaler.json`

#### 1. What to Build
A dedicated Google Colab notebook that loads `data/train_baseline_normal.csv`, trains a compact 1D-CNN Autoencoder using PyTorch or TensorFlow, evaluates reconstruction performance on `data/test_fault_injections.csv`, exports `backend/ml_artifacts/autoencoder.onnx` ($<200\text{ KB}$), saves normalization parameters to `scaler.json`, and generates publication-grade training curves for the video presentation.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Create `notebooks/02_train_autoencoder.ipynb` for training and exporting our 1D-CNN autoencoder in Google Colab:
1. Load `data/train_baseline_normal.csv` and construct sliding windows of shape (batch, 12 timesteps, 8 features).
2. Fit a RobustScaler on baseline features and export parameters to `scaler.json`.
3. Build the 1D-CNN Autoencoder:
   - Encoder: Conv1D(16 filters, kernel=3, relu, padding='same') -> Conv1D(8 filters, kernel=3, relu) -> Flatten -> Dense(8) [latent bottleneck vector z]
   - Decoder: Dense(12*8) -> Reshape((12, 8)) -> ConvTranspose1D(16 filters, kernel=3, padding='same') -> Conv1D(8 filters, kernel=3, padding='same')
4. Train for 15 epochs using Adam (lr=1e-3) and MSE loss.
5. Evaluate on `data/test_fault_injections.csv`:
   - Calculate reconstruction MSE for normal periods vs capacitive drift vs severe storm.
   - Show that normal weather and severe storms have low MSE (< 0.030), while capacitive drift produces high MSE (> 0.045).
   - Set Anomaly Threshold tau at the 99.5th percentile of normal errors (~0.042).
6. Export the trained model to `autoencoder.onnx`.
7. Generate 3 presentation plots:
   - Plot 1: Training & Validation Loss Curve.
   - Plot 2: Reconstruction Error Distribution (Normal vs Injected Drift).
   - Plot 3: Correlation Heatmap showing learned feature manifold.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Open [colab.research.google.com](https://colab.research.google.com) $\to$ Upload `notebooks/02_train_autoencoder.ipynb`.
- [ ] Upload `data/train_baseline_normal.csv` and `data/test_fault_injections.csv` into Colab's file browser.
- [ ] Click **Runtime** $\to$ **Run all**.
- [ ] Download the generated `autoencoder.onnx` and `scaler.json` files and place them into `backend/ml_artifacts/`.
- [ ] Save the generated loss curve and evaluation plots for the presentation video!

#### 4. How to Test & Verify
- **Test Command (PowerShell / Terminal):**
  ```powershell
  python -c "import os, onnxruntime as ort; assert os.path.exists('backend/ml_artifacts/autoencoder.onnx'); sess = ort.InferenceSession('backend/ml_artifacts/autoencoder.onnx'); print('ONNX Model Loaded! Input Shape:', sess.get_inputs()[0].shape); print('Model File Size:', os.path.getsize('backend/ml_artifacts/autoencoder.onnx'), 'bytes')"
  ```
- **Expected Result:** Output displays `ONNX Model Loaded! Input Shape: [None, 12, 8]` with file size $< 500,000$ bytes.

---

### Task 5: Real-Time Live ML Pipeline & MQTT Ingestion (FastAPI Backend)

- **Owner:** Any Team Member (Estimated time: 60 mins)
- **Priority:** Must Have (Real-Time ML Engine)
- **Files Touched:** `backend/services/anomaly_detector.py`, `backend/services/mqtt_subscriber.py`, `backend/routers/telemetry.py`

#### 1. What to Build
Upgrade the FastAPI backend so that on **every single 1 Hz telemetry packet** received from Mosquitto:
1. It runs live inference using `onnxruntime` CPU ($\sim 2\text{ ms}$).
2. Calculates real-time Reconstruction Error (MSE) and compares against threshold $\tau = 0.042$.
3. Calculates real-time SHAP feature attribution.
4. Enriches the 1 Hz SSE stream with a live `ml_metrics` payload containing real-time MSE, threshold status, and feature contributions.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Integrate real-time ONNX inference into the SkyGuard AI backend:
1. Update `backend/services/anomaly_detector.py`:
   - On startup, load `backend/ml_artifacts/autoencoder.onnx` using onnxruntime.InferenceSession and `scaler.json`.
   - On each incoming reading, build the 12-sample sliding window, normalize it, and run ONNX inference.
   - Compute real-time MSE: float(np.mean((window - reconstructed)**2)).
   - Decompose MSE into per-sensor SHAP attribution percentages: [temperature, humidity, pressure, dew_point].
   - Return an MLResult dict:
     { "reconstruction_error": mse, "threshold": 0.042, "is_anomaly": mse > 0.042, "shap_values": [...], "latency_ms": elapsed_ms }
2. Update `backend/services/mqtt_subscriber.py`:
   - Subscribes to `weather/+/telemetry`.
   - Passes data through IMD Physics Rules (Stage 1), then through the live ONNX Anomaly Detector (Stage 2).
   - Writes to `store` (persists to Supabase).
   - Broadcasts SSE event: `event: telemetry` containing both sensor data AND `ml_metrics`.
3. Add `onnxruntime>=1.16.0` to `backend/requirements.txt`.
```

#### 3. Human Work (No Syntax Writing)
- [ ] Commit changes, push to GitHub, and pull onto your Azure VM:
  ```bash
  cd SkyGuard_SIH && git pull && sudo docker-compose up -d --build
  ```

#### 4. How to Test & Verify
- **Test Command:** Test real-time inference locally:
  ```powershell
  python -c "from services.anomaly_detector import anomaly_detector; from models.schemas import TelemetryPayload; from datetime import datetime, timezone; w = [TelemetryPayload(timestamp=datetime.now(timezone.utc).isoformat(), temperature_c=32.0, pressure_hpa=1005.0, humidity_pct=55.0, dew_point_c=22.0, sequence=i) for i in range(12)]; res = anomaly_detector.evaluate_window(w); print('Live Inference Output:', res)"
  ```
- **Expected Result:** Output prints real-time reconstruction error and SHAP attribution with zero errors.

---

### Task 6: Laptop 1 Hardware Weather Station Emulator

- **Owner:** Any Team Member (Estimated time: 45 mins)
- **Priority:** Must Have (Critical Path)
- **Files Touched:** `backend/simulator/client.py`

#### 1. What to Build
A standalone Python executable to run on **Laptop 1** that acts as the physical Automatic Weather Station hardware. It streams 1 Hz weather readings over MQTT to the Azure VM and provides interactive keyboard keys to inject faults live on camera.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Create `backend/simulator/client.py` for Laptop 1 representing physical AWS hardware:
- Connects via `paho-mqtt` to `--host` on port 1883.
- Publishes to topic `weather/AGRA-01/telemetry` every 1.0 second.
- Default weather: realistic diurnal cycle (Temp 28-35°C, Humidity 50-70%, Pressure ~1005 hPa).
- Listens for terminal keyboard keypresses:
    '1' -> Heat Spike (+8°C instant jump)
    '2' -> Capacitive Drift (+15% humidity bias while temp remains high)
    '3' -> Severe Thunderstorm (Pressure drops -11 hPa, Humidity surges to 94%, Temp drops -8°C)
    '0' -> Reset to Baseline Normal
- Prints real-time terminal output:
  [TX SEQ #1042] -> AGRA-01: Temp=32.4°C | Humidity=58.2% | Pressure=1005.1 hPa | Mode=NORMAL
```

#### 3. Human Work (No Syntax Writing)
- [ ] On **Laptop 1**, install requirements: `pip install paho-mqtt`.
- [ ] Run the emulator pointing to your Azure VM:
  ```powershell
  python backend/simulator/client.py --host <VM_PUBLIC_IP>
  ```

#### 4. How to Test & Verify
- **Test Steps:**
  1. Watch Laptop 1's terminal: verify `[TX SEQ #...]` logs tick once every second.
  2. Press key `2` (Drift): verify terminal indicates `FAULT ACTIVE: CAPACITIVE DRIFT`.
  3. Press key `0`: verify terminal indicates `RESET TO NORMAL`.

---

### Task 7: Laptop 2 Real-Time ML Dashboard & 3D Digital Twin

- **Owner:** Any Team Member (Estimated time: 60 mins)
- **Priority:** Must Have (Visual Showcase)
- **Files Touched:** `frontend/src/components/panels/LiveMLPipelinePanel.tsx`, `frontend/src/components/panels/ShapChart.tsx`, `frontend/src/app/page.tsx`, `frontend/.env.local`

#### 1. What to Build
A dedicated **Live ML Pipeline Monitor** panel on Laptop 2's dashboard that visualizes the ML model running in real time:
1. **Live MSE Error Gauge & Waveform:** A line chart moving tick-by-tick at 1 Hz, showing the live reconstruction error relative to the red threshold line ($\tau = 0.042$).
2. **Live Dynamic SHAP Bars:** Bars that adjust every second to reflect real-time feature contributions.
3. **Cinematic 3D Camera Focus:** The moment the MSE line crosses the threshold, the 3D twin turns Red and smoothly auto-zooms into the culprit sensor.

#### 2. Sequence of Instructions to AI Agent
Paste this exact prompt into your AI coding assistant:

```text
Build a Live ML Pipeline Monitor panel on the Next.js frontend:
1. Create `frontend/src/components/panels/LiveMLPipelinePanel.tsx`:
   - Receives `ml_metrics` from the 1 Hz SSE stream.
   - Displays a real-time sparkline of the last 30 seconds of Reconstruction MSE.
   - Draws a prominent red dashed reference line at Anomaly Threshold: 0.042.
   - Displays current numerical MSE (e.g. 0.0162) and Model Inference Latency (e.g. 2.4 ms).
   - Displays status badge: NOMINAL (Green) or ANOMALY BREACH (Red pulse).
2. Update `frontend/src/components/panels/ShapChart.tsx` so that feature attribution bars update dynamically every second rather than only showing static text when normal.
3. Mount `LiveMLPipelinePanel` inside `frontend/src/app/page.tsx` right next to the 3D Digital Twin.
4. Ensure `frontend/.env.local` points to `NEXT_PUBLIC_API_URL=http://<VM_PUBLIC_IP>:8000/api/v1`.
```

#### 3. Human Work (No Syntax Writing)
- [ ] On **Laptop 2**, start the frontend:
  ```powershell
  cd frontend
  npm install
  npm run dev
  ```
- [ ] Open `http://localhost:3000` in Google Chrome and press `F11` for full screen.

#### 4. How to Test & Verify
- **Test Steps:**
  1. Look at Laptop 2: verify the **Live ML Pipeline Monitor** updates every second with MSE $\approx 0.015$ (Green).
  2. On Laptop 1, press `2` (Capacitive Drift).
  3. Watch Laptop 2: the MSE curve climbs in real time ($0.018 \to 0.027 \to 0.039 \to 0.048$), crosses the red dashed line, the 3D twin flashes Red, and the camera auto-zooms into the humidity cylinder!

---

### Task 8: End-to-End Two-Laptop Smoke Test

- **Owner:** Two Team Members together (Estimated time: 30 mins)
- **Priority:** Must Have (Pre-Recording Gate)
- **Files Touched:** None (Testing only)

#### 1. What to Build
A complete rehearsal verifying the entire live loop across both machines.

#### 2. Test Execution Checklist

| Step | Action | Expected Output | Status |
|---|---|---|---|
| **Step 1** | Check Azure VM health | `http://<VM_PUBLIC_IP>:8000/health` returns `healthy` | [ ] Pass |
| **Step 2** | Start Laptop 1 client | Terminal ticks: `[TX SEQ #...]` once per second | [ ] Pass |
| **Step 3** | Open Laptop 2 dashboard | 3D Twin is Green; Live ML Pipeline shows MSE $\approx 0.015$ | [ ] Pass |
| **Step 4** | Press `3` on Laptop 1 (Storm) | Pressure drops, but MSE stays under threshold; station stays **Green** | [ ] Pass |
| **Step 5** | Press `2` on Laptop 1 (Drift) | MSE climbs live on screen; crosses $0.042$; station turns **Red**; camera zooms to humidity | [ ] Pass |
| **Step 6** | Check SHAP Attribution | Humidity bar indicates $>80\%$ contribution | [ ] Pass |
| **Step 7** | Click "False Alarm" on Laptop 2 | Anomaly updates; feedback row created in Supabase | [ ] Pass |
| **Step 8** | Press `0` on Laptop 1 (Reset) | MSE drops back to $\approx 0.014$; station returns to Green overview | [ ] Pass |

---

### Task 9: Video Presentation Recording & Storyboard

- **Owner:** Entire Team (Estimated time: 60-90 mins)
- **Priority:** Must Have (Final Deliverable)
- **Deliverable:** 3 to 5-Minute Video File (`SkyGuard_AI_Showcase.mp4`)

#### 1. Recording Setup
- Place **Laptop 1** (terminal edge simulator) and **Laptop 2** (3D Digital Twin + Live ML Monitor) side-by-side on a desk, or use OBS Studio to record both screens side-by-side.

#### 2. Timed 5-Minute Narration Script

```
[0:00 - 0:45] SYSTEM ARCHITECTURE & PROOF OF CONCEPT
- Show both laptops: "Welcome to SkyGuard AI. On Laptop 1, we emulate Automatic Weather Station
  hardware streaming 1 Hz telemetry over MQTT. On our Azure Cloud VM, our 1D-CNN autoencoder
  processes each packet in real time. On Laptop 2, our control room visualizes the live ML pipeline."
- Point out the Live ML Pipeline Monitor: "Notice the real-time reconstruction error running at 2.4 ms
  latency, currently at 0.015—well below our operating threshold of 0.042."

[0:45 - 1:45] TRUE NEGATIVE TEST: SEVERE THUNDERSTORM
- Presenter presses [3] on Laptop 1.
- Show pressure drop (-11 hPa) and humidity surge (94%).
- Point to Laptop 2: "Notice the station remains GREEN. Why? Because the ML autoencoder understands
  multivariate correlation: during natural storms, temperature and pressure move together in physically
  consistent manifolds. Zero false alarms!"

[1:45 - 3:00] SILENT CAPACITIVE DRIFT & REAL-TIME ML DETECTION
- Presenter presses [2] on Laptop 1 to inject subtle +15% capacitive humidity drift.
- "Watch the live ML monitor on Laptop 2 in real time. As drift enters the sliding window, the
  reconstruction error climbs tick-by-tick: 0.022... 0.034... 0.044!"
- The line breaches the red threshold! The 3D twin flashes RED, the camera smoothly auto-focuses onto
  the humidity radiation shield, and the SHAP bar chart confirms humidity as the 86% culprit!

[3:00 - 3:45] OPERATOR TRIAGE & ACTIVE LEARNING LOOP
- Presenter on Laptop 2 clicks "Acknowledge" and "Mark as False Alarm".
- "Every operator action logs the autoencoder's 8-dimensional latent bottleneck vector to our Supabase
  PostgreSQL database, where DBSCAN clustering identifies recurrent false positive patterns."

[3:45 - 4:30] DATA SCIENCE DEPTH (GOOGLE COLAB)
- Show 30 seconds of the Google Colab notebook: training loss curves, PR-AUC (>0.92), and correlation
  heatmaps that prove model generalizability.

[4:30 - 5:00] CONCLUSION & IMPACT
- "SkyGuard AI: Deterministic IMD physics paired with real-time explainable deep learning to eliminate
  silent sensor failures across India's meteorological network."
```

---

## 🛡️ Zero-Cost Guardrails & Budget Summary

| Service | Tier / Plan | Cost | Quota Limit |
|---|---|---|---|
| **Azure Virtual Machine** | Standard_B2s (Ubuntu 22.04) | ~$1.00 / day | Covered by your $100 Azure for Students grant ($95 remaining). |
| **Supabase PostgreSQL** | Free Tier | $0.00 | 500 MB storage (we use $<5\text{ MB}$). |
| **Mosquitto MQTT** | Open-source Docker container | $0.00 | Hosted inside your Azure VM. |
| **Google Colab** | Free CPU/T4 GPU runtime | $0.00 | Free cloud execution. |
| **Next.js Frontend** | Runs locally on Laptop 2 | $0.00 | Free local execution. |
| **Total Out-of-Pocket Expense** | | **$0.00** | **100% Free** |

> [!TIP]
> **To Save Azure Credits:** When you finish working for the day, stop the VM in the Azure Portal (`az vm deallocate`). Start it again when you resume testing!

---

## 🚨 Emergency Pitch Fallback Plan

If cloud WiFi or the Azure VM is unavailable during recording:

> [!IMPORTANT]
> Run the entire system locally on Laptop 2 in 10 seconds:
> ```powershell
> # Open Terminal 1 (Backend)
> cd backend; python main.py
>
> # Open Terminal 2 (Frontend)
> cd frontend; npm run dev
> ```
> Open `http://localhost:3000`. The internal simulator will automatically take over!
