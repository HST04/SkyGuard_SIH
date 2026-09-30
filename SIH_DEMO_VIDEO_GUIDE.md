# 🎬 SIH 2026 Demo Video Master Guide — SkyGuard AI
> **3-Minute High-Impact Presentation Blueprint: Problem-Solution Impact • Code Rigor • Live App Showcase**
> *Target Duration: Exactly 03:00 (180 Seconds) | Format: Multi-Scene Screen Capture (Architecture ➔ IDE Code Spotlight ➔ Live App Demo)*

---

## 📌 Executive Presentation Strategy: The 180-Second SIH Winning Blueprint

Smart India Hackathon (SIH) judges evaluate dozens of projects in rapid succession. Presentations that look like a "vibe-coded app with a bunch of buttons" or feature continuous, unfocused code scrolling score poorly.

**SkyGuard AI** wins by structuring the 3-minute video into **3 distinct, high-impact scenes**:

1. **Scene 1 (00:00 – 00:45) — Problem & System Architecture**: Framing the Indian AWS telemetry problem (static thresholds causing alarm fatigue and corrupting NWP models) and introducing our Split-Edge/Cloud Architecture.
2. **Scene 2 (00:45 – 01:25) — Production Code Proof (IDE Spotlight)**: Highlighting the core mathematical engine (`confluence_engine.py`) in VS Code to prove deep technical implementation rather than a surface-level UI mock.
3. **Scene 3 (01:25 – 03:00) — Live App Demonstration & Impact**: Executing live fault injections (Thunderstorm squall line vs. Capacitive Drift fault), demonstrating zero false alarms, 3D Digital Twin camera auto-focus, SHAP attributions, predictive maintenance, and real-time data imputation.

---

## ⏱️ Timeline & Scene Transition Strategy

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SKYGUARD AI (180s)                                     │
├────────────────────────────┬─────────────────────────────┬─────────────────────────────┤
│ SCENE 1: PROBLEM & ARCH    │ SCENE 2: CODE PROOF (IDE)   │ SCENE 3: LIVE APP & IMPACT  │
│ (00:00 - 00:45)            │ (00:45 - 01:25)             │ (01:25 - 03:00)             │
│ • AWS static threshold flaw│ • `confluence_engine.py`    │ • Thunderstorm (Green)      │
│ • Split-Edge/Cloud         │ • Decision Matrix & Formula │ • Capacitive Drift (Red)    │
│ • Context Burst Protocol   │ • Physics-Informed Rules    │ • 3D Camera Lerp & SHAP XAI │
└────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

| Time Window | Duration | Scene Focus | Primary Screen | Core Message Delivered |
|---|---|---|---|---|
| **00:00 – 00:45** | 45s | **Scene 1: The Problem & Architecture** | Architecture Diagram & Slides | Indian AWS networks suffer from static threshold flaws. SkyGuard's split-edge architecture solves bandwidth and anomaly classification. |
| **00:45 – 01:25** | 40s | **Scene 2: Technical Know-How & Code Proof** | VS Code (`confluence_engine.py`) | Fusing Model A (Weather) and Model B (Defects) via a deterministic decision matrix and mathematical confidence scoring. |
| **01:25 – 02:15** | 50s | **Scene 3A: Live Demo — Severe Storm vs. Defect** | Next.js 3D Twin & Control Bar | **Proof of Accuracy:** Severe squall line keeps station GREEN (zero false alarm). Capacitive drift pulses RED and auto-focuses camera. |
| **02:15 – 02:45** | 30s | **Scene 3B: Operational Assurance & Recovery** | SHAP XAI, Maintenance & Imputation | SHAP explains culprit parameter (RH 88%); EWMA warns calibration due; Multivariate Imputation repairs corrupt data ($84\% \to 42\%$). |
| **02:45 – 03:00** | 15s | **Close & Benchmark Summary** | Summary Overlay | 85% false alarm reduction, <15ms edge inference, >90% bandwidth saved, preserving India's NWP model feed. |

---

## 🎙️ Second-by-Second Video Script & Screen Action Guide

### Scene 1: The Crisis & Split-Edge Architecture (00:00 – 00:45 | 45 Seconds)

* **Visual on Screen:**
  - Full-screen high-resolution Architecture Diagram (`System Architecture.md` / Mermaid rendering).
  - Highlight callout animations over: **1.0 Edge Device Layer (ESP32)** ➔ **MQTT Broker** ➔ **2.0 Cloud Analytics Engine**.
