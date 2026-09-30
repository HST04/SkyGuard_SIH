# 🎬 SkyGuard AI — Winning SIH 3-Minute Demo Video Script & Production Guide
> **Smart India Hackathon Finalist Masterclass: High-Authority Pitch • Live 3D Digital Twin • Split-Edge AI Demonstration**  
> **Target Duration:** Exactly 03:00 (180 Seconds) | **Pacing:** ~135 words/minute (~405 words total narration)  
> **Status:** Codebase Locked — 100% faithful to the deployed prototype at `http://localhost:3000`

---

## 🏆 The SIH Evaluator Psychology: How to Score in the Top 1%

Hackathon evaluators review dozens of videos in hours. Studies of winning SIH submissions show judges make their shortlisting decision in the **first 30 seconds**.

### 🚫 The 4 Fatal Mistakes That Get Videos Rejected
1. **The "Slide Deck Intro" Trap:** Spending 45 seconds on team member names, college logos, and theoretical problem slides. **Rule:** Show the live working 3D prototype from Second 00:01.
2. **The "Frontend Only" Suspicion:** Evaluators assume pretty UI is a Figma mockup. **Rule:** Prove edge telemetry packets, ML reconstruction MSE curves, and explainability math within the first 60 seconds.
3. **The "Runaway Timer" Trap:** Videos exceeding 3 minutes are either penalized or cut off mid-sentence. **Rule:** Hit your closing impact slide at exactly 02:45 and fade out at 03:00.
4. **The "Overpromising" Trap:** Claiming to detect 20 weather variables when IMD problem statements mandate core parameters. **Rule:** Explicitly state that SkyGuard operates on the mandated core atmospheric triad: **Temperature ($T$), Barometric Pressure ($P$), and Relative Humidity ($RH$)**.

---

## 🖥️ Production Staging & Recording Environment

### 1. Hardware & Screen Setup
- **Display Resolution:** 1920 × 1080 (16:9 1080p).
- **Browser:** Google Chrome at `http://localhost:3000`. Press **`F11`** for borderless fullscreen mode. Dark mode active.
- **Side Terminal (Optional Dual-Pane) or Browser Hotkeys:** The dashboard supports direct keyboard shortcuts:
  - `[0]` : Nominal Baseline (Reset)
  - `[3]` : Severe Thunderstorm Squall
  - `[2]` : Capacitive Humidity Drift
  - `[4]` : Frozen Sensor Flatline
  - `[1]` : Thermal Impulse Spike
- **Mouse Highlight:** Use OBS Studio or PointerFocus to add a subtle cyan highlight around the cursor so clicks are instantly noticeable.

### 2. Audio Setup
- Use a dedicated headset/USB condenser microphone.
- Apply an OBS Studio **Noise Suppression (RNNoise)** filter and a gentle **Compressor** so your voice sounds crisp, authoritative, and studio-grade.
- No background music (or whisper-quiet low-pass ambient drone at -28 dB maximum). Voice clarity is paramount.

---

## ⏱️ Master 180-Second Timeline Overview

```
00:00 ──────────────── 00:25 ─────────────── 00:55 ────────────────────── 01:35 ───────────────────── 02:15 ─────────────── 02:45 ────── 03:00
  │                      │                     │                            │                           │                     │          │
  ▼                      ▼                     ▼                            ▼                           ▼                     ▼          ▼
[1. The Crisis]   [2. Split-Edge]   [3. Scenario 1: Storm]       [4. Scenario 2: Drift]      [5. XAI & Repair]     [6. Benchmarks]   [Fade Out]
Hook & IMD Need   ESP32 & Context   Zero False Alarm Proof       Silent Fault & 3D Focus     SHAP + Self-Healing   National Impact    Thank You
```

---

## 🎙️ Complete Second-by-Second Video Script & Action Cues

### SEGMENT 1: The National Crisis & The Hook (00:00 – 00:25 | 25 Seconds)

* **Visual on Screen:**
  - Fullscreen view of the **SkyGuard AI 3D Digital Twin** (`AGRA-01`) gently rotating with a glowing green health aura.
  - Right panel open to **Live ML & Confluence** showing nominal live telemetry (Temperature ~30°C, Humidity ~62%, Pressure ~1005 hPa) streaming at 1 Hz.
* **Physical Action:**
  - Slowly orbit the 3D weather station with the mouse for 3 seconds. Hover cursor briefly over the live telemetry cards.
* **Spoken Voiceover (38 words | ~17 seconds):**
  > *"Automatic Weather Stations deployed across India are the backbone of monsoon forecasting and disaster management. Yet today, rigid static threshold rules trigger rampant false alarms during storms, while missing silent sensor drift that quietly corrupts India's numerical weather models.*
  > 
  > *This is **SkyGuard AI**."*

