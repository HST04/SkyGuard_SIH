# Product Requirements Document — SkyGuard AI
## Self-Healing Edge-to-Cloud Anomaly Detection for Automatic Weather Stations

| Field | Value |
|---|---|
| **Document Version** | 2.0 (Expanded) |
| **Status** | Approved for Build |
| **Owner** | Project Lead / ML Engineer |
| **Last Updated** | 2026-09-16 |
| **Target Release** | Hackathon MVP: Week 6 · Public Portfolio Launch: December |
| **Classification** | Public / Portfolio |

### Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | — | — | Initial hackathon scope |
| 2.0 | 2026-09-16 | — | Full expansion: architecture, data contracts, ML spec, NFRs, QA, rollout |

---

## 1. Executive Summary

Automatic Weather Stations (AWS) are deployed in harsh, unmanned environments where sensors degrade, drift, and fail silently. Conventional monitoring relies on **static threshold rules** (e.g., "alert if relative humidity > 100%"). These rules are trivially defeated by:

- **Sensor drift** — slow bias that never crosses a hard limit.
- **Environmental noise** — dust, icing, thermal gradients, radio interference.
- **Cross-channel decoupling** — a humidity sensor fails while temperature and pressure remain nominal.

The result is **alarm fatigue**: operators disable alerts, and genuine faults go undetected.

**SkyGuard AI** is a self-healing, edge-to-cloud anomaly detection pipeline that:

1. **Pre-filters** physically impossible readings using hardcoded IMD climatological rules (cheap, deterministic, zero-latency).
2. **Learns the normal manifold** of multivariate weather telemetry with a 1D-CNN autoencoder, exploiting inter-parameter correlation (T ↔ P ↔ RH) as the primary health signal.
3. **Explains** every flag via SHAP attribution so operators trust and act on alerts.
4. **Improves itself** through an operator feedback loop: confirmed/refuted anomalies are logged to Supabase, clustered with DBSCAN in latent space, and converted into threshold-tuning recommendations.
5. **Visualizes** the station as a procedural Three.js Digital Twin with a live 1 Hz SSE feed and a demo-ready fault injector.

**MVP is 100% software-simulated.** No hardware dependency, no field deployment, no procurement blocker — enabling a fully contained, reproducible sprint.

---

## 2. Problem Statement

### 2.1 Current State

| Aspect | Today |
|---|---|
| Detection method | Static IMD thresholds, single-parameter |
| False alarm rate | High (estimated 60–80% of alerts are non-actionable) |
| Multivariate reasoning | None |
| Explainability | None — alerts are binary and opaque |
| Adaptation | None — thresholds are hand-tuned and frozen |
| Operator trust | Low; alert fatigue leads to ignored dashboards |

### 2.2 Root Causes

1. **Univariate blindness.** A humidity sensor reading 78% RH is "valid" in isolation — but not if temperature is 41 °C and pressure is falling, a combination that is climatologically implausible.
2. **Threshold brittleness.** Physical limits (0–100% RH) catch only gross failures, not drift or noise.
3. **No feedback channel.** Operators have no mechanism to teach the system which alerts were real.
4. **Compute constraints.** AWS gateways are low-power; heavy models cannot run on-device without careful optimization.

### 2.3 Opportunity

Multivariate correlation structure is a **free, high-signal health indicator**. When sensors are healthy, T/P/RH move together in physically consistent ways. When one degrades, the correlation breaks — often before any single channel violates a hard limit. A compact convolutional autoencoder can learn this structure and flag deviations at sub-50 ms latency.

---

## 3. Goals, Non-Goals, and Success Metrics

### 3.1 Goals

| ID | Goal | Type |
|---|---|---|
| G-1 | Detect sensor anomalies invisible to static thresholds | Technical |
| G-2 | Reduce false alarm rate by ≥80% vs. static IMD rules | Business |
| G-3 | Achieve PR-AUC > 0.90 on held-out fault-injection test set | Technical |
| G-4 | Sub-50 ms per-window inference on constrained hardware | Technical |
| G-5 | Provide human-readable explanations for every alert | Product |
| G-6 | Close the loop with an operator feedback → retraining cycle | Product |
| G-7 | Ship a visually compelling public artifact suitable for social build-in-public content | Portfolio |

### 3.2 Non-Goals (Explicitly Out of Scope for MVP)

- ❌ Physical hardware integration (no LoRaWAN, no RS-485, no real AWS units)
- ❌ Weather *forecasting* — this is data *integrity* monitoring, not prediction
- ❌ Multi-tenant / multi-organization auth and billing
- ❌ Regulatory certification (WMO/IMD compliance audits)
- ❌ Mobile native apps
- ❌ Automated model retraining in production (MVP is recommendation-only; a human applies changes)

### 3.3 Success Metrics

| Metric | Target | Measurement Method |
|---|---|---|
| **PR-AUC** | > 0.90 | Held-out test set, 5-fold CV mean |
| **Inference latency (p95)** | < 50 ms | ONNX Runtime, single vCPU, 60-sample window |
| **False Alarm Rate reduction** | ≥ 80% | Alerts/hour vs. static IMD baseline over 7-day simulated run |
| **Recall @ operating threshold** | ≥ 0.92 | Test set |
| **SSE update frequency** | 1 Hz, jitter < 100 ms | Client-side timestamp delta histogram |
| **SSE reconnection** | < 5 s recovery, exponential backoff | Chaos test: 10 forced disconnects |
| **Model artifact size** | < 500 KB (quantized) | Post-training INT8 quantization |
| **Cold start (edge)** | < 2 s | Container start → first inference |
| **Feedback loop round-trip** | < 60 s | Operator click → Supabase row → DBSCAN recommendation |