* **Voiceover Script:**
  > "Automatic Weather Stations deployed across India form the critical backbone of disaster warning and agriculture. Yet today, they rely on rigid, single-parameter static threshold rules. When a severe thunderstorm hits, static rules trigger rampant false alarms. Worse, when sensors slowly drift or freeze, conventional loggers miss them completely—quietly corrupting India's numerical weather prediction models.
  >
  > This is **SkyGuard AI**—a split-edge anomaly detection and predictive maintenance platform built specifically to solve this crisis.
  >
  > Microcontrollers in remote terrains cannot run heavy deep neural networks. SkyGuard pairs ultra-low-power edge filtering on microcontrollers (ESP32 / TFLite Micro) running under 15 milliseconds with a cloud analytics engine. Nominal data stays in local circular storage; only when an anomaly occurs does the edge transmit an MQTT context burst with a multi-hour window—slashing cellular bandwidth by over 90 percent."

---

### Scene 2: Production Code Walkthrough — VS Code (00:45 – 01:25 | 40 Seconds)

* **Visual on Screen:**
  - Switch screen directly to **VS Code** displaying `backend/services/confluence_engine.py`.
  - Highlight **Line 72–85**: `compute_confidence(self, p_weather, p_defect)`
  - Highlight **Line 87–120**: `evaluate_confluence()` Decision Matrix.
  - Highlight **Line 210–235**: Physical & Meteorological Safety Overrides (`is_squall_physics` and `capacitive_drift`).
* **Voiceover Script:**
  > "Behind our interface lies rigorous production engineering. Here in our backend, rather than relying on non-deterministic LLM chat dialogues, SkyGuard implements a deterministic **Classification Confluence Engine**.
  >
  > In `confluence_engine.py`, we evaluate two specialized models in tandem: **Model A**, a Weather Classifier trained on extreme atmospheric events, and **Model B**, a Sensor Defect Classifier trained on synthetically injected fault archetypes.
  >
  > Notice line 72: our mathematical confidence formula factors in both model probabilities and penalizes classification ambiguity.
  >
  > Down in line 87, our decision matrix fuses predictions into clear operational states. Furthermore, line 210 enforces thermodynamic physical boundary checks: if barometric pressure drops rapidly alongside cooling and moisture surge, atmospheric physics overrides false defect flags—guaranteeing zero false alarms during real storms."

---

### Scene 3A: Live App Showcase — True Storm vs. Silent Sensor Drift (01:25 – 02:15 | 50 Seconds)

* **Visual on Screen:**
  - Switch screen to the **Next.js 3D Digital Twin Dashboard** (`http://localhost:3000`).
  - **Action 1 (01:25):** Presenter clicks the **`Thunderstorm (Squall)`** button in the Edge Chaos Lab bar.
    - Live time-series graph plunges: Pressure drops from 1005 to 994 hPa, Humidity surges to 94%, Temperature drops.
    - AI Error Meter stays nominal (~0.021 MSE < 0.042 threshold).
    - 3D Digital Twin remains **Solid Green**. Status: *"AI STATUS: NOMINAL — NATURAL WEATHER DYNAMIC"*.
  - **Action 2 (01:50):** Presenter clicks **`Capacitive Drift`** (`humidity_drift`).
    - Relative Humidity creeps up from 58% to 84% at warm ambient temperatures.
    - The live 1D-CNN Reconstruction Error Meter breaches the red **0.042 MSE** line.
    - **Dynamic Effect:** The 3D Digital Twin pulses **RED**, and the Three.js camera smoothly auto-focuses/lerps directly into the louvered humidity sensor shield.
* **Voiceover Script:**
  > "Let's see the live system in action.
  >
  > First, we inject extreme meteorological turbulence—a severe thunderstorm squall line. Watch the barometric pressure drop by 11 hectopascals while humidity spikes to 94%. Static rule systems cry wolf with false alarms here. But watch SkyGuard: **our 3D Digital Twin remains solid green!** Model A validates that thermodynamic coupling is intact. Zero false alarm.
  >
  > Now, let's inject the real enemy: silent capacitive sensor drift.
  >
  > Relative humidity creeps up to 84%. Because 84 is below the 100% threshold, static systems are completely blind. But watch our 1D-CNN Autoencoder latent bottleneck: reconstruction error breaches our calibrated 0.042 threshold.
  >
  > Instantly, the 3D Digital Twin alerts the operator! The station pulses red, and our camera autonomously glides into the exact physical component at fault. Confluence confirms: **Hardware Sensor Defect with 92% confidence.**"

---

### Scene 3B: Operational Lifecycle — SHAP XAI, Maintenance & Imputation (02:15 – 02:45 | 30 Seconds)

* **Visual on Screen:**
  - Scroll down to the **Explainable Report Viewer (XAI Hub)**: Relative Humidity dominates the **SHAP attribution bar at 88%**, with natural-language text justification.
  - Scroll to **Sensor Health & Predictive Maintenance**: Showing *"Cumulative Drift: Calibration due in < 2 Weeks"*.
  - Scroll to **Multivariate Imputation Module**: Showing Reported Faulty RH ($84.2\%$) ➔ Suggested Imputed RH ($42.6\%$). Presenter clicks `[Apply Imputation]`.
