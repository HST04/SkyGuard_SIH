# 📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon)

> **Submission Deadline:** 2 Days (48 Hours)  
> **Who is this guide for?**  
> Anyone on the team who has been assigned a task and feels overwhelmed by technical terms. You do **not** need to write code. You just need to copy-paste prompts into your AI assistant, click buttons, and run simple test commands.  
> Every single step below explains **what** we are doing and **why** it matters in plain, simple words!

---

## 🗺️ How the System Works

```
 [LAPTOP 1: Weather Station]
       │  (Reads temperature & humidity every second)
       │  (Filters basic errors and saves the last 2 hours in a circular buffer)
       ▼
 [AZURE CLOUD SERVER: Backend Engine]
       ├── Saves readings to Database (Supabase PostgreSQL + local SQLite fallback)
       ├── Model A: Identifies natural weather events (e.g. thunderstorms)
       ├── Model B: Identifies physical sensor defects (e.g. drift, flatlines)
       ├── Confluence Decision Matrix: Evaluates both models to classify the event
       ├── Predictive Maintenance: Tracks sensor drift over days
       └── Imputation Module: Reconstructs faulty sensor values from healthy sensors
       │
       ▼
 [LAPTOP 2: Control Room Dashboard]
       └── Shows 4 tabs (Live ML, SHAP Explainability, Maintenance, Imputation)
           and an interactive 3D weather station that auto-focuses on faulty sensors.
```

---

## 👥 Team Assignments & Coordination

| Member | Assigned Component | Deliverable Handed Off | Branch |
|---|---|---|---|
| **Hanswarup** | Pull requests, Docker setup, and the Multi-Scale Analyzer (calculates rates of change and thermodynamic coupling). | Running cloud server (ports 1883 & 8000) and analyzer service | `feat/hanswarup` |
| **Yukti** | Training in Google Colab (1D-CNN Autoencoder, Model A Weather Classifier, Model B Defect Classifier). | Model weight files in `backend/ml_artifacts/` | `feat/yukti` |
| **Araz** | Dataset checking and the Laptop 1 emulator script (5 chaos keys, 2-hour circular buffer, context burst). | Datasets in `data/` and 1 Hz MQTT live stream | `feat/araz` |
| **Mudit** | Database setup (Supabase + SQLite fallback) and the Confluence Decision Matrix service. | Database tables and confluence decision service | `feat/mudit` |
| **Harsh** | Predictive maintenance drift tracker, imputation service, and telemetry ingestion pipeline. | 1 Hz SSE stream broadcasting all metrics | `feat/harsh` |
| **Shreyansh** | Next.js 4-tab control room dashboard and 3D digital twin camera auto-zoom. | Web dashboard on `localhost:3000` | `feat/shreyansh` |

### 🔄 Technical Handoffs:
1. **Araz ➔ Yukti:** Araz provides `train_baseline_normal.csv` and `test_fault_injections.csv`. Yukti uploads them to Colab to train the models.
2. **Yukti ➔ Hanswarup, Mudit, Harsh:** Yukti exports model files to `backend/ml_artifacts/`. Hanswarup adds dependencies to Docker; Mudit and Harsh load them in backend services.
3. **Hanswarup ➔ Mudit, Harsh:** Hanswarup's Multi-Scale Analyzer calculates rates of change ($dT/dt, dP/dt$) and passes them to Mudit's confluence service and Harsh's ingestion pipeline.
4. **Harsh ➔ Shreyansh:** Harsh bundles telemetry, confluence decision, maintenance drift, and imputed values into the 1 Hz SSE stream; Shreyansh binds these values to the 4 dashboard tabs.
5. **Hanswarup ➔ Araz:** Hanswarup runs Mosquitto on port 1883; Araz points the Laptop 1 transmitter to that port.
6. **All ➔ Hanswarup:** Members push to their branch and open pull requests; Hanswarup reviews diffs, runs tests, and merges into `main`.

---

## 🟢 STAGE 1: Setting Up the Cloud Notebook (The Database)

### 🎯 The Goal:
Give our system a safe storage place in the cloud so readings and alerts never disappear when laptops turn off.

### 🧠 Why are we doing this? (The Analogy)
If your computer battery dies while running an experiment, everything in memory is lost. A database is like an indestructible cloud notebook. Every reading, every alert, and every operator note gets written down forever. If the cloud loses internet for a moment, our code is smart enough to write to a local notebook file on your laptop instead of crashing!