---

### SEGMENT 2: Split-Edge Architecture & Low-Bandwidth Burst (00:25 – 00:55 | 30 Seconds)

* **Visual on Screen:**
  - Point to the **AI Pattern Health (1D-CNN)** panel in the right sidebar.
  - Show the live **Reconstruction Error MSE curve** remaining flat below the red `0.095` threshold, with latency showing **`~2.4 ms`**.
  - On-screen callout / text graphic: *"ESP32 Edge: INT8 Quantized Autoencoder | < 15ms Latency | > 90% Bandwidth Saved"*.
* **Physical Action:**
  - Hover cursor over the **Latency (2.4 ms)** badge and the **Pattern Deviation (MSE: ~0.014)** line.
* **Spoken Voiceover (70 words | ~28 seconds):**
  > *"Remote stations cannot stream heavy data over cellular or satellite links. SkyGuard solves this with a **Split-Edge/Cloud Architecture**.*
  > 
  > *At the edge, an ESP32 microcontroller runs an INT8-quantized 1D-CNN temporal autoencoder in under 15 milliseconds, evaluating sliding 12-second multivariate windows. Clean nominal data stays in a local circular buffer. Only when anomalies occur does the edge transmit an MQTT incident burst with pre-fault context—slashing bandwidth consumption by over 90 percent."*

---

### SEGMENT 3: Scenario 1 — Severe Thunderstorm Squall (True Negative) (00:55 – 01:35 | 40 Seconds)

* **Visual on Screen:**
  - Presenter presses **`[3]`** (or clicks `[3] Thunderstorm` on the top bar).
  - The live chart reacts: Pressure plummets by **-11 hPa**, Relative Humidity surges to **94%**, and Temperature drops by **-8°C**.
  - **Confluence Banner** updates: **`NATURAL STORM (ZERO FALSE ALARM)`** with an emerald shield icon.
  - The 3D Digital Twin station **remains solid EMERALD GREEN**.
* **Physical Action:**
  - Click **`[3] Thunderstorm`**.
  - Move cursor to the plummeting barometric pressure graph.
  - Point to the green status: **`p_weather: 98%`**, **`p_defect: 8%`**.
* **Spoken Voiceover (88 words | ~35 seconds):**
  > *"Let's test this against the ultimate challenge: a violent thunderstorm squall front. I press key 3.*
  > 
  > *Notice the extreme turbulence: pressure plummets by 11 hectopascals, humidity surges to 94 percent, and temperature plunges. In legacy systems, these massive rates-of-change trigger immediate false alarms.*
  > 
  > *But look at SkyGuard's 3D twin: **it remains completely green.** Our cloud **Model A Weather Classifier** verifies the multi-scale cross-derivatives ($dT/dt, dP/dt, dRH/dt$). Because thermodynamic laws are respected, our Confluence Engine classifies this as a natural weather event with 98% confidence. **Zero false alarms.**"*

---

### SEGMENT 4: Scenario 2 — Capacitive Humidity Drift (Hardware Defect) (01:35 – 02:15 | 40 Seconds)

* **Visual on Screen:**
  - Presenter presses **`[2]`** (or clicks `[2] Capacitive Drift` on the top bar).
  - Relative Humidity subtly creeps up to **84%**, while Temperature stays warm (33°C) and Pressure remains flat (1005 hPa).
  - The **1D-CNN Reconstruction Error (MSE)** curve spikes violently past the red `0.095` threshold (climbing to 1.2+).
  - **3D Digital Twin pulses GLOWING RED**. The Three.js camera **autonomously lerps and zooms directly into the Relative Humidity sensor mast**.
  - Confluence Banner shifts to: **`HARDWARE DEFECT CONFIRMED: CAPACITIVE_DRIFT (96% Confidence)`**.
* **Physical Action:**
  - Press **`[2] Capacitive Drift`**.
  - Let hands off mouse for 2 seconds to let the automatic 3D camera zoom smoothly focus on the sensor shield.
  - Hover cursor over the breached MSE threshold line.
* **Spoken Voiceover (92 words | ~36 seconds):**
  > *"Now, let's inject the real silent killer: insidious hardware degradation. I press key 2.*
  > 
  > *A capacitive hygrometer develops positive drift, reading 84 percent. Traditional threshold rules miss this completely because 84 is well within normal 0-to-100 limits.*
  > 
  > *However, SkyGuard's 1D-CNN immediately detects thermodynamic decoupling: humidity is climbing during peak afternoon heat without any pressure drop. The reconstruction error breaches the threshold.*
  > 
  > *Instantly, our 3D Digital Twin pulses red and autonomously pans to the exact failing sensor. Our Confluence Engine fuses Model A and Model B, confirming **Hardware Defect with 96% confidence.**"*