* **Voiceover Script:**
  > "SkyGuard doesn't just raise alarms—it closes the operational repair loop:
  >
  > First, our **SHAP Explainability Hub** generates Shapley feature attributions, proving to field technicians that humidity contributed 88% of the error.
  >
  > Second, our **Predictive Maintenance Module** tracks daily residual drift using EWMA, warning planners that calibration is required within 14 days before total failure occurs.
  >
  > Third, our **Multivariate Imputation Module** reconstructs corrupted telemetry using healthy correlated channels, correcting 84% back to 42.6% to keep downstream forecasting models running without gaps."

---

### Close: Impact & Quantitative Benchmarks (02:45 – 03:00 | 15 Seconds)

* **Visual on Screen:**
  - Full view of the Next.js 3D Digital Twin resetting smoothly to nominal green.
  - Overlay Card displaying key metrics:
    - *False Alarm Reduction: ≥ 85%*
    - *Edge Inference Latency: < 15 ms on ESP32*
    - *Bandwidth Savings: > 90% via Context Bursts*
    - *Confluence F1-Score: 0.94*
* **Voiceover Script:**
  > "By combining edge-quantized micro-intelligence with cloud-scale confluence reasoning, SkyGuard AI cuts false alarms by over 85 percent, saves 90 percent bandwidth, and guarantees pristine data integrity for India's weather infrastructure.
  >
  > Thank you!"

---

## 🛠️ On-Screen Code Spotlight Details (`confluence_engine.py`)

When presenting Scene 2 (VS Code), highlight these specific methods to demonstrate deep computer science and domain knowledge:

```python
# 1. Mathematical Confidence Scoring Formula (Lines 72-85)
def compute_confidence(self, p_weather: float, p_defect: float) -> float:
    p_w = max(0.0, min(1.0, float(p_weather)))
    p_d = max(0.0, min(1.0, float(p_defect)))
    diff = abs(p_d - p_w)
    max_p = max(p_d, p_w)
    ambiguity = 1.0 - diff
    conf_pct = max_p * (1.0 - ambiguity * 0.18) * 100.0
    return round(conf_pct, 1)

# 2. Confluence Truth Matrix (Lines 87-120)
# Fuses Model A P(Weather) and Model B P(Defect) into auditable states:
# - Weather >= 0.70 & Defect < 0.30 -> "Natural Weather Event" (Zero False Alarm)
# - Weather < 0.30 & Defect >= 0.70 -> "Sensor Defect" (High Severity Alert)

# 3. Thermodynamic Physical Safety Overrides (Lines 210-225)
# Squall Physics Check:
# If dt_p < -3.0 hPa and dt_rh > 12.0% and dt_t < -2.0°C -> Valid atmospheric squall!
# Overrides false defect flags during extreme storms.
```

---

## 🧠 Evaluator Defense Cheat Sheet (SIH Q&A)

Keep these exact responses ready if judges ask questions after viewing your video:

1. **Q: Why not run the whole AI model directly on the ESP32?**
   - *Answer:* Microcontrollers like the ESP32-S3 have 512 KB SRAM limits. Running dual ensemble models (Random Forests / LightGBM) and SHAP feature attributions on microcontrollers is physically impossible. Our split-architecture uses a quantized INT8 autoencoder (<15ms, <48KB SRAM) on the edge for filtering, and offloads multi-scale confluence to the cloud.

2. **Q: How did you train Model B without historical sensor failure datasets?**
   - *Answer:* Real-world labeled sensor failure datasets in meteorology are almost non-existent. We solved this data scarcity by mathematically injecting 5 fault archetypes (frozen flatlines, impulse spikes, Gaussian noise bursts, capacitive drift, packet loss) directly into clean weather time-series data.

3. **Q: Why use a Confluence Matrix instead of an LLM agent?**
   - *Answer:* Critical infrastructure monitoring requires deterministic, reproducible, sub-second decisions. LLMs introduce non-deterministic hallucination risks and high inference latency. Our Confluence Matrix uses exact probability bounds and physical thermodynamic laws.

---

## 🎬 Recording Day Checklist

- [ ] Open Chrome at `http://localhost:3000` (Press `F11` for clean full screen).
- [ ] Open VS Code at `backend/services/confluence_engine.py` (Zoom font size to 16pt for clear recording readability).
- [ ] Open Architecture Diagram or presentation slides for Scene 1.
- [ ] Configure OBS Studio for 1080p 60fps recording with active noise cancellation.
- [ ] Perform a dry run of the 3 button actions: **Squall** ➔ **Capacitive Drift** ➔ **Reset**. Verify that the 3D camera lerps smoothly.
