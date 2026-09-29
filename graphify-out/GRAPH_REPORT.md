# Graph Report - SkyGuard_SIH  (2026-09-29)

## Corpus Check
- 70 files · ~192,961 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .pptx 3, (none) 2, .csv 2)

## Summary
- 980 nodes · 1865 edges · 47 communities (42 shown, 5 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `269970c7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- useTelemetryStore
- test_mqtt_stage6.py
- test_qa_backend_math_edge_cases.py
- anyio
- imputation_engine.py
- InMemoryStore
- TelemetryPayload
- ConfluenceResult
- DriftTracker
- compilerOptions
- 📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon)
- test_qa_edge_telemetry_stress.py
- simulator.py
- anomalies.py
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
- CircularRingBuffer
- TestConfluenceEngineEdgeCases
- package.json
- 🌟 Key Architecture & Capabilities
- client.py
- SkyGuard AI MVP: Minimum User Flows & Operational Journeys
- test_qa_ml_integration.py
- Harsh: maintenance + imputation, fitted into main
- TestMalformedPayloadsAndTypeMismatch
- rules/graphify.md
- MultivariateAnomalyDetector
- stream_telemetry
- test_sensor_health.py
- make_packet
- ConfluenceEngine
- MultiScaleAnalyzer
- TestShapeCompatibilityAndFailureModes
- AnomalyEvaluation
- SKILL.md
- AnomalyEvent
- .analyze_window

## God Nodes (most connected - your core abstractions)
1. `TelemetryPayload` - 54 edges
2. `useTelemetryStore` - 42 edges
3. `make_packet()` - 33 edges
4. `ConfluenceEngine` - 28 edges
5. `InMemoryStore` - 26 edges
6. `MultivariateAnomalyDetector` - 26 edges
7. `AnomalyEvent` - 24 edges
8. `DriftTracker` - 22 edges
9. `react` - 20 edges
10. `MultiScaleAnalyzer` - 19 edges

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

## Communities (47 total, 5 thin omitted)

### Community 0 - "useTelemetryStore"
Cohesion: 0.07
Nodes (62): EdgeSimulatorPage(), frontend_src_app_globals, metadata, RootLayout(), DashboardPage(), TimeSeriesChart(), Header(), AnomalyCard() (+54 more)

### Community 1 - "test_mqtt_stage6.py"
Cohesion: 0.16
Nodes (13): calculate_dew_point(), EdgeIMDBoundaryChecker, Calculates dew point using Magnus-Tetens approximation., Layer 1.1 Local Deterministic Bounds & Rate-of-Change Checker Evaluates IMD…, Unit & Integration Tests for Laptop 1 Edge Weather Station Transmitter Stage 6…, Verify standard edge telemetry packet passes through backend ingestion cleanly., Verify all 5 transmitter modes generate physically consistent baseline and…, Verify in-memory circular ring buffer maintains 120-item capacity and retrieves… (+5 more)

### Community 2 - "test_qa_backend_math_edge_cases.py"
Cohesion: 0.06
Nodes (72): asyncio, AsyncSession, AnomalyIncident, Base, format_db_url(), get_recent_telemetry(), get_session(), init_db() (+64 more)

### Community 3 - "anyio"
Cohesion: 0.13
Nodes (11): anyio, CRITICAL VULNERABILITY TEST: Evaluate what happens when NaN or Inf are injected…, Rigorous tests evaluating the 5 chaos modes in client.py and extended simulator…, Verify all 5 chaos modes generate well-formed TelemetryPayload packets., HARSH ANALYSIS - Mode 1 Heat Spike: Tick 1 jumps +8°C instantaneously ->…, HARSH ANALYSIS - Mode 2 Capacitive Drift: In client.py, humidity jumps +15% in…, HARSH ANALYSIS - Mode 3 Severe Thunderstorm: In client.py, storm applies -11…, CRITICAL PROTOCOL DISCREPANCY - Mode 4 Frozen Sensor: In client.py, humidity… (+3 more)

### Community 4 - "imputation_engine.py"
Cohesion: 0.06
Nodes (31): dew_point(), find_column(), _fit_line(), ImputationEngine, _ok(), Imputation: estimates what a faulty sensor should read, using the sensors that…, Fit RH-vs-T and pressure stats from the normal-weather CSV., rh_from_dewpoint() (+23 more)

### Community 5 - "InMemoryStore"
Cohesion: 0.06
Nodes (17): InMemoryStore, Any, Non-blocking enqueue for database persistence., Adds telemetry to in-memory history and enqueues async DB write without…, Adds anomaly to in-memory state and enqueues async DB write., Enqueues a predictive maintenance record for persistence., Blocks until pending persistence tasks have finished (useful for testing)., Clears in-memory history and active anomalies (useful for testing). (+9 more)

### Community 6 - "TelemetryPayload"
Cohesion: 0.23
Nodes (13): TelemetryPayload, calculate_dew_point(), IMDPhysicsRuleEngine, Stage 1: Deterministic Climatological & Physical Bounds Checker. Strictly based…, Evaluates current reading against IMD physics bounds and previous step. Returns…, Calculates dew point using the standard Magnus-Tetens approximation formula., Runs every telemetry source through one ordered processing pipeline., TelemetryIngestionService (+5 more)

### Community 7 - "ConfluenceResult"
Cohesion: 0.15
Nodes (8): ConfluenceResult, Any, Structured outcome of the Dual-Model Classification Confluence Decision Matrix…, Evaluates a window of telemetry records. If trained models are present, runs…, Attempts to load Model A (Weather) and Model B (Defect) from artifacts. If…, Calculates mathematical confidence score (0-100%) according to Layer 2.3:…, Evaluates the deterministic Confluence Decision Matrix (PRD Section 5.5 /…, dict

### Community 8 - "DriftTracker"
Cohesion: 0.09
Nodes (14): DriftTracker, Report current state without feeding a new residual., Use baseline statistics instead of a live warmup (all stations)., Keep the live warmup, but never assume less noise than this., Call after a technician recalibrates the sensor., _SensorState, Rigorous tests for DriftTracker: learning phase, zero-sigma crash, negative…, Verify exact transition from 'Learning' to 'Healthy' at WARMUP_SAMPLES. (+6 more)

### Community 9 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 10 - "📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon)"
Cohesion: 0.04
Nodes (47): 🗺️ How the System Works, 🎬 How to Record:, 📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon), 🟢 STAGE 1: Setting Up the Cloud Notebook (The Database), 🟢 STAGE 2: Setting Up the Cloud Server (The Azure Brain), 🟢 STAGE 3: Creating the Weather Materials (The Teacher Data), 🟢 STAGE 4: Training the AI Brain in Google Colab (Free GPU), 🟢 STAGE 5: Building the Cloud Decision Engine (The Judge & Doctor) (+39 more)

### Community 11 - "test_qa_edge_telemetry_stress.py"
Cohesion: 0.23
Nodes (13): Settings, Harsh, Rigorous QA Stress Test Suite: Edge Transmitter, Chaos Modes, MQTT/REST…, BaseSettings, fastapi_responses, json, logging, math, numpy (+5 more)

### Community 12 - "simulator.py"
Cohesion: 0.19
Nodes (13): FaultInjectionRequest, get_simulator_status(), inject_fault(), get, post, Injects a physical sensor fault or environmental transient into the virtual…, Resets simulator to clean nominal weather with zero faults., Launches the 5-Minute Auto-Scenario Pitch Script: - T+0:00 (Baseline): Normal… (+5 more)

### Community 13 - "anomalies.py"
Cohesion: 0.16
Nodes (15): AnomalyUpdateRequest, OperatorFeedback, StationOverview, get_anomaly(), list_anomalies(), get, post, Lists detected anomalies, sorted by most recent. (+7 more)

### Community 14 - "MQTTSubscriber"
Cohesion: 0.20
Nodes (8): MQTTSubscriber, Any, Client, ConnectFlags, DisconnectFlags, MQTTMessage, Properties, ReasonCode

### Community 15 - "main.py"
Cohesion: 0.15
Nodes (15): health_check(), lifespan(), get, root(), ImputationAcceptRequest, accept_imputation(), get_maintenance(), get (+7 more)

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
Cohesion: 0.12
Nodes (11): Any, Broadcasts an SSE message formatted as: event: <event_type> data: <json_string>, SSEBroadcastManager, Rigorous tests evaluating the SSE Broadcast Manager, connection lifecycle,…, Verify subscribing and unsubscribing cleanly tracks client count., Verify broadcasts are dispatched concurrently to all active subscriber queues., Verify when a slow/stalled client queue (maxsize=100) fills up, the oldest…, VULNERABILITY TEST: If non-serializable objects (such as raw Python objects or… (+3 more)

### Community 20 - "4. Member Task Details"
Cohesion: 0.08
Nodes (25): 1. Project Context & System Architecture, 2. Task Allocation & Work Breakdown, 3. Team Coordination & Technical Handoffs, 4. Member Task Details, 5. Team Rehearsal & Verification Matrix, 6. Showcase Recording Plan (5-Minute Dual-Screen Video), ARAZ, HANSWARUP (+17 more)

### Community 21 - "🎬 SkyGuard AI — 3-Minute Prototype Video Submission Master Guide"
Cohesion: 0.09
Nodes (21): 📌 Executive Video Architecture: The 180-Second Strategy, High-Level Timeline Breakdown, Key Technical Specifications, 📊 Live Demonstration Teleprompter & Action Cue Sheet, Recommended Dual-Pane Recording Layout (1920x1080), 🖥️ Screen Layout & Production Staging, 🎙️ Second-by-Second Video Script & Choreography, Segment 1: The Hook & The Critical Problem (00:00 – 00:25 | 25 seconds) (+13 more)

### Community 25 - "Product Requirements Document — SkyGuard AI"
Cohesion: 0.11
Nodes (17): 1. Executive Summary, 2.1 Current State vs. SkyGuard AI, 2.2 Root Causes Addressed, 2. Problem Statement & Root Causes, 3.1 Goals, 3.2 Non-Goals (Out of Scope for MVP), 3.3 Success Metrics, 3. Goals, Non-Goals, and Success Metrics (+9 more)

### Community 26 - "CircularRingBuffer"
Cohesion: 0.11
Nodes (15): CircularRingBuffer, make_incident_burst(), Builds an MQTT Incident Context Burst payload., In-memory circular ring buffer representing a 2-hour sliding window (120…, Returns the past `count` samples preceding the current reading., Verify Incident Burst payload structure contains trigger reading + 12 context…, Verify backend ingestion handles incident burst payloads by unwrapping the…, test_incident_burst_ingestion_compatibility() (+7 more)

### Community 27 - "TestConfluenceEngineEdgeCases"
Cohesion: 0.07
Nodes (15): fixture, Zero variance in temperature or humidity must return 0.0 correlation without…, Document flaw: NaN or Inf inside window propagates silently into correlation…, Document flaw: compute_derivatives relies on list indexing window[-1] -…, Verify boundary condition: rho_{T, RH} > 0.0 and abs(dP/dt) < 2.0., Rigorous verification of Layer 2.3 ConfluenceEngine and confidence score…, Verify confidence formula: conf_pct = max(P_D, P_W) * (1.0 - (1.0 - |P_D -…, Test negative, super-unity, and NaN probability handling. (+7 more)

### Community 28 - "package.json"
Cohesion: 0.05
Nodes (42): dependencies, clsx, lucide-react, next, react, react-dom, @react-three/drei, @react-three/fiber (+34 more)

### Community 29 - "🌟 Key Architecture & Capabilities"
Cohesion: 0.18
Nodes (10): 1.0 Edge Device Layer (ESP32 Deployment & Emulation), 1. Start the Backend API (FastAPI), 2.0 Cloud Analytics Layer (Structured Reasoning), 2. Start the Frontend Dashboard (Next.js 14), 3.0 Visualization & Alerting Layer (Operator Dashboard), 3. Optional Two-Laptop / Edge Simulator Demo, 🌟 Key Architecture & Capabilities, 🚀 Quick Start (Local Run) (+2 more)

### Community 30 - "client.py"
Cohesion: 0.14
Nodes (17): argparse, Predictive maintenance: tracks slow sensor drift and estimates when a sensor…, FaultState, format_status_badge(), main(), parse_args(), print_banner(), SkyGuard AI — Laptop 1 Edge Weather Station Transmitter (AWS AGRA-01) Assigned… (+9 more)

### Community 31 - "SkyGuard AI MVP: Minimum User Flows & Operational Journeys"
Cohesion: 0.29
Nodes (6): 1. Primary Flow: Edge Filtering, Confluence Reasoning, & XAI Diagnostics, 2. Secondary Flow: Predictive Maintenance & Sensor Health (3.4), 3. Tertiary Flow: Imputation & Data Correction (3.5), 4. Live Demonstration Flow: The 5-Minute Pitch Script, Primary Sequence Diagram, SkyGuard AI MVP: Minimum User Flows & Operational Journeys

### Community 32 - "test_qa_ml_integration.py"
Cohesion: 0.11
Nodes (19): build_synthetic_autoencoder_onnx(), __init__(), build_synthetic_model_a(), build_synthetic_model_b(), build_synthetic_scaler_json(), fixture, Harsh, Rigorous ML Pipeline & Yukti Integration QA Test Suite. Target Services…, Generates scaler.json matching Yukti's schema from notebook Step 3. (+11 more)

### Community 33 - "Harsh: maintenance + imputation, fitted into main"
Cohesion: 0.40
Nodes (4): For Mudit, For Shreyansh, Harsh: maintenance + imputation, fitted into main, Settings

### Community 34 - "TestMalformedPayloadsAndTypeMismatch"
Cohesion: 0.13
Nodes (8): Verify numeric strings are coerced while boolean-as-float is audited., Verify unexpected extra fields are safely ignored by TelemetryPayload., Verify MQTT subscriber message handler discards malformed UTF-8, non-JSON, and…, Verify FastAPI REST endpoints strictly reject malformed JSON and out-of-spec…, Rigorous tests evaluating how the ingestion pipeline, schemas, and endpoints…, Verify that omitting mandatory fields raises Pydantic ValidationError., Verify non-numeric strings in numeric fields are rejected with ValidationError., TestMalformedPayloadsAndTypeMismatch

### Community 36 - "MultivariateAnomalyDetector"
Cohesion: 0.17
Nodes (7): MultivariateAnomalyDetector, Runs 1 Hz inference on the sliding window. Returns: (detected_anomaly_or_none,…, Stage 2 & 5: Multivariate Temporal Anomaly Detection Engine. Evaluates incoming…, Verifies that missing artifacts do not crash the backend and trigger…, DISCREPANCY CHECK: If scaler.json is corrupted or invalid, does…, TestMissingArtifactsHandling, ndarray

### Community 37 - "stream_telemetry"
Cohesion: 0.18
Nodes (10): get_latest_telemetry(), get_station_overview(), get_telemetry_history(), get, Hydration endpoint: gets the most recent telemetry packet., Retrieves recent rolling telemetry history for chart visualization., Summary overview for Station AGRA-01., Server-Sent Events (SSE) live telemetry and anomaly stream at 1 Hz. Directly… (+2 more)

### Community 38 - "test_sensor_health.py"
Cohesion: 0.43
Nodes (6): feed(), Harsh: predictive maintenance + imputation. Run: python -m pytest tests -q, Runs packets through a fresh SensorHealthService (no detector)., test_drift_detected_and_imputed(), test_normal_weather_stays_healthy(), test_storm_pauses_maintenance()

### Community 39 - "make_packet"
Cohesion: 0.16
Nodes (10): make_packet(), Generates 1 Hz telemetry reading with physical diurnal baseline and chaos…, Rigorous tests evaluating rapid packet bursts (50-100 packets): - Concurrency…, Verify ingesting 100 packets concurrently via asyncio.gather: - Lock serializes…, Verify store._telemetry_history adheres to its bounded deque capacity (1000…, Verify store.get_telemetry_history(limit=12) strictly honors the limit argument., MEMORY LEAK AUDIT TEST: store._anomalies is a standard Python dict with NO…, MEMORY LEAK AUDIT TEST: store._feedback_logs and sensor_health.accepted are… (+2 more)

### Community 40 - "ConfluenceEngine"
Cohesion: 0.14
Nodes (12): ConfluenceEngine, Layer 2.3: Classification Confluence & Confidence Scoring Engine. Reconciles…, Verify deterministic 4-quadrant Confluence Decision Matrix rules., Verify confidence scoring formula., test_confluence_confidence_scoring(), test_confluence_decision_matrix_rules(), Verifies that corrupted model files are caught gracefully and do not break…, Rigorously audits the Confluence Decision Matrix and Confidence formulas. (+4 more)

### Community 41 - "MultiScaleAnalyzer"
Cohesion: 0.18
Nodes (10): MultiScaleAnalyzer, Layer 2.1: Multi-Scale Multivariate Physical Analyzer (PRD Section 5.3 /…, Task 1.3: Verify isolated Multi-Scale Multivariate Analyzer functionality., test_multi_scale_analyzer_isolated(), make_telemetry_window(), Helper to generate sliding window of synthetic TelemetryPayload items., CRITICAL BUG DISCOVERY: In confluence_engine.py, self.model_a and self.model_b…, Verifies MultiScaleAnalyzer output vector contract with downstream models. (+2 more)

### Community 42 - "TestShapeCompatibilityAndFailureModes"
Cohesion: 0.17
Nodes (7): Harsh tests on ONNX dimension contracts and anomaly_detector error handling., Strict shape test: Yukti's ONNX autoencoder exports with fixed timesteps=12:…, BUG DISCOVERY: When window has 3 to 11 points, norm_matrix[-12:, :] returns…, When window length is 24 (> 12), norm_matrix[-12:, :] takes the last 12 points,…, FEATURE ORDER CONTRACT: Both training notebook and anomaly_detector.py must…, Verify dynamic_axes allows batch sizes 1, 2, and 8 when sequence length is…, TestShapeCompatibilityAndFailureModes

### Community 43 - "AnomalyEvaluation"
Cohesion: 0.20
Nodes (6): AnomalyEvaluation, Any, Tuple-compatible result that preserves the legacy event-only API., Rigorous tests evaluating live hot-plugged ML artifacts matching Yukti's schema., BUG DISCOVERY: scaler.json contains custom baseline means: T=30.5, RH=62.0,…, TestSyntheticArtifactsHotPlugging

### Community 45 - "AnomalyEvent"
Cohesion: 0.33
Nodes (5): AnomalyEvent, ShapAttribution, _epoch(), Sensor health: predictive maintenance + imputation, run once per packet from…, weather_event: pass the confluence engine's answer once it exists. Left as…

### Community 46 - ".analyze_window"
Cohesion: 0.36
Nodes (5): Any, Comprehensive multi-scale analysis over the current rolling telemetry window.…, Safely extracts a float field from a Pydantic model or dictionary., Computes numerical first derivatives (dT/dt, dP/dt, dRH/dt) and second…, Computes Pearson correlation coefficient rho_{T, RH} across the sliding window.…

## Knowledge Gaps
- **198 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 475 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `init_db()` connect `test_qa_backend_math_edge_cases.py` to `test_qa_edge_telemetry_stress.py`, `4. Member Task Details`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `Tasks:` connect `4. Member Task Details` to `test_qa_backend_math_edge_cases.py`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `TelemetryPayload` (e.g. with `InMemoryStore` and `MultivariateAnomalyDetector`) actually correct?**
  _`TelemetryPayload` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ConfluenceEngine` (e.g. with `TestConfluenceEngineEdgeCases` and `TestConfluenceConfidenceAndDecisionMatrix`) actually correct?**
  _`ConfluenceEngine` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `InMemoryStore` (e.g. with `AnomalyEvent` and `OperatorFeedback`) actually correct?**
  _`InMemoryStore` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nextConfig`, `name`, `version` to the rest of the system?**
  _198 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `useTelemetryStore` be split into smaller, more focused modules?**
  _Cohesion score 0.07056936647955092 - nodes in this community are weakly interconnected._