---

## 4. Personas & User Stories

### 4.1 Personas

| Persona | Description | Primary Need |
|---|---|---|
| **Meera — IMD Field Operator** | Monitors 40 AWS units from a control room. Non-ML expert. | Trustworthy, explainable alerts she can act on in <30 seconds |
| **Arjun — Data Engineer** | Maintains ingestion pipelines and broker uptime. | Observable, debuggable, standards-based (MQTT) plumbing |
| **Dr. Rao — Meteorologist / Reviewer** | Validates whether flagged data should be discarded. | Physical plausibility reasoning + attribution evidence |
| **Recruiter / Reviewer (Portfolio)** | Evaluates engineering depth from a public repo + demo video. | Clear architecture, real metrics, polished UI |

### 4.2 User Stories

**Ingestion & Detection**
- **US-01** — As an operator, I want physically impossible readings flagged instantly so I can discard them before they pollute downstream models.
- **US-02** — As an operator, I want anomalies detected even when no single parameter breaches a hard limit, so that silent drift is caught.
- **US-03** — As an operator, I want to see *which* sensor caused the flag, so I know what to inspect.

**Explainability & Trust**
- **US-04** — As a meteorologist, I want SHAP-style attribution per channel so I can validate the model's reasoning.
- **US-05** — As an operator, I want a confidence score alongside each alert so I can triage by severity.

**Feedback & Adaptation**
- **US-06** — As an operator, I want to mark an alert as "Confirmed Fault" or "False Alarm" in one click.
- **US-07** — As an operator, I want the system to periodically suggest threshold adjustments based on my feedback.
- **US-08** — As a data engineer, I want feedback older than 7 days auto-purged to control storage cost and privacy surface.

**Demo & Visualization**
- **US-09** — As a demo viewer, I want a live 3D Digital Twin that reacts to telemetry in real time.
- **US-10** — As a demo operator, I want to inject faults on demand (spike, drift, stuck-at) to prove detection works.
- **US-11** — As a portfolio reviewer, I want a public README, architecture diagram, and benchmark table.

---

## 5. Scope

### 5.1 MVP Scope (Must Have)

| # | Capability | Deliverable |
|---|---|---|
| 1 | Virtual Edge Simulator UI | Web app generating synthetic T/P/RH telemetry at 1 Hz |
| 2 | MQTT transport | TLS-secured MQTT to Azure-hosted Mosquitto |
| 3 | IMD Pre-Filter | Deterministic rule engine, ~12 hardcoded rules |
| 4 | 1D-CNN Autoencoder | PyTorch training + ONNX export, quantized |
| 5 | Baselines | K-Means + Decision Tree with identical eval harness |
| 6 | SHAP Explainability | Per-window, per-channel attribution |
| 7 | Active Learning Loop | Supabase feedback table + DBSCAN recommender |
| 8 | Next.js UI | Digital Twin, SSE live feed, Injector, Feedback panel |

### 5.2 Post-MVP / Stretch (Nice to Have)

- LSTM/Transformer autoencoder comparison
- Multi-station federated learning
- Real AWS hardware bridge (Modbus/RS-485 → MQTT)
- Grafana/Power BI ops dashboard
- Automated threshold application (closed-loop write-back)
- ONNX Runtime Web / WASM in-browser inference demo
- Docker Compose one-command local spin-up
- Public leaderboard of fault-injection scenarios

### 5.3 Out of Scope

Refer to §3.2.

---

## 6. System Architecture

### 6.1 High-Level Architecture

```mermaid
flowchart LR
    subgraph EDGE["Virtual Edge (Browser)"]
        SIM["Simulator UI<br/>T/P/RH @ 1 Hz"]
        INJ["Fault Injector<br/>spike/drift/stuck/noise"]
        SIM --> INJ
    end

    subgraph BROKER["Azure Cloud"]
        MQ["Mosquitto Broker<br/>TLS :8883"]
        API["Ingestion Service<br/>FastAPI"]
        PRE["IMD Pre-Filter"]
        ML["1D-CNN Autoencoder<br/>ONNX Runtime"]
        SHAP["SHAP Explainer"]
        SSE["SSE Broadcaster"]
    end

    subgraph DATA["Persistence"]
        SB[("Supabase<br/>feedback, 7-day TTL")]
        BLOB[("Azure Blob<br/>model artifacts")]
    end

    subgraph CLIENT["Next.js App"]
        TWIN["Three.js Digital Twin"]
        FEED["Live SSE Feed"]
        FB["Operator Feedback Panel"]
    end

    INJ -->|MQTT/TLS| MQ
    MQ --> API
    API --> PRE
    PRE -->|pass| ML
    PRE -->|hard fail| SSE
    ML --> SHAP
    SHAP --> SSE
    SSE --> FEED
    SSE --> TWIN
    FB -->|REST| API
    API --> SB
    SB -->|DBSCAN job| ML
    BLOB --> ML