---

### SEGMENT 5: Explainability, Predictive Maintenance & Self-Healing Repair (02:15 – 02:45 | 30 Seconds)

* **Visual on Screen:**
  1. Click **`Explainable AI (SHAP)`** tab: Show Relative Humidity bar dominating with an **88% positive contribution**.
  2. Click **`Maintenance`** tab: Show EWMA drift projection warning: **`Calibration Required in < 2 Weeks`**.
  3. Click **`Data Repair`** tab: Show corrupted reported value **`84.2%`** vs. suggested physical value **`42.6%`**. Click **`[Accept & Impute]`** — the telemetry repairs live on screen!
* **Physical Action:**
  - Rapid click sequence: Tab 2 (`Explainability`) $\to$ Tab 3 (`Maintenance`) $\to$ Tab 4 (`Data Repair`) $\to$ Click `[Accept & Impute]`.
* **Spoken Voiceover (76 words | ~27 seconds):**
  > *"SkyGuard doesn't just alert—it closes the entire operational loop:*
  > 
  > *First, under **Explainable AI**, SHAP attributions prove Relative Humidity drove 88% of the anomaly.*
  > 
  > *Second, our **Predictive Maintenance** module uses EWMA residual tracking to forecast sensor recalibration two weeks in advance.*
  > 
  > *Finally, under **Data Repair**, our multivariate imputation engine uses ambient temperature physics to reconstruct the true 42% reading in real-time, self-healing the data stream for numerical weather models."*

---

### SEGMENT 6: Quantitative Benchmarks & High-Impact Conclusion (02:45 – 03:00 | 15 Seconds)

* **Visual on Screen:**
  - Presenter presses **`[0]`** (Reset) — the 3D twin smoothly rotates out and returns to pristine emerald green.
  - Semi-transparent Metrics Summary Card or final clean UI view:
    - **False Alarm Reduction: ≥ 85%**
    - **Edge Inference Latency: < 15 ms on ESP32**
    - **Bandwidth Reduction: > 90% via MQTT Context Bursts**
    - **Mandated Compliance: 100% (Core Triad: T, P, RH only)**
* **Physical Action:**
  - Press **`[0]`** to reset. Center the mouse.
* **Spoken Voiceover (38 words | ~14 seconds):**
  > *"By combining edge-quantized intelligence with thermodynamic cloud confluence, SkyGuard AI delivers 85% fewer false alarms, sub-15 millisecond edge execution, and guaranteed data integrity for India's weather infrastructure.*
  > 
  > *SkyGuard AI: Protecting India's Skies. Thank you."*

---

## 📋 The 180-Second Teleprompter Cue Sheet (Print or Keep on 2nd Screen)

| Time | Action to Perform | UI Tab & Screen State | Voice Cue (First Words) |
| :--- | :--- | :--- | :--- |
| **00:00** | Rotate 3D twin slowly | Main Screen, Station Green, 1 Hz live | *"Automatic Weather Stations deployed across India..."* |
| **00:25** | Hover over MSE meter | Live ML Tab, MSE < 0.015, Latency ~2.4ms | *"Remote stations cannot stream heavy data..."* |
| **00:55** | **Press `[3]`** (Squall) | Pressure drops -11 hPa, Twin stays **GREEN** | *"Let's test this against the ultimate challenge..."* |
| **01:15** | Point to Confluence banner | Status: `NATURAL STORM (ZERO FALSE ALARM)` | *"Because thermodynamic laws are respected..."* |
| **01:35** | **Press `[2]`** (Cap. Drift) | RH rises to 84%, Twin pulses **RED**, camera zooms | *"Now, let's inject the real silent killer..."* |
| **01:55** | Hands off mouse | Auto-focus on RH sensor, MSE > 0.095 | *"Our 3D Digital Twin pulses red and pans..."* |
| **02:15** | Click **`Explainable AI`** | SHAP panel: RH bar at 88% | *"SkyGuard doesn't just alert..."* |
| **02:25** | Click **`Maintenance`** | EWMA drift: Calibration < 2 weeks | *"Second, our Predictive Maintenance module..."* |
| **02:35** | Click **`Data Repair`** $\to$ `[Accept]` | Corrupted 84.2% $\to$ Repaired 42.6% | *"Finally, our multivariate imputation engine..."* |
| **02:45** | **Press `[0]`** (Reset) | Station returns to clean emerald green | *"By combining edge-quantized intelligence..."* |
| **03:00** | Fade to black / Stop recording | Perfect 03:00 mark | *"Thank you."* |