---

### Step 1: Create a Free Supabase Account
1. Open your web browser and go to: **[supabase.com](https://supabase.com)**
2. Click **Start your project** (sign in using your GitHub or Google account).
3. Click **New Project**.
4. Type in:
   - **Name:** `skyguard-db`
   - **Password:** Pick something easy to remember, like `SkyGuard2026!` (write it down!).
   - **Region:** Pick the one closest to you (e.g. `Central India` or `East US`).
5. Click **Create new project** and wait ~60 seconds.
- [ ] *Done!*

### Step 2: Copy Your Secret Database Link
1. In Supabase, look at the bottom-left corner and click the ⚙️ **Project Settings** icon.
2. Click **Database** on the left menu.
3. Scroll down until you see **Connection string**, then click the **URI** tab.
4. Copy the long link shown. It looks like this:  
   `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxx.supabase.co:5432/postgres`
5. Replace `[YOUR-PASSWORD]` with the password you chose in Step 1.
- [ ] *Done!*

### Step 3: Tell the AI to Connect the Code
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this prompt:

```text
Connect our FastAPI backend to Supabase PostgreSQL with an automatic SQLite fallback:
1. Create `backend/data/db.py`:
   - Read DATABASE_URL from .env. If empty or unreachable, fall back to 'sqlite+aiosqlite:///./skyguard.db'.
   - Create 4 tables:
     - telemetry_records: stores every second of weather data (T, P, RH, wind, solar).
     - anomaly_incidents: stores detected anomalies, confluence decision, confidence score, culprit sensor, and justification.
     - maintenance_predictions: stores sensor drift tracking and days until recalibration.
     - operator_feedback: stores when a human clicks "False Alarm" or "Confirmed Defect".
   - Function init_db() to create tables if they do not exist.
2. Update `backend/data/store.py` so incoming readings are saved to db.py in background tasks.
3. Update `backend/requirements.txt` to include: sqlalchemy>=2.0.0, asyncpg>=0.29.0, aiosqlite>=0.19.0.
4. Create `backend/.env` with: DATABASE_URL=<PASTE_YOUR_LINK_HERE>
```
*(Remember to put your real database link at the bottom of the prompt!)*
- [ ] *Done!*

### Step 4: Test It!
1. Open your terminal in VS Code / PowerShell.
2. Run this command:
   ```powershell
   cd backend
   python -c "import asyncio; from data.db import init_db; asyncio.run(init_db()); print('SUCCESS: Database notebook is ready!')"
   ```
3. 👀 **What success looks like:** The terminal prints:  
   `SUCCESS: Database notebook is ready!`
- [ ] *Done!*

---

## 🟢 STAGE 2: Setting Up the Cloud Server (The Azure Brain)

### 🎯 The Goal:
Create a computer on the internet that stays on 24/7 so Laptop 1 can send weather data to it from anywhere.

### 🧠 Why are we doing this? (The Analogy)
If Laptop 1 and Laptop 2 are in different rooms or on different Wi-Fi networks, they cannot talk to each other directly without a shared cloud server. The Azure computer acts as a central post office that receives messages from Laptop 1 and forwards them to Laptop 2.

---

### Step 5: Create a Free Virtual Computer on Azure
1. Go to **[portal.azure.com](https://portal.azure.com)** and sign in with your student email.
2. In the top search bar, type `Virtual Machines` and click on it.
3. Click **Create** $\to$ **Azure virtual machine**.
4. Fill in:
   - **Subscription:** Azure for Students (uses your free $100 grant)
   - **Resource group:** Click *Create new* $\to$ type `rg-skyguard`
   - **Name:** `skyguard-vm`
   - **Image:** **Ubuntu Server 22.04 LTS**
   - **Size:** **Standard_B2s** (~$1/day, completely free from student credit)
   - **Authentication:** SSH public key $\to$ Key name: `skyguard-key`
5. Click **Review + create** $\to$ Click **Create**.
6. When a popup appears, click **Download private key and create resource**. Save `skyguard-key.pem` on your laptop!
- [ ] *Done!*

### Step 6: Open the Cloud Doors (Ports 1883, 8000, 22)
1. In Azure, open your `skyguard-vm`.
2. Click **Networking** on the left menu.
3. Click **Add inbound port rule**.
4. Set **Destination port ranges** to: `1883,8000,22` and click **Add**.
5. Look at the Overview page of your VM and copy your **Public IP address** (e.g., `20.120.45.67`). Write it down!
- [ ] *Done!*

### Step 7: Start the Server Software
1. Open PowerShell on your computer and connect to Azure:
   ```powershell
   ssh -i "path\to\skyguard-key.pem" azureuser@<YOUR_PUBLIC_IP>
   ```
2. Paste this single command to download and start the software:
   ```bash
   sudo apt-get update && sudo apt-get install -y docker.io docker-compose git
   git clone https://github.com/<YOUR_GITHUB_USERNAME>/SkyGuard_SIH.git && cd SkyGuard_SIH
   sudo docker-compose up -d --build
   ```
- [ ] *Done!*

### Step 8: Test It!
1. Open Google Chrome and type: `http://<YOUR_PUBLIC_IP>:8000/health`
2. 👀 **What success looks like:** A clean web page saying:
   ```json
   { "status": "healthy", "service": "SkyGuard AI - AWS Anomaly Detection Engine" }
   ```
- [ ] *Done!*

---

## 🟢 STAGE 3: Creating the Weather Materials (The Teacher Data)

### 🎯 The Goal:
Create realistic Indian weather data and fake sensor defects so our AI can learn the difference between a natural storm and a broken sensor.

### 🧠 Why are we doing this? (The Analogy)
Real weather sensors almost never break while an engineer is standing there taking notes. If we wait for a sensor to break in real life, we would wait 5 years! So we use math to inject 5 types of fake sensor defects:
1. **The Frozen Sensor:** Humidity gets stuck at 84% all day even when the sun gets hot.
2. **The Electric Shock (Spike):** Temperature jumps +8°C in 1 second.
3. **The Slow Drift:** Humidity slowly creeps +15% higher than it should be because of dust.
4. **The Noisy Sensor:** Wild fuzzy vibrations caused by loose wires.
5. **The Thunderstorm (The Test):** Pressure drops -11 hPa and humidity surges to 94%—this is a REAL storm, NOT a broken sensor!

---

### Step 9: Tell the AI to Write the Weather Generator
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this prompt:

```text
Update `scripts/generate_dataset.py` to create comprehensive training datasets:
1. Normal Indian Weather (data/train_baseline_normal.csv):
   - 15,000 timesteps for station AGRA-01.
   - Temperature peaks at 38°C in afternoon, cools to 22°C at night.
   - Humidity moves OPPOSITE to temperature (40% afternoon, 85% early morning).
   - Pressure has natural tides between 1002 and 1008 hPa.
2. Labeled Multi-Class Test Dataset (data/test_fault_injections.csv):
   - 'nominal': clean weather.
   - 'squall': severe thunderstorm (pressure plunge -12 hPa, humidity surge 94%, temp drop -8°C).
   - 'frozen_value': RH stuck at 84.2% for 4 hours while temperature changes.
   - 'capacitive_drift': RH slowly climbs +15% too high.
   - 'impulse_spike': +8°C instant spike.
   - 'noise_burst': high-frequency fuzzy noise on one channel.
   - 'packet_dropout': missing data packets.
3. Check and confirm negative correlation between T and RH (r < -0.7).
```
- [ ] *Done!*

### Step 10: Run the Generator
1. In your terminal, run:
   ```powershell
   python scripts/generate_dataset.py
   ```
2. 👀 **What success looks like:** The terminal prints:  
   `Normal rows: 15000. T-RH Correlation: -0.84. Injected test sets created in data/ folder!`
- [ ] *Done!*

---

## 🟢 STAGE 4: Training the AI Brain in Google Colab (Free GPU)

### 🎯 The Goal:
Train our two specialized AI models and our autoencoder in Google Colab, and download the finished brain files.

### 🧠 Why are we doing this? (The Analogy)
Instead of one confused AI trying to do everything, we use a team of specialists:
- **The Autoencoder:** Measures how weird the weather looks compared to normal (MSE error score).
- **Model A (The Weather Detective):** Answers: *"Does this look like a real thunderstorm or cloudburst?"*
- **Model B (The Hardware Mechanic):** Answers: *"Does this look like a broken, drifting, or frozen sensor?"*
Google Colab lets us train all three in under 2 minutes on Google's free cloud computers!

---

### Step 11: Tell the AI to Create the Colab Training Notebook
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this prompt:

```text
Create `notebooks/02_train_autoencoder.ipynb` to train our complete ML pipeline in Google Colab:
1. Load train_baseline_normal.csv and test_fault_injections.csv.
2. Train Model 1 (1D-CNN Autoencoder):
   - Sliding window of 12 timesteps.
   - Normal weather produces low reconstruction error (< 0.025).
   - Broken sensors produce high reconstruction error (> 0.042).
   - Export to `backend/ml_artifacts/autoencoder.onnx` (< 200 KB) and `scaler.json`.
3. Train Model 2 (Model A - Weather Classifier):
   - LightGBM model that outputs P(Weather) in [0.0, 1.0].
   - Export to `backend/ml_artifacts/model_a_weather.pkl`.
4. Train Model 3 (Model B - Sensor Defect Classifier):
   - LightGBM model trained on synthetic faults that outputs P(Defect) in [0.0, 1.0] and defect type.
   - Export to `backend/ml_artifacts/model_b_defect.pkl`.
5. Generate 3 presentation plots:
   - Loss curve, Error separation curve (Storm vs Drift), and Model Accuracy Confusion Matrix.
   - Save all plots to `backend/ml_artifacts/plots/`.
```
- [ ] *Done!*

### Step 12: Train in Google Colab (Zero Setup)
1. In your browser, open: **[colab.research.google.com](https://colab.research.google.com)**
2. Click **Upload** $\to$ select `notebooks/02_train_autoencoder.ipynb`.
3. Click the 📁 **Folder icon** on the left menu. Drag and drop both CSV files (`train_baseline_normal.csv` and `test_fault_injections.csv`) into that folder.
4. Click top menu: **Runtime** $\to$ **Run all**.
5. Wait ~90 seconds. Look at the graphs—they will show that storms stay green while broken sensors spike red!
6. In the left folder tab, right-click and download:
   - `autoencoder.onnx`
   - `model_a_weather.pkl`
   - `model_b_defect.pkl`
   - `scaler.json`
   - The plot images (save these for your presentation slides!).
7. Move these downloaded files into your project folder: `backend/ml_artifacts/`.
- [ ] *Done!*

### Step 13: Test It!
1. In your terminal, run:
   ```powershell
   python -c "import os; p = 'backend/ml_artifacts'; assert os.path.exists(f'{p}/autoencoder.onnx'); assert os.path.exists(f'{p}/model_a_weather.pkl'); assert os.path.exists(f'{p}/model_b_defect.pkl'); print('SUCCESS: All 3 AI Brain files are ready!')"
   ```
2. 👀 **What success looks like:** Terminal prints:  
   `SUCCESS: All 3 AI Brain files are ready!`
- [ ] *Done!*

---

## 🟢 STAGE 5: Building the Cloud Decision Engine (The Judge & Doctor)

### 🎯 The Goal:
Connect our models in FastAPI so that every second, the cloud evaluates data with:
1. **The Confluence Judge:** Combines Model A and Model B into an ironclad decision (Storm vs Broken Sensor).
2. **The Maintenance Doctor:** Warns if a sensor is slowly drifting weeks before it fails.
3. **The Data Repairman (Imputation):** Suggests the real temperature or humidity if a sensor breaks.

### 🧠 Why are we doing this? (The Analogy)
If Model A says *"95% chance it's a thunderstorm"* and Model B says *"2% chance it's broken"*, the Confluence Judge says: *"DO NOT ALARM! It's just rain!"*  
If Model B says *"94% chance of humidity drift"* and Model A says *"5% chance of weather"*, the Judge fires an alert: *"Sensor Defect (92% Confidence)"*.  
Meanwhile, the Doctor calculates when the technician needs to visit the station, and the Repairman fills in the missing data so weather reports don't have gaps!

---

### Step 14: Tell the AI to Build the Cloud Services
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this prompt:

```text
Build the full Cloud Analytics Layer in the FastAPI backend:
1. Create `backend/services/confluence_engine.py`:
   - Loads model_a_weather.pkl and model_b_defect.pkl.
   - Evaluates:
     - High Weather + Low Defect -> "Natural Weather Event" (No Alarm!)
     - Low Weather + High Defect -> "Sensor Defect" (Alarm Raised!)
     - High Weather + High Defect -> "Compound Event" (Warning!)
   - Calculates Confidence Score: max(P(Defect), P(Weather)) * (1.0 - abs(P(Defect)-P(Weather))*0.20).
2. Create `backend/services/predictive_maintenance.py`:
   - Tracks long-term EWMA drift.
   - When drift exceeds 2.0 sigma, sets status to "At Risk" and estimates days until recalibration.
3. Create `backend/services/imputation_engine.py`:
   - If a sensor defect is confirmed, calculates the true expected value from healthy sensors.
4. Update `backend/services/telemetry_ingestion.py` so every 1-second packet passes through:
   Rule Check -> Reconstruction Error -> Dual-Model Confluence -> Maintenance -> Imputation.
   Broadcasts everything across the SSE stream to the frontend.
```
- [ ] *Done!*

### Step 15: Test It!
1. In your terminal, run:
   ```powershell
   python -c "from services.confluence_engine import confluence_engine; res = confluence_engine.evaluate_confluence(0.05, 0.94, 'capacitive_drift'); print('Confluence Test Result:', res)"
   ```
2. 👀 **What success looks like:** Terminal prints:  
   `Confluence Test Result: {'classification': 'Sensor Defect', 'confidence_score': 92.1, 'severity': 'High', 'operator_alert': True}`
- [ ] *Done!*

---

## 🟢 STAGE 6: Setting Up Laptop 1 (The Weather Station Transmitter)

### 🎯 The Goal:
Turn Laptop 1 into the physical weather station in the field that transmits live data and lets us press keyboard buttons on camera to break sensors live!

### 🧠 Why are we doing this? (The Analogy)
During your hackathon video, you need to prove to the judges that the system works in real time. Laptop 1 is the transmitter. When you press `2`, you inject humidity drift. When you press `3`, you simulate a thunderstorm. The judges will watch Laptop 2 react live!

---

### Step 16: Tell the AI to Build the Transmitter Program
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this prompt:

```text
Update `backend/simulator/client.py` for Laptop 1:
- Connects over MQTT to --host on port 1883.
- Sends weather data every 1.0 second for station AGRA-01.
- Maintains an internal 2-hour circular ring buffer (120 samples).
- Keyboard chaos keys:
  '1' -> Heat Spike (+8°C instant jump)
  '2' -> Capacitive Drift (+15% humidity bias)
  '3' -> Severe Thunderstorm (-11 hPa drop, 94% humidity, -8°C cool)
  '4' -> Frozen Sensor (humidity flatlines at 84%)
  '0' -> Reset to Normal Baseline
- When a fault is pressed, sends an Incident Burst containing the trigger packet + past 12 context readings.
- Prints clean color-coded status lines in the terminal.
```
- [ ] *Done!*

### Step 17: Run Laptop 1
1. On **Laptop 1**, open terminal:
   ```powershell
   pip install paho-mqtt
   python backend/simulator/client.py --host <YOUR_VM_PUBLIC_IP>
   ```
2. 👀 **What success looks like:** Every second, terminal logs:  
   `[TX SEQ #1042] -> AGRA-01: Temp=32.4°C | Humidity=58.1% | Pressure=1005.2 hPa | Mode=NORMAL`
- [ ] *Done!*

---

## 🟢 STAGE 7: Setting Up Laptop 2 (The 3D Control Screen)

### 🎯 The Goal:
Turn Laptop 2 into the IMD Control Room dashboard with an animated 3D weather station and clean tabs for Confluence, SHAP, Maintenance, and Imputation.

### 🧠 Why are we doing this? (The Analogy)
A dashboard with 20 confusing charts will overwhelm the judges. Instead, we use clean tabs:
- **Tab 1 (Live ML & Confluence):** Shows the red line and the decision badge (`Sensor Defect | 92.4% Confidence`).
- **Tab 2 (Explainable AI):** Shows the SHAP bar chart explaining *why* humidity is the culprit.
- **Tab 3 (Maintenance):** Shows the Doctor's warning: *"Calibration due in < 2 Weeks"*.
- **Tab 4 (Data Repair):** Shows the suggested corrected value and an "Accept & Impute" button.
The 3D model stays on the left and smoothly flies right to the broken sensor!

---

### Step 18: Tell the AI to Build the Tabbed Screen
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this prompt:

```text
Update the Next.js frontend on Laptop 2:
1. Create `frontend/src/components/panels/ConfluenceAlertBanner.tsx`:
   - Shows bright alert badge:
     - Emerald Green: "Natural Weather Event (Zero False Alarm)"
     - Rose Red: "Sensor Defect Confirmed (Confidence: 92%)"
   - Mini gauges for Model A P(Weather) and Model B P(Defect).
2. Create `frontend/src/components/panels/PredictiveMaintenancePanel.tsx`:
   - Shows cumulative drift progress bar and countdown: "Calibration due in < 2 Weeks".
3. Create `frontend/src/components/panels/ImputationPanel.tsx`:
   - Shows Reported Bad Value (84.2%) vs Suggested Corrected Value (42.6%).
   - Clickable button: "Accept & Impute" to repair the data.
4. Update `frontend/src/app/page.tsx`:
   - Organize the right sidebar into 4 tabs:
     [Live ML & Confluence] | [XAI (SHAP)] | [Maintenance] | [Data Repair]
   - Ensure the 3D Digital Twin auto-zooms into the culprit sensor when a defect fires.
```
- [ ] *Done!*

### Step 19: Start Laptop 2
1. On **Laptop 2**, open terminal:
   ```powershell
   cd frontend
   npm run dev
   ```
2. Open Google Chrome $\to$ go to `http://localhost:3000` $\to$ Press `F11` for full screen.
3. 👀 **What success looks like:** You see the 3D weather station spinning smoothly, and the 4 tabs on the right side!
- [ ] *Done!*

---

## 🟢 STAGE 8: The 30-Minute Rehearsal (Testing Everything)

Put Laptop 1 and Laptop 2 side-by-side. Follow this test sequence:

| Step | What to do on Laptop 1 | What should happen on Laptop 2 | Verified? |
|---|---|---|---|
| **Test 1** | Laptop 1 runs normally | 3D twin is **Green**. Error score is $\sim 0.015$ (below threshold). | [ ] YES |
| **Test 2** | Press key `3` (Thunderstorm) | Pressure plunges, but station stays **GREEN**! Banner says: *"Natural Weather Event (96% Confidence) — Zero False Alarm!"* | [ ] YES |
| **Test 3** | Press key `2` (Drift) | Error climbs live, crosses the red line! Station turns **RED**! Camera smoothly auto-zooms into the humidity cylinder! | [ ] YES |
| **Test 4** | Click Tab 2 (SHAP) | Humidity bar shows 88% culprit with plain text reason. | [ ] YES |
| **Test 5** | Click Tab 3 (Maintenance) | Shows: *"Calibration due in < 2 Weeks"*. | [ ] YES |
| **Test 6** | Click Tab 4 (Data Repair) | Shows: `84.2% -> 42.6%`. Click *"Accept & Impute"*. | [ ] YES |
| **Test 7** | Press key `0` (Reset) | Station turns **Green** again and camera zooms back out! | [ ] YES |

---

## 🟢 STAGE 9: Recording the 5-Minute Video

### 🎬 How to Record:
1. Place both laptops side-by-side on a desk so a camera can see both screens, or use OBS Studio to record both laptop screens side-by-side.
2. Follow this exact script:

- **[0:00 - 0:45] Intro:**  
  *"Hello! This is SkyGuard AI. On Laptop 1, we emulate an Indian weather station. On Azure cloud, our AI models run in real time. On Laptop 2, our control room shows the live 3D digital twin."*
- **[0:45 - 1:45] The Storm Test (Zero False Alarms):**  
  *Press key [3] on Laptop 1.*  
  *"Watch: pressure drops by 11 hPa and humidity surges to 94%. Old systems sound false alarms during storms. But our station stays GREEN! Model A recognizes natural weather physics with 96% confidence. Zero false alarms!"*
- **[1:45 - 3:00] The Drift Test (The Real Detection):**  
  *Press key [2] on Laptop 1.*  
  *"Now we inject subtle capacitive drift. Watch the error curve climb tick-by-tick! It crosses our red threshold! The 3D twin turns RED, the camera auto-zooms into the humidity sensor, and our Confluence Judge confirms: Sensor Defect with 92% confidence!"*
- **[3:00 - 3:45] Explainability, Maintenance & Repair:**  
  *Click Tab 2 (SHAP): "Our AI explains why: 88% humidity attribution."*  
  *Click Tab 3 (Maintenance): "Our predictive maintenance engine warns us 2 weeks before total sensor failure."*  
  *Click Tab 4 (Repair): "And our imputation engine instantly corrects the corrupted reading from 84% back to 42%. We click Accept!"*
- **[3:45 - 4:30] Google Colab:**  
  *Show 30 seconds of your Colab charts: training loss curves and confusion matrices.*
- **[4:30 - 5:00] Conclusion:**  
  *"SkyGuard AI transforms India's meteorological network with explainable, split-edge intelligence. Thank you!"*
