# Graph Report - SkyGuard_SIH  (2026-09-30)

## Corpus Check
- 91 files · ~250,674 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: .pkl 4, .pptx 3, (none) 2)

## Summary
- 1543 nodes · 2437 edges · 106 communities (97 shown, 9 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `38f0b579`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- useTelemetryStore
- TestChaosModesValidationAndInconsistencies
- db.py
- Detailed Minute-by-Minute Demo Script
- TestImputationThermodynamicEdgeCases
- InMemoryStore
- TelemetryPayload
- ConfluenceResult
- DriftTracker
- compilerOptions
- 📖 SkyGuard AI — Beginner's Step-by-Step Guide (Zero Jargon)
- test_qa_edge_telemetry_stress.py
- inject_fault
- get_anomaly
- MQTTSubscriber
- routers/sensor_health.py
- End-to-End ML Strategy: Split-Edge/Cloud Anomaly Detection & Telemetry Quality Assurance
- EdgeTelemetrySimulator
- SkyGuard AI: Split-Edge/Cloud Anomaly Detection Architecture
- anyio
- 4. Member Task Details
- 🎬 SkyGuard AI — 3-Minute Prototype Video Submission Master Guide
- next.config.mjs
- next-env.d.ts
- Product Requirements Document — SkyGuard AI
- CircularRingBuffer
- brandkit/SKILL.md
- dependencies
- 🌟 Key Architecture & Capabilities
- client.py
- SkyGuard AI MVP: Minimum User Flows & Operational Journeys
- synthetic_artifacts_dir
- Harsh: maintenance + imputation, fitted into main
- TestMalformedPayloadsAndTypeMismatch
- rules/graphify.md
- MultivariateAnomalyDetector
- stream_telemetry
- CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE
- make_packet
- ConfluenceEngine
- TestConfluenceEngineEdgeCases
- make_telemetry_window
- TestSyntheticArtifactsHotPlugging
- SKILL.md
- SensorHealthService
- CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION
- High-Agency Frontend Skill
- run_demo.py
- test_qa_backend_math_edge_cases.py
- Appendix B - Canonical Sources (read these before reinventing)
- Design Audit
- test_qa_ml_integration.py
- Analysis & Synthesis Instructions
- Agent Skill: Principal UI/UX Architect & Motion Choreographer (Awwwards-Tier)
- SKILL: Industrial Brutalism & Tactical Telemetry UI
- Design System: Taste Standard
- CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION
- 2. THE COMBINATORIAL VARIATION ENGINE
- 4. DESIGN ENGINEERING DIRECTIVES (Bias Correction)
- 10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know)
- tasteskill: Anti-Slop Frontend Skill
- CORE DIRECTIVE: AWWWARDS-LEVEL DESIGN ENGINEERING
- 22. STYLE VARIATION ENGINE
- Protocol: Premium Utilitarian Minimalism UI Architect
- 11. COMPONENT EXECUTION GUIDELINES
- 18. EXTRA CREATIVITY & IMPLEMENTATION EDGE
- 9. AI TELLS (Forbidden Patterns)
- 12. THE COMBINATORIAL VARIATION ENGINE
- 8. ANTI-AI-SLOP RULES
- 11. REDESIGN PROTOCOL
- 3. DEFAULT ARCHITECTURE & CONVENTIONS
- 6. PERFORMANCE & ACCESSIBILITY GUARDRAILS
- Full-Output Enforcement
- 33. CATEGORY-SPECIFIC BIAS
- 13. COLOR & MATERIAL RULES
- 4. HERO MINIMALISM RULES
- TestCorruptedArtifactsHandling
- 29. ANTI-AI-SLOP RULES
- 5. IMAGE COUNT & PAGE SLICING
- 0. BRIEF INFERENCE (Read the Room Before Anything Else)
- 12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)
- 5. CONTEXT-AWARE PROACTIVITY
- 8. DARK MODE PROTOCOL
- 21. MOBILE ANTI-AI-TELLS RULE
- 7. DIAL DEFINITIONS (Technical Reference)
- 33. DEFAULT SECTION PACKS
- 14. HERO MINIMALISM RULES
- 37. EXAMPLE INTERPRETATIONS
- 2. PLATFORM MODE RULE
- 37. EXAMPLE INTERPRETATIONS
- 15. DEFAULT SITE PACKS
- 20. EXAMPLE INTERPRETATIONS
- TestMultiScaleAnalyzerEdgeCases
- imagegen-frontend-web/SKILL.md
- MultiScaleAnalyzer
- get_simulator_status
- ingest_telemetry_packet
- edge_runner.py
- .analyze_window
- AnomalyEvaluation
- health_check
- submit_operator_feedback
- update_anomaly
- fixture
- Settings