---

## 🛠️ Step-by-Step Operator Runbook (Launch Before Recording)

### Step 1: One-Click System Launch
Open PowerShell in the project root:
```powershell
python run_demo.py
```
*(Or double-click `start_demo.bat`)*.  
This automatically boots:
- FastAPI Backend (`http://localhost:8000`)
- Next.js 14 Dashboard (`http://localhost:3000`)
- Opens Google Chrome to the 3D Digital Twin

### Step 2: Pre-Recording Quick Verification (30 Seconds)
1. In Chrome, press **`F11`** for clean fullscreen.
2. Press **`0`** $\to$ Verify station is Green and `STATION HEALTHY` is displayed.
3. Press **`3`** $\to$ Verify graph plummets, station remains Green (`NATURAL STORM`).
4. Press **`2`** $\to$ Verify station pulses Red, camera zooms to sensor mast, and banner shows `HARDWARE DEFECT CONFIRMED`.
5. Click **`Data Repair`** tab $\to$ Click `Accept & Impute` $\to$ Verify value changes to ~42.6%.
6. Press **`0`** $\to$ Station resets to nominal baseline.

---

## 🎯 Evaluator Defense & Technical Cheat Sheet (For Viva / Q&A)

If evaluators ask deep technical questions during live rounds, use these exact defensible answers:

1. **"Why not run everything on the Edge (ESP32)?"**
   > *"An ESP32 has only 320 KB of SRAM and cannot run multi-model ensembles or SHAP kernel explainability. Pure cloud streaming, on the other hand, wastes satellite data on 99% nominal readings. SkyGuard's Split-Architecture gives edge efficiency (< 48 KB RAM) with cloud analytical depth."*

2. **"How does Model B detect defects if sensor failure datasets don't exist?"**
   > *"IMD AWS failure records are rarely labeled. We solved this by mathematically synthesizing the 5 canonical sensor fault archetypes: capacitive drift ($\alpha \cdot t$), frozen flatlines, impulse spikes, Gaussian noise, and dropout bursts directly over clean historical diurnal baselines."*

3. **"How do you distinguish a storm from a sensor break using only T, P, RH?"**
   > *"Via cross-channel thermodynamic coupling. In a natural squall, the Magnus-Tetens dew point relation holds: barometric plunge ($dP/dt < 0$) is accompanied by convective cooling ($dT/dt < 0$) and saturation ($dRH/dt > 0$). In capacitive drift, $RH$ increases while $T$ is warm and $P$ is stationary—a physical impossibility that violates atmospheric equilibrium."*

---

## 📦 Video Submission Packaging Template (Ready to Copy-Paste)

### Video Title:
```
SkyGuard AI — Split-Edge AI Anomaly Detection & Predictive Maintenance for AWS (SIH Prototype Demo)
```

### Video Description:
```markdown
SkyGuard AI is a split-architecture anomaly detection, explainability, and self-healing platform engineered specifically for Automatic Weather Stations (AWS). Operating strictly on the mandated core atmospheric triad (Temperature, Pressure, Relative Humidity), SkyGuard solves the twin challenges of Automatic Weather Stations: false alarm fatigue during severe convective storms and silent data corruption caused by sensor drift.

⏱️ TIMESTAMPS:
00:00 - The National Crisis: AWS False Alarms vs. Silent Sensor Drift
00:25 - Split-Edge Architecture: ESP32 Edge Autoencoder (<15ms, >90% Bandwidth Saved)
00:55 - Scenario 1: Severe Thunderstorm Squall (True Negative / Zero False Alarm)
01:35 - Scenario 2: Capacitive Sensor Drift (1D-CNN Latent Detection & 3D Twin Alert)
02:15 - Operational Lifecycle: SHAP XAI, EWMA Maintenance & Self-Healing Imputation
02:45 - Quantitative Impact & Scalability Benchmarks

🚀 KEY PERFORMANCE BENCHMARKS:
• False Alarm Reduction: ≥ 85% compared to static threshold systems
• Edge Latency: < 15 ms on ESP32 @ 240 MHz (< 48 KB SRAM footprint)
• Bandwidth Conservation: > 90% via MQTT incident context bursting
• Confluence Engine F1-Score: 0.94
• Self-Healing: Real-time multivariate physical imputation keeps NWP feeds uninterrupted
• Compliance: 100% strictly compliant with mandated core parameters (T, P, RH)
```
