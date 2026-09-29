# Graph Report - SkyGuard_SIH  (2026-09-29)

## Corpus Check
- 54 files · ~14,200 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 515 nodes · 1115 edges · 25 communities (21 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Next.js Frontend & 3D Twin
- Edge Station Simulator & Chaos Client
- Database Persistence (PostgreSQL & SQLite)
- Frontend NPM Dependencies
- Imputation & Sensor Recovery Engine
- In-Memory Telemetry Ring Store
- IMD Physical Plausibility Rules
- Confluence Decision Matrix
- Predictive Maintenance EWMA Drift
- Frontend TypeScript Configuration
- Multivariate Anomaly Detection & SHAP
- Backend Ingestion & Core Services
- Simulator & Injection REST Router
- Anomaly & Feedback REST Router
- MQTT Broker Subscriber Service
- Telemetry Stream & SSE Router
- Sensor Health Service Orchestrator
- Edge Telemetry Generator
- FastAPI Main Application Lifecycle
- Machine Learning Models & Scalers
- Sensor Health & Imputation API
- Dataset Generation & Fault Synthesis
- Docker & Infrastructure
- Database & Confluence Unit Tests

## God Nodes (most connected - your core abstractions)
1. `useTelemetryStore` - 42 edges
2. `TelemetryPayload` - 39 edges
3. `InMemoryStore` - 22 edges
4. `AnomalyEvent` - 21 edges
5. `react` - 20 edges
6. `DriftTracker` - 18 edges
7. `lucide-react` - 16 edges
8. `compilerOptions` - 16 edges
9. `ShapAttribution` - 14 edges
10. `SensorHealthService` - 14 edges

## Surprising Connections (you probably didn't know these)
- `ShapAttribution` --uses--> `IMDPhysicsRuleEngine`  [INFERRED]
  backend/models/schemas.py → backend/services/rule_engine.py
- `ShapAttribution` --uses--> `SensorHealthService`  [INFERRED]
  backend/models/schemas.py → backend/services/sensor_health.py
- `AnomalyEvaluation` --uses--> `AnomalyEvent`  [INFERRED]
  backend/services/anomaly_detector.py → backend/models/schemas.py
- `MultivariateAnomalyDetector` --uses--> `AnomalyEvent`  [INFERRED]
  backend/services/anomaly_detector.py → backend/models/schemas.py
- `MultivariateAnomalyDetector` --uses--> `TelemetryPayload`  [INFERRED]
  backend/services/anomaly_detector.py → backend/models/schemas.py

## Import Cycles
- None detected.

## Communities (25 total, 4 thin omitted)

### Community 0 - "Next.js Frontend & 3D Twin"
Cohesion: 0.07
Nodes (60): EdgeSimulatorPage(), frontend_src_app_globals, metadata, RootLayout(), DashboardPage(), TimeSeriesChart(), Header(), AnomalyCard() (+52 more)

### Community 1 - "Edge Station Simulator & Chaos Client"
Cohesion: 0.06
Nodes (47): argparse, calculate_dew_point(), CircularRingBuffer, EdgeIMDBoundaryChecker, FaultState, format_status_badge(), main(), make_incident_burst() (+39 more)

### Community 2 - "Database Persistence (PostgreSQL & SQLite)"
Cohesion: 0.11
Nodes (41): asyncio, AsyncSession, AnomalyIncident, Base, format_db_url(), get_recent_telemetry(), get_session(), init_db() (+33 more)

### Community 3 - "Frontend NPM Dependencies"
Cohesion: 0.05
Nodes (42): dependencies, clsx, lucide-react, next, react, react-dom, @react-three/drei, @react-three/fiber (+34 more)

### Community 4 - "Imputation & Sensor Recovery Engine"
Cohesion: 0.10
Nodes (24): dew_point(), find_column(), _fit_line(), ImputationEngine, _ok(), Imputation: estimates what a faulty sensor should read, using the sensors that…, Fit RH-vs-T and pressure stats from the normal-weather CSV., rh_from_dewpoint() (+16 more)

### Community 5 - "In-Memory Telemetry Ring Store"
Cohesion: 0.11
Nodes (9): InMemoryStore, Any, Non-blocking enqueue for database persistence., Adds telemetry to in-memory history and enqueues async DB write without…, Adds anomaly to in-memory state and enqueues async DB write., Enqueues a predictive maintenance record for persistence., Blocks until pending persistence tasks have finished (useful for testing)., In-memory operational store paired with non-blocking asynchronous persistence.… (+1 more)

### Community 6 - "IMD Physical Plausibility Rules"
Cohesion: 0.21
Nodes (15): TelemetryPayload, calculate_dew_point(), IMDPhysicsRuleEngine, Stage 1: Deterministic Climatological & Physical Bounds Checker. Strictly based…, Evaluates current reading against IMD physics bounds and previous step. Returns…, Calculates dew point using the standard Magnus-Tetens approximation formula., Runs every telemetry source through one ordered processing pipeline., TelemetryIngestionService (+7 more)

### Community 7 - "Confluence Decision Matrix"
Cohesion: 0.13
Nodes (14): ConfluenceEngine, ConfluenceResult, Any, Structured outcome of the Dual-Model Classification Confluence Decision Matrix…, Evaluates a window of telemetry records. If trained models are present, runs…, Layer 2.3: Classification Confluence & Confidence Scoring Engine. Reconciles…, Attempts to load Model A (Weather) and Model B (Defect) from artifacts. If…, Calculates mathematical confidence score (0-100%) according to Layer 2.3:… (+6 more)

### Community 8 - "Predictive Maintenance EWMA Drift"
Cohesion: 0.19
Nodes (6): DriftTracker, Report current state without feeding a new residual., Use baseline statistics instead of a live warmup (all stations)., Keep the live warmup, but never assume less noise than this., Call after a technician recalibrates the sensor., _SensorState

### Community 9 - "Frontend TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 10 - "Multivariate Anomaly Detection & SHAP"
Cohesion: 0.20
Nodes (8): ShapAttribution, AnomalyEvaluation, MultivariateAnomalyDetector, Any, Runs 1 Hz inference on the sliding window. Returns: (detected_anomaly_or_none,…, Tuple-compatible result that preserves the legacy event-only API., Stage 2 & 5: Multivariate Temporal Anomaly Detection Engine. Evaluates incoming…, ndarray

### Community 11 - "Backend Ingestion & Core Services"
Cohesion: 0.23
Nodes (10): Config, Settings, BaseSettings, json, logging, numpy, pydantic_settings, time (+2 more)

### Community 12 - "Simulator & Injection REST Router"
Cohesion: 0.21
Nodes (12): FaultInjectionRequest, PitchScriptStatus, inject_fault(), post, Injects a physical sensor fault or environmental transient into the virtual…, Resets simulator to clean nominal weather with zero faults., Launches the 5-Minute Auto-Scenario Pitch Script: - T+0:00 (Baseline): Normal…, Cancels running pitch script. (+4 more)

### Community 13 - "Anomaly & Feedback REST Router"
Cohesion: 0.17
Nodes (14): AnomalyUpdateRequest, OperatorFeedback, get_anomaly(), list_anomalies(), get, post, Lists detected anomalies, sorted by most recent., Get detailed anomaly with SHAP feature attribution. (+6 more)

### Community 14 - "MQTT Broker Subscriber Service"
Cohesion: 0.20
Nodes (8): MQTTSubscriber, Any, Client, ConnectFlags, DisconnectFlags, MQTTMessage, Properties, ReasonCode

### Community 15 - "Telemetry Stream & SSE Router"
Cohesion: 0.19
Nodes (12): StationOverview, get_latest_telemetry(), get_station_overview(), get_telemetry_history(), get, Hydration endpoint: gets the most recent telemetry packet., Retrieves recent rolling telemetry history for chart visualization., Summary overview for Station AGRA-01. (+4 more)

### Community 16 - "Sensor Health Service Orchestrator"
Cohesion: 0.24
Nodes (4): _epoch(), weather_event: pass the confluence engine's answer once it exists. Left as…, SensorHealthService, deque

### Community 18 - "FastAPI Main Application Lifecycle"
Cohesion: 0.28
Nodes (8): health_check(), lifespan(), get, root(), contextlib, FastAPI, fastapi_middleware_cors, uvicorn

### Community 19 - "Machine Learning Models & Scalers"
Cohesion: 0.25
Nodes (4): Any, Broadcasts an SSE message formatted as: event: <event_type> data: <json_string>, SSEBroadcastManager, Queue

### Community 20 - "Sensor Health & Imputation API"
Cohesion: 0.29
Nodes (7): ImputationAcceptRequest, accept_imputation(), get_maintenance(), get, post, Current drift state, baseline fit, and recently accepted imputations., Operator clicked "Accept & Impute" on the Data Repair tab.

### Community 21 - "Dataset Generation & Fault Synthesis"
Cohesion: 0.67
Nodes (3): get_simulator_status(), get, Returns current edge simulator status and pitch script progress.

## Knowledge Gaps
- **67 isolated node(s):** `CameraTarget`, `SensorNodeProps`, `WeatherStation3DProps`, `AnomalyType`, `AnomalyUpdateRequest` (+62 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 210 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TelemetryPayload` connect `IMD Physical Plausibility Rules` to `Edge Station Simulator & Chaos Client`, `Database Persistence (PostgreSQL & SQLite)`, `Imputation & Sensor Recovery Engine`, `In-Memory Telemetry Ring Store`, `Multivariate Anomaly Detection & SHAP`, `Backend Ingestion & Core Services`, `Simulator & Injection REST Router`, `Anomaly & Feedback REST Router`, `MQTT Broker Subscriber Service`, `Telemetry Stream & SSE Router`, `Sensor Health Service Orchestrator`, `Edge Telemetry Generator`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `InMemoryStore` connect `In-Memory Telemetry Ring Store` to `Database Persistence (PostgreSQL & SQLite)`, `Anomaly & Feedback REST Router`, `IMD Physical Plausibility Rules`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `DriftTracker` connect `Predictive Maintenance EWMA Drift` to `Sensor Health Service Orchestrator`, `Edge Station Simulator & Chaos Client`, `Imputation & Sensor Recovery Engine`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `TelemetryPayload` (e.g. with `InMemoryStore` and `MultivariateAnomalyDetector`) actually correct?**
  _`TelemetryPayload` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InMemoryStore` (e.g. with `TelemetryPayload` and `AnomalyEvent`) actually correct?**
  _`InMemoryStore` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AnomalyEvent` (e.g. with `InMemoryStore` and `AnomalyEvaluation`) actually correct?**
  _`AnomalyEvent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CameraTarget`, `SensorNodeProps`, `WeatherStation3DProps` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._