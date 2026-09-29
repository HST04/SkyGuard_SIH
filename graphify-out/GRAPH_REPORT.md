# Graph Report - SkyGuard_SIH  (2026-09-29)

## Corpus Check
- 67 files · ~184,297 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .pptx 3, (none) 2, .csv 2)

## Summary
- 753 nodes · 1395 edges · 37 communities (31 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 49 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `891ce23a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- useTelemetryStore
- client.py
- test_e2e_pipeline.py
- package.json
- imputation_engine.py
- InMemoryStore
- TelemetryPayload
- ConfluenceEngine
- DriftTracker
- compilerOptions
- 📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon)
- services/sensor_health.py
- simulator.py
- schemas.py
- MQTTSubscriber
- main.py
- End-to-End ML Strategy: Split-Edge/Cloud Anomaly Detection & Telemetry Quality Assurance
- EdgeTelemetrySimulator
- SkyGuard AI: Split-Edge/Cloud Anomaly Detection Architecture
- SSEBroadcastManager
- 4. Member Task Details
- 🎬 SkyGuard AI — 3-Minute Prototype Video Submission Master Guide
- next.config.mjs
- next-env.d.ts
- Product Requirements Document — SkyGuard AI
- WeatherStation3D.tsx
- MultiScaleAnalyzer
- dependencies
- 🌟 Key Architecture & Capabilities
- devDependencies
- SkyGuard AI MVP: Minimum User Flows & Operational Journeys
- scripts
- Harsh: maintenance + imputation, fitted into main
- tailwind.config.ts
- rules/graphify.md
- workflows/graphify.md

## God Nodes (most connected - your core abstractions)
1. `useTelemetryStore` - 42 edges
2. `TelemetryPayload` - 41 edges
3. `InMemoryStore` - 23 edges
4. `AnomalyEvent` - 21 edges
5. `react` - 20 edges
6. `DriftTracker` - 18 edges
7. `main()` - 16 edges
8. `lucide-react` - 16 edges
9. `compilerOptions` - 16 edges
10. `get_session()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Tasks:` --references--> `init_db()`  [INFERRED]
  TASKS.md → backend/data/db.py
- `3. Team Coordination & Technical Handoffs` --references--> `main()`  [INFERRED]
  TASKS.md → backend/simulator/client.py
- `🔄 Technical Handoffs:` --references--> `main()`  [INFERRED]
  tasks_no_jargon.md → backend/simulator/client.py
- `Tasks:` --references--> `main()`  [INFERRED]
  TASKS.md → backend/simulator/client.py
- `Tasks:` --references--> `MaintenanceResult`  [INFERRED]
  TASKS.md → frontend/src/lib/types.ts

## Import Cycles
- None detected.

## Communities (37 total, 6 thin omitted)

### Community 0 - "useTelemetryStore"
Cohesion: 0.09
Nodes (50): EdgeSimulatorPage(), frontend_src_app_globals, metadata, RootLayout(), DashboardPage(), TimeSeriesChart(), Header(), AnomalyCard() (+42 more)

### Community 1 - "client.py"
Cohesion: 0.05
Nodes (47): argparse, Predictive maintenance: tracks slow sensor drift and estimates when a sensor…, calculate_dew_point(), CircularRingBuffer, EdgeIMDBoundaryChecker, FaultState, format_status_badge(), main() (+39 more)

### Community 2 - "test_e2e_pipeline.py"
Cohesion: 0.07
Nodes (65): anyio, asyncio, AsyncSession, AnomalyIncident, Base, format_db_url(), get_recent_telemetry(), get_session() (+57 more)

### Community 3 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, autoprefixer, clsx, postcss, react-dom, tailwind-merge (+6 more)

### Community 4 - "imputation_engine.py"
Cohesion: 0.12
Nodes (18): dew_point(), find_column(), _fit_line(), ImputationEngine, _ok(), Imputation: estimates what a faulty sensor should read, using the sensors that…, Fit RH-vs-T and pressure stats from the normal-weather CSV., rh_from_dewpoint() (+10 more)

### Community 5 - "InMemoryStore"
Cohesion: 0.07
Nodes (17): InMemoryStore, Any, Non-blocking enqueue for database persistence., Adds telemetry to in-memory history and enqueues async DB write without…, Adds anomaly to in-memory state and enqueues async DB write., Enqueues a predictive maintenance record for persistence., Blocks until pending persistence tasks have finished (useful for testing)., Clears in-memory history and active anomalies (useful for testing). (+9 more)

### Community 6 - "TelemetryPayload"
Cohesion: 0.25
Nodes (13): TelemetryPayload, calculate_dew_point(), IMDPhysicsRuleEngine, Stage 1: Deterministic Climatological & Physical Bounds Checker. Strictly based…, Evaluates current reading against IMD physics bounds and previous step. Returns…, Calculates dew point using the standard Magnus-Tetens approximation formula., Runs every telemetry source through one ordered processing pipeline., TelemetryIngestionService (+5 more)

### Community 7 - "ConfluenceEngine"
Cohesion: 0.13
Nodes (14): ConfluenceEngine, ConfluenceResult, Any, Structured outcome of the Dual-Model Classification Confluence Decision Matrix…, Evaluates a window of telemetry records. If trained models are present, runs…, Layer 2.3: Classification Confluence & Confidence Scoring Engine. Reconciles…, Attempts to load Model A (Weather) and Model B (Defect) from artifacts. If…, Calculates mathematical confidence score (0-100%) according to Layer 2.3:… (+6 more)

### Community 8 - "DriftTracker"
Cohesion: 0.11
Nodes (10): DriftTracker, Report current state without feeding a new residual., Use baseline statistics instead of a live warmup (all stations)., Keep the live warmup, but never assume less noise than this., Call after a technician recalibrates the sensor., _SensorState, _epoch(), weather_event: pass the confluence engine's answer once it exists. Left as… (+2 more)

### Community 9 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 10 - "📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon)"
Cohesion: 0.04
Nodes (47): 🗺️ How the System Works, 🎬 How to Record:, 📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon), 🟢 STAGE 1: Setting Up the Cloud Notebook (The Database), 🟢 STAGE 2: Setting Up the Cloud Server (The Azure Brain), 🟢 STAGE 3: Creating the Weather Materials (The Teacher Data), 🟢 STAGE 4: Training the AI Brain in Google Colab (Free GPU), 🟢 STAGE 5: Building the Cloud Decision Engine (The Judge & Doctor) (+39 more)

### Community 11 - "services/sensor_health.py"
Cohesion: 0.20
Nodes (12): Settings, Sensor health: predictive maintenance + imputation, run once per packet from…, BaseSettings, json, logging, math, numpy, pathlib (+4 more)

### Community 12 - "simulator.py"
Cohesion: 0.19
Nodes (13): FaultInjectionRequest, get_simulator_status(), inject_fault(), get, post, Injects a physical sensor fault or environmental transient into the virtual…, Resets simulator to clean nominal weather with zero faults., Launches the 5-Minute Auto-Scenario Pitch Script: - T+0:00 (Baseline): Normal… (+5 more)

### Community 13 - "schemas.py"
Cohesion: 0.15
Nodes (18): AnomalyUpdateRequest, ImputationAcceptRequest, OperatorFeedback, ShapAttribution, StationOverview, get_anomaly(), list_anomalies(), get (+10 more)

### Community 14 - "MQTTSubscriber"
Cohesion: 0.20
Nodes (8): MQTTSubscriber, Any, Client, ConnectFlags, DisconnectFlags, MQTTMessage, Properties, ReasonCode

### Community 15 - "main.py"
Cohesion: 0.09
Nodes (25): health_check(), lifespan(), get, root(), accept_imputation(), get_maintenance(), get, post (+17 more)

### Community 16 - "End-to-End ML Strategy: Split-Edge/Cloud Anomaly Detection & Telemetry Quality Assurance"
Cohesion: 0.06
Nodes (31): 10.1 Model Architecture & Formulation, 10. Imputation & Correction Module (3.5), 11. Evaluation Metrics & Benchmark Targets, 12. Configuration Reference (`config/ml_pipeline.yaml`), 1. Executive Summary & Core Principles, 2. End-to-End ML Pipeline Architecture, 3.1 1.1 IMD Plausibility Check (Logical Filter), 3.2 1.2 Quantized PyOD (Lightweight Outlier Detection) (+23 more)

### Community 17 - "EdgeTelemetrySimulator"
Cohesion: 0.24
Nodes (3): PitchScriptStatus, EdgeTelemetrySimulator, Main 1 Hz simulation tick.

### Community 18 - "SkyGuard AI: Split-Edge/Cloud Anomaly Detection Architecture"
Cohesion: 0.07
Nodes (26): 1. Executive Summary & Design Principles, 1. Periodic Nominal Heartbeat, 2. Flagged Incident Packet (Context Burst), 2. High-Level Architecture Diagram, 3. Detailed Layer Explanation & Responsibilities, 4. End-to-End Data Pipeline Flow, 5.1 Layer 1.1: IMD Plausibility Check (Logical Filter), 5.2 Layer 1.2: Quantized PyOD / TFLite Micro (+18 more)

### Community 19 - "SSEBroadcastManager"
Cohesion: 0.25
Nodes (4): Any, Broadcasts an SSE message formatted as: event: <event_type> data: <json_string>, SSEBroadcastManager, Queue

### Community 20 - "4. Member Task Details"
Cohesion: 0.08
Nodes (25): 1. Project Context & System Architecture, 2. Task Allocation & Work Breakdown, 3. Team Coordination & Technical Handoffs, 4. Member Task Details, 5. Team Rehearsal & Verification Matrix, 6. Showcase Recording Plan (5-Minute Dual-Screen Video), ARAZ, HANSWARUP (+17 more)

### Community 21 - "🎬 SkyGuard AI — 3-Minute Prototype Video Submission Master Guide"
Cohesion: 0.09
Nodes (21): 📌 Executive Video Architecture: The 180-Second Strategy, High-Level Timeline Breakdown, Key Technical Specifications, 📊 Live Demonstration Teleprompter & Action Cue Sheet, Recommended Dual-Pane Recording Layout (1920x1080), 🖥️ Screen Layout & Production Staging, 🎙️ Second-by-Second Video Script & Choreography, Segment 1: The Hook & The Critical Problem (00:00 – 00:25 | 25 seconds) (+13 more)

### Community 25 - "Product Requirements Document — SkyGuard AI"
Cohesion: 0.11
Nodes (17): 1. Executive Summary, 2.1 Current State vs. SkyGuard AI, 2.2 Root Causes Addressed, 2. Problem Statement & Root Causes, 3.1 Goals, 3.2 Non-Goals (Out of Scope for MVP), 3.3 Success Metrics, 3. Goals, Non-Goals, and Success Metrics (+9 more)

### Community 26 - "WeatherStation3D.tsx"
Cohesion: 0.23
Nodes (12): CameraController(), CameraTarget, TARGETS, SensorNode(), SensorNodeProps, StationModel(), WeatherStation3D(), WeatherStation3DProps (+4 more)

### Community 27 - "MultiScaleAnalyzer"
Cohesion: 0.23
Nodes (9): MultiScaleAnalyzer, Any, Layer 2.1: Multi-Scale Multivariate Physical Analyzer (PRD Section 5.3 /…, Comprehensive multi-scale analysis over the current rolling telemetry window.…, Safely extracts a float field from a Pydantic model or dictionary., Computes numerical first derivatives (dT/dt, dP/dt, dRH/dt) and second…, Computes Pearson correlation coefficient rho_{T, RH} across the sliding window.…, Task 1.3: Verify isolated Multi-Scale Multivariate Analyzer functionality. (+1 more)

### Community 28 - "dependencies"
Cohesion: 0.17
Nodes (12): dependencies, clsx, lucide-react, next, react, react-dom, @react-three/drei, @react-three/fiber (+4 more)

### Community 29 - "🌟 Key Architecture & Capabilities"
Cohesion: 0.18
Nodes (10): 1.0 Edge Device Layer (ESP32 Deployment & Emulation), 1. Start the Backend API (FastAPI), 2.0 Cloud Analytics Layer (Structured Reasoning), 2. Start the Frontend Dashboard (Next.js 14), 3.0 Visualization & Alerting Layer (Operator Dashboard), 3. Optional Two-Laptop / Edge Simulator Demo, 🌟 Key Architecture & Capabilities, 🚀 Quick Start (Local Run) (+2 more)

### Community 30 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 31 - "SkyGuard AI MVP: Minimum User Flows & Operational Journeys"
Cohesion: 0.29
Nodes (6): 1. Primary Flow: Edge Filtering, Confluence Reasoning, & XAI Diagnostics, 2. Secondary Flow: Predictive Maintenance & Sensor Health (3.4), 3. Tertiary Flow: Imputation & Data Correction (3.5), 4. Live Demonstration Flow: The 5-Minute Pitch Script, Primary Sequence Diagram, SkyGuard AI MVP: Minimum User Flows & Operational Journeys

### Community 32 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 33 - "Harsh: maintenance + imputation, fitted into main"
Cohesion: 0.40
Nodes (4): For Mudit, For Shreyansh, Harsh: maintenance + imputation, fitted into main, Settings

## Knowledge Gaps
- **198 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 371 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `client.py` to `📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon)`, `4. Member Task Details`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `init_db()` connect `test_e2e_pipeline.py` to `4. Member Task Details`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `TelemetryPayload` (e.g. with `InMemoryStore` and `MultivariateAnomalyDetector`) actually correct?**
  _`TelemetryPayload` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InMemoryStore` (e.g. with `AnomalyEvent` and `OperatorFeedback`) actually correct?**
  _`InMemoryStore` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AnomalyEvent` (e.g. with `InMemoryStore` and `AnomalyEvaluation`) actually correct?**
  _`AnomalyEvent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nextConfig`, `name`, `version` to the rest of the system?**
  _198 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `useTelemetryStore` be split into smaller, more focused modules?**
  _Cohesion score 0.0869215291750503 - nodes in this community are weakly interconnected._