## God Nodes (most connected - your core abstractions)
1. `TelemetryPayload` - 55 edges
2. `useTelemetryStore` - 42 edges
3. `CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE` - 39 edges
4. `CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION` - 39 edges
5. `make_packet()` - 33 edges
6. `ConfluenceEngine` - 29 edges
7. `InMemoryStore` - 28 edges
8. `MultivariateAnomalyDetector` - 27 edges
9. `AnomalyEvent` - 24 edges
10. `DriftTracker` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Tasks:` --references--> `init_db()`  [INFERRED]
  TASKS.md → backend/data/db.py
- `Tasks:` --references--> `MaintenanceResult`  [INFERRED]
  TASKS.md → frontend/src/lib/types.ts
- `Tasks:` --references--> `MaintenanceResult`  [INFERRED]
  TASKS.md → frontend/src/lib/types.ts
- `Tasks:` --references--> `ImputationResult`  [INFERRED]
  TASKS.md → frontend/src/lib/types.ts
- `Tasks:` --references--> `ImputationResult`  [INFERRED]
  TASKS.md → frontend/src/lib/types.ts

## Import Cycles
- None detected.

## Communities (106 total, 9 thin omitted)

### Community 0 - "useTelemetryStore"
Cohesion: 0.05
Nodes (78): name, private, version, EdgeSimulatorPage(), frontend_src_app_globals, metadata, RootLayout(), DashboardPage() (+70 more)

### Community 1 - "TestChaosModesValidationAndInconsistencies"
Cohesion: 0.14
Nodes (11): EdgeIMDBoundaryChecker, Layer 1.1 Local Deterministic Bounds & Rate-of-Change Checker Evaluates IMD…, Verify edge-side Layer 1.1 IMD boundary and step checks flag physical…, test_edge_imd_boundary_checker(), Rigorous tests evaluating the 5 chaos modes in client.py and extended simulator…, Verify all 5 chaos modes generate well-formed TelemetryPayload packets., HARSH ANALYSIS - Mode 1 Heat Spike: Tick 1 jumps +8°C instantaneously ->…, HARSH ANALYSIS - Mode 2 Capacitive Drift: In client.py, humidity jumps +15% in… (+3 more)

### Community 2 - "db.py"
Cohesion: 0.06
Nodes (61): AsyncSession, AnomalyIncident, Base, format_db_url(), get_recent_telemetry(), get_session(), init_db(), insert_anomaly() (+53 more)

### Community 3 - "Detailed Minute-by-Minute Demo Script"
Cohesion: 0.12
Nodes (15): Detailed Minute-by-Minute Demo Script, Live Hotkey Reference Table, Phase 1: Introduction & The Core Problem (0:00 – 0:45), Phase 2: Nominal Diurnal Baseline & Edge Verification (0:45 – 1:30), Phase 3: The True-Negative Severe Thunderstorm Squall (1:30 – 2:30), Phase 4: Capacitive Humidity Drift, SHAP Attribution & Data Repair (2:30 – 3:20), Phase 5: Frozen Sensor, Predictive Maintenance, & Conclusion (3:20 – 4:00), Pre-Recording Checklist (+7 more)

### Community 4 - "TestImputationThermodynamicEdgeCases"
Cohesion: 0.10
Nodes (11): Rigorous tests for Magnus-Tetens formulas and ImputationEngine., Verify thermodynamic identity: At RH = 100%, Dew Point == Temperature., dew_point must clamp RH between 0.001% and 100.0%., When Dew Point > Temperature (physical impossibility in non-supersaturated…, sat_vp(-243.12) hits the exact Magnus-B singularity, causing ZeroDivisionError., Document mathematical flaw: Below -243.12 C, the denominator (MAGNUS_B + t)…, At extreme cold (T <= -240 C), sat_vp(t) underflows to 0.0, causing…, Document mathematical flaw: In t_from_dewpoint, when a > MAGNUS_A, the… (+3 more)

### Community 5 - "InMemoryStore"
Cohesion: 0.07
Nodes (11): InMemoryStore, Any, Non-blocking enqueue for database persistence., Adds telemetry to in-memory history and enqueues async DB write without…, Adds anomaly to in-memory state and enqueues async DB write., Enqueues a predictive maintenance record for persistence., Blocks until pending persistence tasks have finished (useful for testing)., Clears in-memory history and active anomalies (useful for testing). (+3 more)

### Community 6 - "TelemetryPayload"
Cohesion: 0.25
Nodes (13): TelemetryPayload, calculate_dew_point(), IMDPhysicsRuleEngine, Stage 1: Deterministic Climatological & Physical Bounds Checker. Strictly based…, Evaluates current reading against IMD physics bounds and previous step. Returns…, Calculates dew point using the standard Magnus-Tetens approximation formula., Runs every telemetry source through one ordered processing pipeline., TelemetryIngestionService (+5 more)

### Community 7 - "ConfluenceResult"
Cohesion: 0.24
Nodes (6): ConfluenceResult, Any, Structured outcome of the Dual-Model Classification Confluence Decision Matrix…, Evaluates a window of telemetry records. If trained models are present, runs…, Calculates mathematical confidence score (0-100%). Formula: max(P_d, P_w) *…, dict

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
Cohesion: 0.19
Nodes (20): asyncio, lifespan(), AnomalyEvent, AnomalyUpdateRequest, FaultInjectionRequest, OperatorFeedback, PitchScriptStatus, ShapAttribution (+12 more)

### Community 12 - "inject_fault"
Cohesion: 0.22
Nodes (9): inject_fault(), post, Injects a physical sensor fault or environmental transient into the virtual…, Resets simulator to clean nominal weather with zero faults., Launches the 5-Minute Auto-Scenario Pitch Script: - T+0:00 (Baseline): Normal…, Cancels running pitch script., reset_simulator(), start_pitch_script() (+1 more)

### Community 13 - "get_anomaly"
Cohesion: 0.40
Nodes (5): get_anomaly(), list_anomalies(), get, Lists detected anomalies, sorted by most recent., Get detailed anomaly with SHAP feature attribution.

### Community 14 - "MQTTSubscriber"
Cohesion: 0.20
Nodes (8): MQTTSubscriber, Any, Client, ConnectFlags, DisconnectFlags, MQTTMessage, Properties, ReasonCode

### Community 15 - "routers/sensor_health.py"
Cohesion: 0.29
Nodes (7): ImputationAcceptRequest, accept_imputation(), get_maintenance(), get, post, Current drift state, baseline fit, and recently accepted imputations., Operator clicked "Accept & Impute" on the Data Repair tab.

### Community 16 - "End-to-End ML Strategy: Split-Edge/Cloud Anomaly Detection & Telemetry Quality Assurance"
Cohesion: 0.06
Nodes (31): 10.1 Model Architecture & Formulation, 10. Imputation & Correction Module (3.5), 11. Evaluation Metrics & Benchmark Targets, 12. Configuration Reference (`config/ml_pipeline.yaml`), 1. Executive Summary & Core Principles, 2. End-to-End ML Pipeline Architecture, 3.1 1.1 IMD Plausibility Check (Logical Filter), 3.2 1.2 Quantized PyOD (Lightweight Outlier Detection) (+23 more)

### Community 18 - "SkyGuard AI: Split-Edge/Cloud Anomaly Detection Architecture"
Cohesion: 0.07
Nodes (26): 1. Executive Summary & Design Principles, 1. Periodic Nominal Heartbeat, 2. Flagged Incident Packet (Context Burst), 2. High-Level Architecture Diagram, 3. Detailed Layer Explanation & Responsibilities, 4. End-to-End Data Pipeline Flow, 5.1 Layer 1.1: IMD Plausibility Check (Logical Filter), 5.2 Layer 1.2: 1D-CNN Temporal Autoencoder (ONNX / TFLite Micro) (+18 more)

### Community 19 - "anyio"
Cohesion: 0.11
Nodes (14): Any, Broadcasts an SSE message formatted as: event: <event_type> data: <json_string>, SSEBroadcastManager, anyio, HARSH ANALYSIS - Mode 3 Severe Thunderstorm: In client.py, storm applies -11…, Rigorous tests evaluating the SSE Broadcast Manager, connection lifecycle,…, Verify subscribing and unsubscribing cleanly tracks client count., Verify broadcasts are dispatched concurrently to all active subscriber queues. (+6 more)

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
Cohesion: 0.12
Nodes (11): CircularRingBuffer, In-memory circular ring buffer representing a 2-hour sliding window (120…, Returns the past `count` samples preceding the current reading., Verify in-memory circular ring buffer maintains 120-item capacity and retrieves…, test_circular_ring_buffer(), Rigorous tests evaluating the MQTT Incident Context Burst mechanism: - Burst…, Verify incident burst payload structure matches expected protocol specification., ARCHITECTURAL DEFECT TEST: When a burst arrives, mqtt_subscriber extracts ONLY… (+3 more)

### Community 27 - "brandkit/SKILL.md"
Cohesion: 0.05
Nodes (43): 1. Logo Cover, 1. Monogram + Meaning, 2 × 3 REFERENCE-STYLE LAYOUT, 2. Logo Construction, 2. Product Action, 3. Digital Application, 3. Metaphor Fusion, 4. Brand Essence (+35 more)

### Community 28 - "dependencies"
Cohesion: 0.07
Nodes (26): dependencies, clsx, lucide-react, next, react, react-dom, @react-three/drei, @react-three/fiber (+18 more)

### Community 29 - "🌟 Key Architecture & Capabilities"
Cohesion: 0.18
Nodes (10): 1.0 Edge Device Layer (ESP32 Deployment & Emulation), 1. Start the Backend API (FastAPI), 2.0 Cloud Analytics Layer (Structured Reasoning), 2. Start the Frontend Dashboard (Next.js 14), 3.0 Visualization & Alerting Layer (Operator Dashboard), 3. Optional Two-Laptop / Edge Simulator Demo, 🌟 Key Architecture & Capabilities, 🚀 Quick Start (Local Run) (+2 more)

### Community 30 - "client.py"
Cohesion: 0.11
Nodes (24): calculate_dew_point(), FaultState, format_status_badge(), main(), make_incident_burst(), parse_args(), print_banner(), SkyGuard AI — Laptop 1 Edge Weather Station Transmitter (AWS AGRA-01) Assigned… (+16 more)

### Community 31 - "SkyGuard AI MVP: Minimum User Flows & Operational Journeys"
Cohesion: 0.29
Nodes (6): 1. Primary Flow: Edge Filtering, Confluence Reasoning, & XAI Diagnostics, 2. Secondary Flow: Predictive Maintenance & Sensor Health (3.4), 3. Tertiary Flow: Imputation & Data Correction (3.5), 4. Live Demonstration Flow: The 5-Minute Pitch Script, Primary Sequence Diagram, SkyGuard AI MVP: Minimum User Flows & Operational Journeys

### Community 32 - "synthetic_artifacts_dir"
Cohesion: 0.15
Nodes (12): build_synthetic_autoencoder_onnx(), __init__(), build_synthetic_model_a(), build_synthetic_model_b(), build_synthetic_scaler_json(), fixture, Generates scaler.json matching Yukti's schema from notebook Step 3., Generates Model A (Weather Classifier) returning classes ['nominal', 'squall']. (+4 more)

### Community 33 - "Harsh: maintenance + imputation, fitted into main"
Cohesion: 0.40
Nodes (4): For Mudit, For Shreyansh, Harsh: maintenance + imputation, fitted into main, Settings

### Community 34 - "TestMalformedPayloadsAndTypeMismatch"
Cohesion: 0.12
Nodes (9): Verify numeric strings are coerced while boolean-as-float is audited., Verify unexpected extra fields are safely ignored by TelemetryPayload., CRITICAL VULNERABILITY TEST: Evaluate what happens when NaN or Inf are injected…, Verify MQTT subscriber message handler discards malformed UTF-8, non-JSON, and…, Verify FastAPI REST endpoints strictly reject malformed JSON and out-of-spec…, Rigorous tests evaluating how the ingestion pipeline, schemas, and endpoints…, Verify that omitting mandatory fields raises Pydantic ValidationError., Verify non-numeric strings in numeric fields are rejected with ValidationError. (+1 more)

### Community 36 - "MultivariateAnomalyDetector"
Cohesion: 0.20
Nodes (6): MultivariateAnomalyDetector, Runs 1 Hz inference on the sliding window. Returns: (detected_anomaly_or_none,…, Stage 2 & 5: Multivariate Temporal Anomaly Detection Engine. Evaluates incoming…, Verifies that missing artifacts do not crash the backend and trigger…, TestMissingArtifactsHandling, ndarray

### Community 37 - "stream_telemetry"
Cohesion: 0.18
Nodes (10): get_latest_telemetry(), get_station_overview(), get_telemetry_history(), get, Hydration endpoint: gets the most recent telemetry packet., Retrieves recent rolling telemetry history for chart visualization., Summary overview for Station AGRA-01., Server-Sent Events (SSE) live telemetry and anomaly stream at 1 Hz. Directly… (+2 more)

### Community 38 - "CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE"
Cohesion: 0.06
Nodes (34): 10. IMAGE-FIRST CODEX WEBSITE WORKFLOW, 11. WHEN TO TRIGGER IMAGE GENERATION FIRST, 13. WEBSITE REFERENCE RULE, 15. RESPONSIVE FIRST-VIEW RULE, 16. ANTI-NESTED-BOX RULE, 17. REDUCE MICRO-UI CLUTTER RULE, 18. SECTION IMAGE GENERATION RULE, 19. WEBSITE IMAGE SYSTEM RULE (+26 more)

### Community 39 - "make_packet"
Cohesion: 0.12
Nodes (14): make_packet(), Generates 1 Hz telemetry reading with physical diurnal baseline and chaos…, Verify standard edge telemetry packet passes through backend ingestion cleanly., Verify all 5 transmitter modes generate physically consistent baseline and…, test_mqtt_payload_uses_existing_ingestion_pipeline(), test_transmitter_fault_packets(), Rigorous tests evaluating rapid packet bursts (50-100 packets): - Concurrency…, Verify ingesting 100 packets concurrently via asyncio.gather: - Lock serializes… (+6 more)

### Community 40 - "ConfluenceEngine"
Cohesion: 0.14
Nodes (11): ConfluenceEngine, Layer 2.3: Classification Confluence & Confidence Scoring Engine. Reconciles…, Attempts to load Model A (Weather) and Model B (Defect) from artifacts or root.…, Verify deterministic 4-quadrant Confluence Decision Matrix rules., Verify confidence scoring formula., test_confluence_confidence_scoring(), test_confluence_decision_matrix_rules(), Rigorously audits the Confluence Decision Matrix and Confidence formulas. (+3 more)

### Community 41 - "TestConfluenceEngineEdgeCases"
Cohesion: 0.15
Nodes (7): Rigorous verification of Layer 2.3 ConfluenceEngine and confidence score…, Verify confidence formula: conf_pct = max(P_D, P_W) * (1.0 - (1.0 - |P_D -…, Test negative, super-unity, and NaN probability handling., Verify exact quadrant boundaries for 70% and 30% thresholds: - Weather Event:…, Document critical bug: evaluate_window uses getattr(curr, key) directly without…, Test resilience when an object has an attribute explicitly set to None., TestConfluenceEngineEdgeCases

### Community 42 - "make_telemetry_window"
Cohesion: 0.15
Nodes (9): make_telemetry_window(), Helper to generate sliding window of synthetic TelemetryPayload items., Harsh tests on ONNX dimension contracts and anomaly_detector error handling., Strict shape test: Yukti's ONNX autoencoder exports with fixed timesteps=12:…, BUG DISCOVERY: When window has 3 to 11 points, norm_matrix[-12:, :] returns…, When window length is 24 (> 12), norm_matrix[-12:, :] takes the last 12 points,…, FEATURE ORDER CONTRACT: Both training notebook and anomaly_detector.py must…, Verify dynamic_axes allows batch sizes 1, 2, and 8 when sequence length is… (+1 more)

### Community 43 - "TestSyntheticArtifactsHotPlugging"
Cohesion: 0.25
Nodes (4): Rigorous tests evaluating live hot-plugged ML artifacts matching Yukti's schema., BUG DISCOVERY: scaler.json contains custom baseline means: T=30.5, RH=62.0,…, Verifies that ConfluenceEngine evaluate_window actively calls loaded Model A…, TestSyntheticArtifactsHotPlugging

### Community 45 - "SensorHealthService"
Cohesion: 0.08
Nodes (15): find_column(), _fit_line(), ImputationEngine, _ok(), Fit RH-vs-T and pressure stats from the normal-weather CSV., _slope(), weather_event: pass the confluence engine's answer once it exists. Left as…, SensorHealthService (+7 more)

### Community 46 - "CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION"
Cohesion: 0.06
Nodes (34): 10. DEVICE MOCKUP FRAME RULE, 11. ONBOARDING FLOW RULE, 12. FIRST SCREEN CLEANLINESS RULE, 13. SAFE AREA AND SYSTEM REGION RULE, 14. NAVIGATION RULE, 15. CLEAN LAYOUT RULE, 16. CREATIVE IMAGE DIRECTION RULE, 17. BACKGROUND TEXTURE AND SURFACE RULE (+26 more)

### Community 47 - "High-Agency Frontend Skill"
Cohesion: 0.06
Nodes (30): 10. FINAL PRE-FLIGHT CHECK, 1. ACTIVE BASELINE CONFIGURATION, 2. DEFAULT ARCHITECTURE & CONVENTIONS, 3. DESIGN ENGINEERING DIRECTIVES (Bias Correction), 4. CREATIVE PROACTIVITY (Anti-Slop Implementation), 5. PERFORMANCE GUARDRAILS, 6. TECHNICAL REFERENCE (Dial Definitions), 7. AI TELLS (Forbidden Patterns) (+22 more)

### Community 48 - "run_demo.py"
Cohesion: 0.12
Nodes (16): atexit, calc_dew_point(), EdgeStationRunner, Reads non-blocking keypress if available on Windows., Magnus-Tetens thermodynamic dew point formula., pathlib, cleanup(), is_port_in_use() (+8 more)

### Community 49 - "test_qa_backend_math_edge_cases.py"
Cohesion: 0.12
Nodes (28): dew_point(), Imputation: estimates what a faulty sensor should read, using the sensors that…, rh_from_dewpoint(), sat_vp(), t_from_dewpoint(), Predictive maintenance: tracks slow sensor drift and estimates when a sensor…, _epoch(), Sensor health: predictive maintenance + imputation, run once per packet from… (+20 more)

### Community 50 - "Appendix B - Canonical Sources (read these before reinventing)"
Cohesion: 0.09
Nodes (21): APPENDICES - Real Source-Backed Reference Material, Appendix A - Install Commands per Design System, Appendix B - Canonical Sources (read these before reinventing), Appendix C - Apple Liquid Glass: Honest Web Approximation, Apple Liquid Glass (Apple platforms only), Atlassian, Bootstrap, Carbon (+13 more)

### Community 51 - "Design Audit"
Cohesion: 0.10
Nodes (19): Code Quality, Color and Surfaces, Component Patterns, Content, Design Audit, Fix Priority, How This Works, Iconography (+11 more)

### Community 52 - "test_qa_ml_integration.py"
Cohesion: 0.12
Nodes (15): anyio_backend(), fixture, End-to-End System Integration Test (Hanswarup — TASKS.md Task 1.4) Verifies…, Verify FastAPI REST API endpoints using TestClient., test_e2e_fastapi_rest_endpoints(), Harsh, Rigorous ML Pipeline & Yukti Integration QA Test Suite. Target Services…, fastapi_testclient, joblib (+7 more)

### Community 53 - "Analysis & Synthesis Instructions"
Cohesion: 0.11
Nodes (18): 1. Define the Atmosphere, 2. Map the Color Palette, 3. Establish Typography Rules, 4. Define the Hero Section, 5. Describe Component Stylings, 6. Define Layout Principles, 7. Define Responsive Rules, 8. Encode Motion Philosophy (+10 more)

### Community 54 - "Agent Skill: Principal UI/UX Architect & Motion Choreographer (Awwwards-Tier)"
Cohesion: 0.11
Nodes (17): 1. Meta Information & Core Directive, 2. THE "ABSOLUTE ZERO" DIRECTIVE (STRICT ANTI-PATTERNS), 3. THE CREATIVE VARIANCE ENGINE, 4. HAPTIC MICRO-AESTHETICS (COMPONENT MASTERY), 5. MOTION CHOREOGRAPHY (FLUID DYNAMICS), 6. PERFORMANCE GUARDRAILS, 7. EXECUTION PROTOCOL, 8. PRE-OUTPUT CHECKLIST (+9 more)

### Community 55 - "SKILL: Industrial Brutalism & Tactical Telemetry UI"
Cohesion: 0.12
Nodes (16): 1. Skill Meta, 2.1 Swiss Industrial Print, 2.2 Tactical Telemetry & CRT Terminal, 2. Visual Archetypes, 3.1 Macro-Typography (Structural Headers), 3.2 Micro-Typography (Data & Telemetry), 3.3 Textural Contrast (Artistic Disruption), 3. Typographic Architecture (+8 more)

### Community 56 - "Design System: Taste Standard"
Cohesion: 0.13
Nodes (14): 1. Visual Theme & Atmosphere, 2. Color Palette & Roles, 3. Typography Rules, 4. Component Stylings, 5. Hero Section, 6. Layout Principles, 7. Responsive Rules, 8. Motion & Interaction (Code-Phase Intent) (+6 more)

### Community 57 - "CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION"
Cohesion: 0.14
Nodes (14): 10. SECTION RHYTHM RULE, 12. DENSITY & SPACING DISCIPLINE, 14. IMAGE / MEDIA DIRECTION, 16. MULTI-IMAGE CONSISTENCY RULE, 17. CLARITY CHECK, 19. RESPONSE BEHAVIOR, 1. ACTIVE BASELINE CONFIGURATION, 21. FINAL GOAL (+6 more)

### Community 58 - "2. THE COMBINATORIAL VARIATION ENGINE"
Cohesion: 0.14
Nodes (14): 2. THE COMBINATORIAL VARIATION ENGINE, Background Character, Background Mode (per-section), Composition Anchor (per-section), CTA Variation, Hero Architecture, Hero Scale (per-page), Motion-Implied Language (+6 more)

### Community 59 - "4. DESIGN ENGINEERING DIRECTIVES (Bias Correction)"
Cohesion: 0.17
Nodes (12): 4.10 Quotes & Testimonials, 4.11 Page Theme Lock (Light / Dark Mode Consistency), 4.1 Typography, 4.2 Color Calibration, 4.3 Layout Diversification, 4.4 Materiality, Shadows, Cards, 4.5 Interactive UI States, 4.6 Data & Form Patterns (+4 more)

### Community 60 - "10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know)"
Cohesion: 0.20
Nodes (10): 10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know), Animation Library Choice, Cards & Containers, Galleries & Media, Hero Paradigms, Layout & Grids, Micro-Interactions & Effects, Navigation & Menus (+2 more)

### Community 61 - "tasteskill: Anti-Slop Frontend Skill"
Cohesion: 0.20
Nodes (10): 13. OUT OF SCOPE, 14. FINAL PRE-FLIGHT CHECK, 1.A Dial Inference (design read → dial values), 1.B Use-Case Presets, 1.C How the Dials Drive Output, 1. THE THREE DIALS (Core Configuration), 2.A When to reach for a real design system (use official packages), 2.B When the brief is an aesthetic, not a system (+2 more)

### Community 62 - "CORE DIRECTIVE: AWWWARDS-LEVEL DESIGN ENGINEERING"
Cohesion: 0.20
Nodes (9): 1. PYTHON-DRIVEN TRUE RANDOMIZATION (BREAKING THE LOOP), 2. AIDA STRUCTURE & SPACING, 3. HERO ARCHITECTURE & THE 2-LINE IRON RULE, 4. THE GAPLESS BENTO GRID, 5. ADVANCED GSAP MOTION & HOVER PHYSICS, 6. COMPONENT ARSENAL & CREATIVITY, 7. CONTENT, ASSETS & STRICT BANS, 8. MANDATORY PRE-FLIGHT <design_plan> (+1 more)

### Community 63 - "22. STYLE VARIATION ENGINE"
Cohesion: 0.20
Nodes (10): 22. STYLE VARIATION ENGINE, Decorative Asset Set, Image Art Direction Bias, Motion-Implied Language, Palette Logic, Signature Component Set, Structure Bias, Texture / Surface Treatment (+2 more)

### Community 64 - "Protocol: Premium Utilitarian Minimalism UI Architect"
Cohesion: 0.20
Nodes (9): 1. Protocol Overview, 2. Absolute Negative Constraints (Banned Elements), 3. Typographic Architecture, 4. Color Palette (Warm Monochrome + Spot Pastels), 5. Component Specifications, 6. Iconography & Imagery Directives, 7. Subtle Motion & Micro-Animations, 8. Execution Protocol (+1 more)

### Community 65 - "11. COMPONENT EXECUTION GUIDELINES"
Cohesion: 0.22
Nodes (9): 11. COMPONENT EXECUTION GUIDELINES, 3D Cascading Card Deck, Diagonal Staggered Square Masonry, Hover-Accordion Slice Layout, Off-Grid Editorial Layout, Pristine Gapless Bento Grid, Product UI Panel Stack, Turning Polaroid Arc (+1 more)

### Community 66 - "18. EXTRA CREATIVITY & IMPLEMENTATION EDGE"
Cohesion: 0.22
Nodes (9): 18. EXTRA CREATIVITY & IMPLEMENTATION EDGE, Composition variety check, Conversion focus, Cross-section contrast, CTA specificity, Cultural / tonal alignment, Data-viz restraint, Image variety inside one comp (+1 more)

### Community 67 - "9. AI TELLS (Forbidden Patterns)"
Cohesion: 0.25
Nodes (8): 9.A Visual & CSS, 9. AI TELLS (Forbidden Patterns), 9.B Typography, 9.C Layout & Spacing, 9.D Content & Data ("Jane Doe" Effect), 9.E External Resources & Components, 9.F Production-Test Tells (banned outright), 9.G EM-DASH BAN (the single most-violated Tell)

### Community 68 - "12. THE COMBINATORIAL VARIATION ENGINE"
Cohesion: 0.25
Nodes (8): 12. THE COMBINATORIAL VARIATION ENGINE, Background Character, Hero Architecture, Motion-Implied Language, Section System, Signature Component Set, Theme Paradigm, Typography Character

### Community 69 - "8. ANTI-AI-SLOP RULES"
Cohesion: 0.25
Nodes (8): 8. ANTI-AI-SLOP RULES, Carousel / marquee slop (layout), Content slop, Data / KPI slop, Density slop, Layout slop, Typography slop, Visual slop

### Community 70 - "11. REDESIGN PROTOCOL"
Cohesion: 0.29
Nodes (7): 11.A Detect the Mode (first action), 11.B Audit Before Touching, 11.C Preservation Rules, 11.D Modernisation Levers (priority order), 11.E Decision Tree: Targeted Evolution vs Full Redesign, 11.F What Never Changes Silently, 11. REDESIGN PROTOCOL

### Community 71 - "3. DEFAULT ARCHITECTURE & CONVENTIONS"
Cohesion: 0.29
Nodes (7): 3.A Stack, 3.B State, 3.C Icons, 3.D Emoji Policy, 3. DEFAULT ARCHITECTURE & CONVENTIONS, 3.E Responsiveness & Layout Mechanics, 3.F Dependency Verification (mandatory)

### Community 72 - "6. PERFORMANCE & ACCESSIBILITY GUARDRAILS"
Cohesion: 0.29
Nodes (7): 6.A Hardware Acceleration, 6.B Reduced Motion (mandatory), 6.C Dark Mode (mandatory for any consumer-facing page), 6.D Core Web Vitals Targets, 6.E DOM Cost, 6.F Z-Index Restraint, 6. PERFORMANCE & ACCESSIBILITY GUARDRAILS

### Community 73 - "Full-Output Enforcement"
Cohesion: 0.29
Nodes (6): Banned Output Patterns, Baseline, Execution Process, Full-Output Enforcement, Handling Long Outputs, Quick Check

### Community 74 - "33. CATEGORY-SPECIFIC BIAS"
Cohesion: 0.29
Nodes (7): 33. CATEGORY-SPECIFIC BIAS, Commerce, Fintech, Health / Fitness, Productivity, Social, Wellness / Lifestyle

### Community 75 - "13. COLOR & MATERIAL RULES"
Cohesion: 0.29
Nodes (7): 13. COLOR & MATERIAL RULES, Background Confidence Rule, Background-image harmony, Gradient Discipline, Materiality, Palette Discipline, Strong guidance

### Community 76 - "4. HERO MINIMALISM RULES"
Cohesion: 0.29
Nodes (7): 4. HERO MINIMALISM RULES, Absolute Hero Rules, Graphic Restraint, Headline Rule, Hero Composition Bias, Pre-output check, Typography Execution

### Community 77 - "TestCorruptedArtifactsHandling"
Cohesion: 0.29
Nodes (3): Verifies that corrupted model files are caught gracefully and do not break…, If scaler.json is corrupted or invalid, anomaly_detector.py gracefully falls…, TestCorruptedArtifactsHandling

### Community 78 - "29. ANTI-AI-SLOP RULES"
Cohesion: 0.33
Nodes (6): 29. ANTI-AI-SLOP RULES, Content slop, Density slop, Layout slop, Typography slop, Visual slop

### Community 79 - "5. IMAGE COUNT & PAGE SLICING"
Cohesion: 0.33
Nodes (6): 5. IMAGE COUNT & PAGE SLICING, Continuity Rule, Counting rule, Format, Section size variety, THIS IS THE PRIMARY OUTPUT RULE

### Community 80 - "0. BRIEF INFERENCE (Read the Room Before Anything Else)"
Cohesion: 0.40
Nodes (5): 0.A Read these signals first, 0.B Output a one-line "Design Read" before generating, 0. BRIEF INFERENCE (Read the Room Before Anything Else), 0.C If the brief is ambiguous, ask one question, do not guess, 0.D Anti-Default Discipline

### Community 81 - "12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)"
Cohesion: 0.40
Nodes (5): 12.A File Location, 12.B Required Frontmatter, 12.C Required Body Sections, 12.D Block-Library Discipline, 12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)

### Community 82 - "5. CONTEXT-AWARE PROACTIVITY"
Cohesion: 0.40
Nodes (5): 5.A Sticky-Stack - Canonical Skeleton, 5.B Horizontal-Pan - Canonical Skeleton, 5.C Scroll-Reveal Stagger - Canonical Skeleton (lighter alternative), 5. CONTEXT-AWARE PROACTIVITY, 5.D Forbidden Animation Patterns

### Community 83 - "8. DARK MODE PROTOCOL"
Cohesion: 0.40
Nodes (5): 8.A Token Strategy (pick one, stick to it), 8.B Do Not Prescribe Specific Colors Here, 8.C Default Mode, 8.D Test in Both Modes Before Finishing, 8. DARK MODE PROTOCOL

### Community 84 - "21. MOBILE ANTI-AI-TELLS RULE"
Cohesion: 0.40
Nodes (5): 21. MOBILE ANTI-AI-TELLS RULE, Copy AI tells, Layout AI tells, UI clutter tells, Visual AI tells

### Community 85 - "7. DIAL DEFINITIONS (Technical Reference)"
Cohesion: 0.50
Nodes (4): 7. DIAL DEFINITIONS (Technical Reference), DESIGN_VARIANCE (Level 1-10), MOTION_INTENSITY (Level 1-10), VISUAL_DENSITY (Level 1-10)

### Community 86 - "33. DEFAULT SECTION PACKS"
Cohesion: 0.50
Nodes (4): 12-section pack, 33. DEFAULT SECTION PACKS, 4-section pack, 8-section pack

### Community 87 - "14. HERO MINIMALISM RULES"
Cohesion: 0.50
Nodes (4): 14. HERO MINIMALISM RULES, Absolute Hero Rules, Headline Rule, Hero Cleanliness Rule

### Community 88 - "37. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 37. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 89 - "2. PLATFORM MODE RULE"
Cohesion: 0.50
Nodes (4): 2. PLATFORM MODE RULE, Android-native premium, Cross-platform premium neutral, iOS-native premium

### Community 90 - "37. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 37. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 91 - "15. DEFAULT SITE PACKS"
Cohesion: 0.50
Nodes (4): 12-section pack, 15. DEFAULT SITE PACKS, 4-section pack, 8-section pack

### Community 92 - "20. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 20. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 93 - "TestMultiScaleAnalyzerEdgeCases"
Cohesion: 0.17
Nodes (7): Zero variance in temperature or humidity must return 0.0 correlation without…, Document flaw: NaN or Inf inside window propagates silently into correlation…, Document flaw: compute_derivatives relies on list indexing window[-1] -…, Verify boundary condition: rho_{T, RH} > 0.0 and abs(dP/dt) < 2.0., Rigorous mathematical tests for Layer 2.1 MultiScaleAnalyzer., Test window sizes: 0, 1, 2, 5, 12, 100 points., TestMultiScaleAnalyzerEdgeCases

### Community 95 - "MultiScaleAnalyzer"
Cohesion: 0.24
Nodes (7): MultiScaleAnalyzer, Layer 2.1: Multi-Scale Multivariate Physical Analyzer (PRD Section 5.3 /…, Task 1.3: Verify isolated Multi-Scale Multivariate Analyzer functionality., test_multi_scale_analyzer_isolated(), Verifies MultiScaleAnalyzer output vector contract with downstream models., Under normal physics, rho(T, RH) is strongly negative (-0.7 to -0.9). When RH…, TestMultiScaleAnalyzerFeatureCompatibility

### Community 96 - "get_simulator_status"
Cohesion: 0.67
Nodes (3): get_simulator_status(), get, Returns current edge simulator status and pitch script progress.

### Community 97 - "ingest_telemetry_packet"
Cohesion: 0.67
Nodes (3): ingest_telemetry_packet(), post, Direct ingestion endpoint for external edge devices / edge_runner.py scripts.…

### Community 98 - "edge_runner.py"
Cohesion: 0.22
Nodes (8): argparse, Colors, main(), SkyGuard AI — Standalone Edge Station Telemetry Streamer & Physics Validator…, msvcrt, time, urllib_error, urllib_request

### Community 99 - ".analyze_window"
Cohesion: 0.36
Nodes (5): Any, Comprehensive multi-scale analysis over the current rolling telemetry window.…, Safely extracts a float field from a Pydantic model or dictionary., Computes numerical first derivatives (dT/dt, dP/dt, dRH/dt) and second…, Computes Pearson correlation coefficient rho_{T, RH} across the sliding window.…

### Community 100 - "AnomalyEvaluation"
Cohesion: 0.50
Nodes (3): AnomalyEvaluation, Any, Tuple-compatible result that preserves the legacy event-only API.

### Community 101 - "health_check"
Cohesion: 0.67
Nodes (3): health_check(), get, root()

### Community 102 - "submit_operator_feedback"
Cohesion: 0.67
Nodes (3): post, Operator Active Learning Feedback loop. Flags false alarms or confirms faults…, submit_operator_feedback()

### Community 103 - "update_anomaly"
Cohesion: 0.67
Nodes (3): Operator action: acknowledge, resolve, or mark an anomaly., update_anomaly(), patch

## Knowledge Gaps
- **638 isolated node(s):** `Colors`, `nextConfig`, `name`, `version`, `private` (+633 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 942 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `init_db()` connect `db.py` to `test_qa_backend_math_edge_cases.py`, `test_qa_edge_telemetry_stress.py`, `test_qa_ml_integration.py`, `4. Member Task Details`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `Tasks:` connect `4. Member Task Details` to `db.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `TelemetryPayload` (e.g. with `InMemoryStore` and `ingest_telemetry_packet()`) actually correct?**
  _`TelemetryPayload` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Colors`, `nextConfig`, `name` to the rest of the system?**
  _638 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `useTelemetryStore` be split into smaller, more focused modules?**
  _Cohesion score 0.05293040293040293 - nodes in this community are weakly interconnected._
- **Should `TestChaosModesValidationAndInconsistencies` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06349206349206349 - nodes in this community are weakly interconnected._