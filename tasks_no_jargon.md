# 📖 SkyGuard AI — Step-by-Step Implementation Guide

**Overview:**  
A step-by-step guide to set up, run, test, and record the SkyGuard AI two-laptop demonstration.  
Follow the numbered steps in order. Copy-paste the AI prompts into your AI assistant, complete the setup steps, and run the test commands.

---

## 🗺️ Visual Map of How Everything Connects

```
   [LAPTOP 1: Weather Station]
         │ (Sends weather data every second)
         ▼
   [AZURE CLOUD SERVER]
         ├── Saves data to Supabase Database (so it never gets lost)
         └── Runs our AI Model (checks if sensors are broken)
         │
         ▼ (Sends live alerts)
   [LAPTOP 2: 3D Control Screen]
         └── Shows the 3D weather station turning Red when a sensor breaks!
```

---

## 🟢 STAGE 1: Setting Up the Database (Saving Our Data)

*Goal: Give our project a cloud database so readings and alerts don't get erased when computers turn off.*

### Step 1: Create a Free Supabase Account
1. Open your browser and go to: **[supabase.com](https://supabase.com)**
2. Click the green button: **Start your project** (sign in with your GitHub or Google account).
3. Click **New Project**.
4. Set:
   - **Name:** `skyguard-db`
   - **Database Password:** Pick any simple password you won't forget (e.g., `SkyGuard2026!`). Write it down!
   - **Region:** Pick the one closest to you (e.g., `Central India` or `East US`).
5. Click **Create new project** and wait ~1 minute for it to finish setting up.
- [ ] *Done!*

### Step 2: Copy the Database Link
1. In your Supabase project, click the ⚙️ **Project Settings** icon on the bottom left.
2. Click **Database** on the left menu.
3. Scroll down to **Connection string** and click the **URI** tab.
4. Copy the long link shown. It looks like this:  
   `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxx.supabase.co:5432/postgres`
5. Replace `[YOUR-PASSWORD]` with the password you made in Step 1.
- [ ] *Done!*

### Step 3: Tell the AI to Connect the Code to the Database
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this **exact prompt**:

```text
Please connect our FastAPI backend to our new Supabase database:
1. Create a file `backend/data/db.py` that connects to DATABASE_URL from our .env file.
2. Define three tables:
   - telemetry_records (to store weather readings: temperature, humidity, pressure, wind, time)
   - anomaly_events (to store alerts when a sensor breaks, severity, and culprit sensor)
   - operator_feedback (to store when a human clicks "False Alarm" or "Resolve")
3. Update `backend/data/store.py` so whenever new data comes in, it saves to Supabase in the background.
4. Update `backend/requirements.txt` to include: sqlalchemy>=2.0.0, asyncpg>=0.29.0, aiosqlite>=0.19.0.
5. Create a `backend/.env` file with: DATABASE_URL=<PASTE_YOUR_DATABASE_LINK_HERE>
```
*(Remember to put your real database link from Step 2 at the bottom!)*
- [ ] *Done!*

### Step 4: Test That the Database Works
1. Open your terminal / command prompt.
2. Run this command:
   ```powershell
   cd backend
   python -c "import asyncio; from data.db import init_db; asyncio.run(init_db()); print('SUCCESS: Database is working!')"
   ```
3. **What you should see:** The terminal prints:  
   `SUCCESS: Database is working!`
4. In your Supabase browser tab, click **Table Editor** on the left. You should see `telemetry_records` and `anomaly_events` tables appear!
- [ ] *Done!*

---

> 💡 **Why did we do Stage 1?**  
> In our old MVP, all data lived only in computer RAM. If the server restarted, everything vanished. Now, every single weather reading and alert is safely saved in the cloud. Even if the server restarts, our data is safe!

---

## 🟢 STAGE 2: Setting Up the Cloud Server (The Brain on the Internet)

*Goal: Get a free virtual computer on Microsoft Azure that will run 24/7 on the internet.*

### Step 5: Create a Free Virtual Machine on Azure
1. Go to **[portal.azure.com](https://portal.azure.com)** and sign in with your student email.
2. In the top search bar, type `Virtual Machines` and click on it.
3. Click **Create** $\to$ **Azure virtual machine**.
4. Fill in these settings:
   - **Subscription:** Azure for Students (uses your free $100 student credit)
   - **Resource group:** Click *Create new* and type `rg-skyguard`
   - **Virtual machine name:** `skyguard-vm`
   - **Region:** Pick closest to you (e.g., `Central India` or `East US`)
   - **Image:** Choose **Ubuntu Server 22.04 LTS**
   - **Size:** Choose **Standard_B2s** (2 CPUs, 4 GB RAM — this costs only ~$1/day from your $100 free student grant)
   - **Authentication type:** Choose **SSH public key**
   - **Key pair name:** `skyguard-key`
5. Click **Review + create** at the bottom, then click **Create**.
6. A popup will ask you to download the private key. Click **Download private key and create resource**. Save the file (`skyguard-key.pem`) to your computer!
- [ ] *Done!*

### Step 6: Open the Internet Doors (Ports)
1. In the Azure portal, open your newly created virtual machine `skyguard-vm`.
2. On the left menu, click **Networking** (or **Network settings**).
3. Click the blue button: **Add inbound port rule**.
4. Fill in:
   - **Destination port ranges:** `1883,8000,22`
   - **Protocol:** `Any`
   - **Action:** `Allow`
   - **Name:** `Allow_SkyGuard`
5. Click **Add**.
6. Look at the overview page of your VM and copy your **Public IP address** (e.g. `20.120.45.67`). Write this down!
- [ ] *Done!*

### Step 7: Log Into the Server and Start the Software
1. Open PowerShell or Terminal on your computer.
2. Connect to the Azure server by running:
   ```powershell
   ssh -i "path\to\skyguard-key.pem" azureuser@<YOUR_PUBLIC_IP>
   ```
   *(Type `yes` if it asks about fingerprint)*.
3. Once you see the green `azureuser@skyguard-vm:~$` prompt, copy and paste this **single command**:
   ```bash
   sudo apt-get update && sudo apt-get install -y docker.io docker-compose git
   git clone https://github.com/<YOUR_GITHUB_USERNAME>/SkyGuard_SIH.git && cd SkyGuard_SIH
   sudo docker-compose up -d --build
   ```
   *(Replace `<YOUR_GITHUB_USERNAME>` with your real GitHub username!)*
- [ ] *Done!*

### Step 8: Test That the Server is Alive
1. Open Google Chrome on your laptop.
2. In the address bar, type: `http://<YOUR_PUBLIC_IP>:8000/health`
3. **What you should see:** A clean web page saying:
   ```json
   { "status": "healthy", "service": "SkyGuard AI - AWS Anomaly Detection Engine" }
   ```
- [ ] *Done!*

---

> 💡 **Why did we do Stage 2?**  
> We now have an actual cloud server running on the internet! Laptop 1 (the weather station) can now send data to this IP address from anywhere in the world, and Laptop 2 can connect to it to see the 3D twin.

---

## 🟢 STAGE 3: Creating the Weather Data (Training Materials for the AI)

*Goal: Generate realistic fake Indian weather data so our AI can learn what "normal" weather looks like.*

### Step 9: Tell the AI to Write the Fake Weather Generator
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this **exact prompt**:

```text
Please create a Python script `scripts/generate_dataset.py` that generates weather data for our Agra weather station:
1. Make a normal weather dataset saved to `data/train_baseline_normal.csv`:
   - 10,000 rows representing 10-minute intervals.
   - Temperature goes up during the day (peaks at 36°C around 2 PM) and cools at night (24°C).
   - Humidity moves OPPOSITE to temperature (dry in the afternoon ~45%, humid in the morning ~80%).
   - Pressure stays around 1005 hPa.
2. Make a test dataset saved to `data/test_fault_injections.csv` that contains labeled anomalies:
   - Clean weather periods (labeled 'normal')
   - Severe thunderstorms with sharp pressure drops and rain (labeled 'valid_squall')
   - Broken sensor: +15% humidity drift while temperature is hot (labeled 'capacitive_drift')
   - Instant heat spikes: +8°C jump in 10 minutes (labeled 'heat_spike')
3. Print out a confirmation that the data is physically realistic (temperature and humidity have negative correlation).
```
- [ ] *Done!*

### Step 10: Run the Generator
1. In your terminal, run:
   ```powershell
   python scripts/generate_dataset.py
   ```
2. **What you should see:** The terminal prints:  
   `Generated 10000 rows of normal weather. T-RH Correlation: -0.82. Datasets saved in data/ folder!`
3. Check your project: verify that `train_baseline_normal.csv` and `test_fault_injections.csv` exist inside the `data` folder.
- [ ] *Done!*

---

> 💡 **Why did we do Stage 3?**  
> An AI cannot know if a sensor is broken unless it first learns what healthy weather looks like. In real weather, when temperature goes UP, relative humidity goes DOWN. Our generated dataset teaches this exact rule to the AI!

---

## 🟢 STAGE 4: Training the AI Brain in Google Colab (Free Google GPU)

*Goal: Train the AI to recognize normal weather patterns and download the finished brain file (`autoencoder.onnx`).*

### Step 11: Tell the AI to Write the Colab Notebook
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this **exact prompt**:

```text
Please create a Jupyter notebook at `notebooks/02_train_autoencoder.ipynb` to train our weather anomaly AI in Google Colab:
1. Load `train_baseline_normal.csv`.
2. Group the data into rolling windows of 12 timesteps (representing 2 hours of history).
3. Train a lightweight 1D-CNN Autoencoder:
   - The AI tries to reconstruct normal weather windows.
   - If weather is normal, reconstruction error (MSE) will be very low (< 0.02).
   - If a sensor drifts or breaks, reconstruction error will shoot up high (> 0.042).
4. Export the trained model to `autoencoder.onnx` (file size must be under 500 KB).
5. Export the feature scale numbers to `scaler.json`.
6. Generate 3 clear charts:
   - Chart 1: Training loss curve (shows AI learning).
   - Chart 2: Normal error vs Broken sensor error (shows the clear detection gap).
   - Chart 3: Correlation heatmap.
```
- [ ] *Done!*

### Step 12: Run the Training on Google Colab
1. In your web browser, go to: **[colab.research.google.com](https://colab.research.google.com)**
2. Click **Upload** and choose `notebooks/02_train_autoencoder.ipynb`.
3. In Colab, click the 📁 **Folder icon** on the left sidebar. Drag and drop both CSV files (`train_baseline_normal.csv` and `test_fault_injections.csv`) into that folder.
4. Click the top menu: **Runtime** $\to$ **Run all**.
5. Wait ~1 minute while it trains.
6. Look at the graphs: you will see the loss go down, and you will see the broken sensor error spike into the red zone!
7. In the left folder tab, right-click and **download**:
   - `autoencoder.onnx`
   - `scaler.json`
8. Move those two downloaded files into your project folder at: `backend/ml_artifacts/`.
- [ ] *Done!*

### Step 13: Check That the Model File is Valid
1. In your laptop terminal, run:
   ```powershell
   python -c "import os; assert os.path.exists('backend/ml_artifacts/autoencoder.onnx'); print('SUCCESS: AI Brain file is ready! Size:', os.path.getsize('backend/ml_artifacts/autoencoder.onnx'), 'bytes')"
   ```
2. **What you should see:** Terminal prints:  
   `SUCCESS: AI Brain file is ready! Size: 148290 bytes`
- [ ] *Done!*

---

> 💡 **Why did we do Stage 4?**  
> We now have a trained AI brain file (`autoencoder.onnx`). It weighs less than 1 Megabyte, so it can run super fast on any computer or cloud server without needing expensive graphics cards!

---

## 🟢 STAGE 5: Making the Cloud Server Run the AI in Real Time

*Goal: Make the Azure cloud server run our AI on every incoming weather packet every single second.*

### Step 14: Tell the AI to Connect the Model to the Live Stream
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this **exact prompt**:

```text
Please update the FastAPI backend so it runs our `autoencoder.onnx` model on every incoming reading:
1. In `backend/services/anomaly_detector.py`:
   - Load `backend/ml_artifacts/autoencoder.onnx` using onnxruntime.
   - On every new 1-second weather reading, run the AI model.
   - Calculate the Reconstruction Error (MSE).
   - If MSE > 0.042, flag it as an ANOMALY.
   - Calculate which sensor caused the error (SHAP breakdown: Temperature, Humidity, or Pressure).
2. In `backend/services/mqtt_subscriber.py`:
   - Send both the weather reading AND the live AI error score across the SSE stream to connected dashboards.
3. Make sure `backend/requirements.txt` includes: onnxruntime>=1.16.0.
```
- [ ] *Done!*

### Step 15: Push the Code to the Cloud Server
1. In your local terminal, commit and push the new code to GitHub:
   ```powershell
   git add .
   git commit -m "feat: real-time ONNX AI detection"
   git push origin main
   ```
2. In your Azure VM terminal (via SSH), pull the latest code and restart:
   ```bash
   cd SkyGuard_SIH && git pull && sudo docker-compose up -d --build
   ```
3. Wait ~30 seconds for the containers to rebuild.
- [ ] *Done!*

---

> 💡 **Why did we do Stage 5?**  
> Now our cloud server doesn't just pass data through—it actively evaluates the data using our trained AI model every single second!

---

## 🟢 STAGE 6: Setting Up Laptop 1 (The Weather Station Transmitter)

*Goal: Turn Laptop 1 into the on-site weather station that beams data to the cloud.*

### Step 16: Tell the AI to Create the Transmitter Program
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this **exact prompt**:

```text
Create `backend/simulator/client.py` designed to run on Laptop 1 as our physical hardware emulator:
- Connects using MQTT to `--host` on port 1883.
- Sends a live weather packet every 1 second: Temperature, Humidity, Pressure, Wind, Solar.
- Has interactive keyboard keys so the presenter can inject faults live during the demo:
    Press '1' -> Injects Heat Spike (+8°C instant jump)
    Press '2' -> Injects Capacitive Drift (+15% humidity bias)
    Press '3' -> Simulates Severe Thunderstorm (Pressure drops -11 hPa, Humidity surges to 94%)
    Press '0' -> Resets back to Normal weather
- Prints clear output in the terminal:
  [TX SEQ #1042] Station AGRA-01: Temp=32.4°C | Humidity=58.2% | Status=NORMAL
```
- [ ] *Done!*

### Step 17: Test Laptop 1 Sending Data to the Cloud
1. On the **cloud server**, from the project root, start the demo MQTT broker:
   ```powershell
   docker compose up -d mqtt
   ```
   If the server uses a firewall or Azure network security group, allow inbound
   TCP port `1883` in addition to the API port `8000`.
2. On the cloud server, start the backend in external MQTT mode:
   ```powershell
   cd backend
   $env:MQTT_ENABLED="true"
   python main.py
   ```
   Confirm `http://<YOUR_PUBLIC_IP>:8000/health` reports
   `"mqtt_enabled": true` and `"edge_simulator_running": false`.
3. On **Laptop 1**, open PowerShell and install the MQTT library:
   ```powershell
   python -m pip install paho-mqtt
   ```
4. Start transmitting to your Azure cloud server:
   ```powershell
   python backend/simulator/client.py --host <YOUR_AZURE_PUBLIC_IP>
   ```
5. **What you should see:** Every second, a new line prints:
   `[TX SEQ #1001] Station AGRA-01: Temp=31.2°C | Humidity=62.1% | Status=NORMAL`
6. Press key `2` on your keyboard. You should see:
   `>>> FAULT INJECTED: CAPACITIVE DRIFT (+15% RH)`
7. Press key `0`. You should see:
   `>>> RESET TO NORMAL`
8. Press `1` to inject a heat spike or `3` to simulate a severe thunderstorm.
The transmitter reconnects automatically if the broker temporarily disappears.
Press `Ctrl+C` to stop it.
- [ ] *Done!*

---

> 💡 **Why did we do Stage 6?**  
> Laptop 1 is now completely decoupled and acts like real field hardware deployed in Agra, India, streaming data to our cloud server!

---

## 🟢 STAGE 7: Setting Up Laptop 2 (The 3D Control Screen)

*Goal: Make Laptop 2 show the live 3D Digital Twin and the real-time AI error meter.*

### Step 18: Tell the AI to Build the Live AI Error Meter
1. Open your AI coding assistant (Antigravity).
2. Copy and paste this **exact prompt**:

```text
Please update the Next.js frontend on Laptop 2:
1. Create `frontend/src/components/panels/LiveMLPipelinePanel.tsx`:
   - Shows a live real-time line chart of the AI's Reconstruction Error (MSE) updating every second.
   - Shows a clear red dashed line at Threshold: 0.042.
   - Shows current error number (e.g. 0.0152) and AI speed (e.g. 2.4 ms).
   - Shows a green pill "AI STATUS: NOMINAL" or flashing red pill "AI ALERT: DRIFT DETECTED".
2. Add this panel to `frontend/src/app/page.tsx` next to the 3D twin.
3. In `frontend/src/components/panels/ShapChart.tsx`, ensure the sensor percentage bars update live every second.
```
- [ ] *Done!*

### Step 19: Point Laptop 2 to the Cloud Server
1. On **Laptop 2**, open file `frontend/.env.local`.
2. Put your Azure VM public IP in these two lines:
   ```env
   NEXT_PUBLIC_API_URL=http://<YOUR_AZURE_PUBLIC_IP>:8000/api/v1
   NEXT_PUBLIC_STREAM_URL=http://<YOUR_AZURE_PUBLIC_IP>:8000/api/v1/telemetry/stream
   ```
3. In your terminal on Laptop 2, start the website:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
4. Open Google Chrome and go to: `http://localhost:3000`
5. Press **F11** on your keyboard to enter clean full-screen mode!
- [ ] *Done!*

---

> 💡 **Why did we do Stage 7?**  
> Laptop 2 is now our visual control room. It connects directly to the Azure server over the internet, receiving real-time AI updates and moving the 3D model!

---

## 🟢 STAGE 8: The Full Dry Run (Testing Everything Together)

*Goal: Verify that when you press a key on Laptop 1, Laptop 2 instantly reacts through the cloud!*

### Step 20: Run the 4-Minute Test Checklist

| What to Do | Where to Do It | What Should Happen on Screen | Result |
|---|---|---|---|
| **1. Start normal stream** | Laptop 1: press `0` | Laptop 2 shows 3D Twin is **GREEN**. Live AI Error line is low (~0.015). | [ ] Working |
| **2. Test a Storm** | Laptop 1: press `3` | Pressure drops and humidity rises, BUT 3D Twin stays **GREEN**! (Proves no false alarms on natural storms). | [ ] Working |
| **3. Inject Drift** | Laptop 1: press `2` | On Laptop 2, the AI error line shoots up, crosses the red threshold line, 3D Twin turns **RED**, and the camera zooms right into the humidity sensor! | [ ] Working |
| **4. Check Explanation** | Laptop 2 | The SHAP bar chart shows **Humidity: 88%** as the culprit. | [ ] Working |
| **5. Test Operator Button** | Laptop 2: click "False Alarm" | Alert status changes to "False Alarm", logged to Supabase. | [ ] Working |
| **6. Reset to Normal** | Laptop 1: press `0` | AI error line drops back to green, 3D station turns back to Green overview. | [ ] Working |

- [ ] *All 6 checks passed!*

---

> 💡 **Why did we do Stage 8?**  
> We have now proven that the entire hardware-to-cloud-to-AI-to-3D-dashboard pipeline works with zero errors. We are ready to record the video!

---

## 🟢 STAGE 9: Recording the 5-Minute Video

*Goal: Record a clean, impressive 5-minute video demonstrating the project to the judges.*

### Step 21: Setup the Recording
1. Place **Laptop 1** (showing the terminal) on the left side of a desk.
2. Place **Laptop 2** (showing the full-screen 3D dashboard) on the right side.
3. Open **OBS Studio** (or record with your phone camera on a steady tripod/books showing both screens).
4. Do a 10-second audio check to make sure your voice is loud and clear.
- [ ] *Done!*

### Step 22: Follow the 5-Minute Script

- **Minute 0:00 - 0:45: Introduction**
  - *Say:* "Welcome to SkyGuard AI. On Laptop 1, we are emulating on-site Automatic Weather Station hardware transmitting over MQTT. On our Azure cloud server, our 1D-CNN autoencoder processes each reading in real time. On Laptop 2, our IMD control room displays the live 3D digital twin."
  - *Point to screen:* Show the green 3D station and the live AI error line running at 0.015.

- **Minute 0:45 - 1:45: The Thunderstorm Test (True Negative)**
  - *Action:* On Laptop 1, press `3` (Severe Thunderstorm).
  - *Say:* "First, let's simulate a natural severe storm. Pressure drops by 11 hPa and humidity surges to 94%. But notice Laptop 2 stays GREEN! Our AI understands physics: during a storm, temperature and pressure move together naturally. Zero false alarms!"

- **Minute 1:45 - 3:00: Silent Sensor Drift (The AI Catch)**
  - *Action:* On Laptop 1, press `2` (Capacitive Drift).
  - *Say:* "Now, let's inject subtle sensor drift (+15% humidity). Traditional static rules fail because 75% humidity looks normal in isolation. But watch our real-time AI error meter on Laptop 2!"
  - *Point to screen:* Watch the line climb over 0.042. The 3D model turns RED, the camera auto-zooms to the humidity cylinder, and the SHAP chart shows Humidity at 88%!

- **Minute 3:00 - 3:45: Operator Feedback**
  - *Action:* On Laptop 2, click "Mark as False Alarm" or "Resolve".
  - *Say:* "The operator can triage alerts in one click. Every action logs the AI's latent vector into our cloud database, allowing the system to adapt over time without human code writing."

- **Minute 3:45 - 4:30: Data Science Depth (Google Colab)**
  - *Action:* Switch screen for 30 seconds to the Google Colab notebook.
  - *Say:* "Behind this is our 1D-CNN autoencoder trained in Google Colab. Here are our training curves and evaluation matrices showing a PR-AUC of over 0.92 on held-out weather test sets."

- **Minute 4:30 - 5:00: Conclusion**
  - *Say:* "SkyGuard AI: Self-healing, explainable, edge-to-cloud data integrity for India's meteorological network. Thank you!"
- [ ] *Video Recorded!*

---

## 🆘 Emergency Quick Fixes (If Anything Gets Stuck)

1. **"The 3D website on Laptop 2 says DISCONNECTED"**  
   - Make sure Laptop 1 is running `python client.py --host <IP>` so data is flowing.
   - Check that port 8000 is open in Azure Networking.
2. **"My Azure credits are draining"**  
   - In Azure Portal, click on `skyguard-vm` and click **Stop** when you are done for the day! Start it again before recording.
3. **"The internet is terrible / WiFi went down"**  
   - Run both Laptop 1 and Laptop 2 connected to a personal 4G/5G mobile phone hotspot. The data transmitted is tiny (< 5 KB per minute)!
4. **"I want to run everything locally without Azure"**  
   - Just open two terminal windows on one laptop:
     - Terminal 1: `cd backend; python main.py`
     - Terminal 2: `cd frontend; npm run dev`
   - Open `http://localhost:3000`. It will work completely offline!
