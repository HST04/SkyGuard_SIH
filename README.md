# 🛰️ SkyGuard AI — Self-Healing Edge-to-Cloud Anomaly Detection for AWS

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-blueviolet.svg?logo=three.js&logoColor=white)](https://docs.pmnd.rs/react-three-fiber)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

**SkyGuard AI** is a self-healing, edge-to-cloud anomaly detection pipeline designed specifically for Automatic Weather Stations (AWS). By pairing deterministic India Meteorological Department (IMD) physics rules with multivariate temporal learning (1D-CNN autoencoder) and explainable AI (SHAP), SkyGuard catches silent sensor drift and cross-channel decoupling that static single-channel thresholds miss.

---

## 🌟 Key Capabilities (Layer 1 MVP)

- **Interactive 3D Digital Twin**: Procedural Three.js / React Three Fiber model of weather station `AGRA-01` with animated rotating anemometer, wind vane, solar panels, and clickable sensor shields.
- **Auto-Focus Camera**: Smooth camera lerp that automatically targets and zooms into the culprit sensor node whenever an anomaly is flagged.
- **Stage 1 IMD Physics Rules**: Deterministic checks for physical saturation bounds (0-100% RH), barometric limits, dew point supersaturation sanity ($T_d \le T + 0.5$), and rate-of-change thresholds.
- **Stage 2 Multivariate Anomaly Detection**: Tracks inter-parameter physical correlation ($T \leftrightarrow P \leftrightarrow RH$) over a 12-timestep sliding window.
- **SHAP Feature Attribution**: Human-readable breakdown showing which sensor contributed to the reconstruction error.
- **Active Learning Loop**: Operator feedback buttons ("Mark as False Alarm", "Acknowledge", "Resolve") logged for threshold adaptation.
- **Virtual Edge Chaos Injector & 5-Minute Auto-Pitch Script**:
  - *Phase 1 (0:00 - 1:30)*: Normal Diurnal Baseline (Status Green)
  - *Phase 2 (1:30 - 3:00)*: Severe Thunderstorm Squall True-Negative Test (Proves zero false alarm on natural storms!)
  - *Phase 3 (3:00 - 3:45)*: Subtle +15% Capacitive Drift Injected
  - *Phase 4 (3:45 - 5:00)*: Anomaly Threshold Tripped! 3D Twin pulses Red, camera zooms into humidity shield, SHAP attribution opens.

---

## 🏗️ Architecture

```mermaid
graph TD
    SIM[Virtual Edge Simulator<br/>Station AGRA-01 @ 1 Hz] --> CORE[FastAPI Ingestion Engine]
    CORE --> RULE{Stage 1: IMD Physics Rules}
    RULE -->|Violation| FLAG[Rule Flag Anomaly]
    RULE -->|Passed| CNN{Stage 2: Multivariate Anomaly Engine}
    CNN -->|Error > Threshold| SHAP[SHAP Attribution Engine]
    CNN -->|Normal| STORE[(In-Memory Buffer)]
    FLAG --> SSE[SSE Broadcast Manager]
    SHAP --> SSE
    STORE --> SSE
    SSE -->|1 Hz Stream| UI[Next.js 3D Digital Twin Dashboard]
    UI -.->|Operator Feedback| CORE
```

---

## 🚀 Quick Start (Zero Cloud Dependencies)

You can run the entire system locally in under 2 minutes:

### 1. Start the Backend API (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```
*API will run at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.*

### 2. Start the Frontend (Next.js 14)
```bash
cd frontend
npm install
npm run dev
```
*Dashboard will open at `http://localhost:3000`.*

---

## 🖥️ Screen Navigation

- **Main 3D Dashboard**: `http://localhost:3000/`
  - 60/40 Split layout: Left 3D Digital Twin with interactive camera; Right live telemetry, SHAP cards, anomaly triage, and time-series chart.
- **Virtual Edge Simulator & Chaos Lab**: `http://localhost:3000/edge-simulator`
  - Fault injector for capacitive drift, heat spikes, barometric drops, and the automated 5-minute pitch script.
