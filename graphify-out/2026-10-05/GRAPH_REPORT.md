# Graph Report - SkyGuard_SIH  (2026-10-05)

## Corpus Check
- 107 files · ~98,177 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 24 file(s) not represented in the graph (top: .csv 10, (none) 3, .pt 3)

## Summary
- 1286 nodes · 2078 edges · 95 communities (82 shown, 13 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fe7189a5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- backend/main.py
- useTelemetryStore
- dataset_builder.py
- brandkit/SKILL.md
- Database
- compilerOptions
- CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE
- package.json
- AgentTurnLog
- CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION
- schemas.py
- next.config.mjs
- next-env.d.ts
- typing
- Analysis & Synthesis Instructions
- High-Agency Frontend Skill
- test_physics.py
- SequenceNormalizer
- pipeline.py
- EdgeSimulatorTUI
- FaultInjector
- Appendix B - Canonical Sources (read these before reinventing)
- GatekeeperCNN1D
- 8. THE CREATIVE ARSENAL (High-End Inspiration)
- run_simulator.py
- fetch_india_weather.py
- SKILL: Industrial Brutalism & Tactical Telemetry UI
- CSVPlayer
- LLMDebateEngine
- 7. AI TELLS (Forbidden Patterns)
- test_physics_and_faults.py
- 6. TECHNICAL REFERENCE (Dial Definitions)
- Agent Skill: Principal UI/UX Architect & Motion Choreographer (Awwwards-Tier)
- CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION
- 2. THE COMBINATORIAL VARIATION ENGINE
- Design System: Taste Standard
- inference_hooks.py
- sys
- test_end_to_end_wiring.py
- How `generate_dataset.py` Works (Layman's Guide for Judges)
- SSEBroadcaster
- 4. DESIGN ENGINEERING DIRECTIVES (Bias Correction)
- numpy
- generate_dataset.py
- 🌟 Key Architecture & Capabilities
- SkyGuard AWS Edge Device Simulator
- 5. MOTION CHOREOGRAPHY (FLUID DYNAMICS)
- 10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know)
- tasteskill: Anti-Slop Frontend Skill
- .transform
- CORE DIRECTIVE: AWWWARDS-LEVEL DESIGN ENGINEERING
- 22. STYLE VARIATION ENGINE
- Design Audit
- SkyGuard AI — Clean Local Backend
- Quickstart Guide
- 11. COMPONENT EXECUTION GUIDELINES
- 18. EXTRA CREATIVITY & IMPLEMENTATION EDGE
- Protocol: Premium Utilitarian Minimalism UI Architect
- 9. AI TELLS (Forbidden Patterns)
- 12. THE COMBINATORIAL VARIATION ENGINE
- 8. ANTI-AI-SLOP RULES
- mock_receiver.py
- 11. REDESIGN PROTOCOL
- 3. DEFAULT ARCHITECTURE & CONVENTIONS
- 6. PERFORMANCE & ACCESSIBILITY GUARDRAILS
- Full-Output Enforcement
- 33. CATEGORY-SPECIFIC BIAS
- 13. COLOR & MATERIAL RULES
- 4. HERO MINIMALISM RULES
- 29. ANTI-AI-SLOP RULES
- 5. IMAGE COUNT & PAGE SLICING
- ingest_telemetry
- 0. BRIEF INFERENCE (Read the Room Before Anything Else)
- 12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)
- 5. CONTEXT-AWARE PROACTIVITY
- 8. DARK MODE PROTOCOL
- 21. MOBILE ANTI-AI-TELLS RULE
- 33. DEFAULT SECTION PACKS
- 14. HERO MINIMALISM RULES
- 37. EXAMPLE INTERPRETATIONS
- 2. PLATFORM MODE RULE
- 37. EXAMPLE INTERPRETATIONS
- 15. DEFAULT SITE PACKS
- 20. EXAMPLE INTERPRETATIONS
- imagegen-frontend-web/SKILL.md
- graphify.md
- graphify/SKILL.md
- data_prep/__init__.py
- imputation/__init__.py
- llm_debate/__init__.py
- models/__init__.py

## God Nodes (most connected - your core abstractions)
1. `useTelemetryStore` - 49 edges
2. `CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE` - 39 edges
3. `CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION` - 39 edges
4. `react` - 23 edges
5. `Database` - 22 edges
6. `CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION` - 22 edges
7. `FaultInjector` - 19 edges
8. `lucide-react` - 19 edges
9. `SequenceNormalizer` - 19 edges
10. `WeatherPhysicsEngine` - 18 edges

## Surprising Connections (you probably didn't know these)
- `test_edge_simulator_payload_compatibility()` --uses--> `EdgeTransmitter`  [INFERRED]
  tests/test_end_to_end_wiring.py → SKYGUARD EDGE SIMULATOR/src/transmitter.py
- `get_pipeline()` --uses--> `SkyGuardPipeline`  [INFERRED]
  backend/services/inference_hooks.py → skyguard_data_model/src/pipeline.py
- `AutoChaosManager` --uses--> `AnomalyType`  [INFERRED]
  SKYGUARD EDGE SIMULATOR/run_simulator.py → SKYGUARD EDGE SIMULATOR/src/models/fault_injector.py
- `CSVPlayer` --uses--> `WeatherReading`  [INFERRED]
  SKYGUARD EDGE SIMULATOR/src/csv_player.py → SKYGUARD EDGE SIMULATOR/src/models/weather_physics.py
- `EdgeSimulatorTUI` --uses--> `AnomalyType`  [INFERRED]
  SKYGUARD EDGE SIMULATOR/src/tui.py → SKYGUARD EDGE SIMULATOR/src/models/fault_injector.py

## Import Cycles
- None detected.

## Communities (95 total, 13 thin omitted)

### Community 0 - "backend/main.py"
Cohesion: 0.09
Nodes (35): asyncio, accept_imputation(), bulk_action_anomalies(), get_anomalies(), get_decisions(), get_imputation_history(), get_latest_telemetry(), get_maintenance() (+27 more)

### Community 1 - "useTelemetryStore"
Cohesion: 0.07
Nodes (71): EdgeSimulatorPage(), frontend_src_app_globals, metadata, RootLayout(), DashboardPage(), TimeSeriesChart(), Header(), AnomalyCard() (+63 more)

### Community 2 - "dataset_builder.py"
Cohesion: 0.06
Nodes (40): fixture, glob, RandomState, build_all_datasets(), extract_base_windows(), format_window_record(), load_raw_station_data(), DataFrame (+32 more)

### Community 3 - "brandkit/SKILL.md"
Cohesion: 0.05
Nodes (43): 1. Logo Cover, 1. Monogram + Meaning, 2 × 3 REFERENCE-STYLE LAYOUT, 2. Logo Construction, 2. Product Action, 3. Digital Application, 3. Metaphor Fusion, 4. Brand Essence (+35 more)

### Community 4 - "Database"
Cohesion: 0.15
Nodes (10): Database, Any, Cleans all telemetry, anomalies, agent logs, decisions, and imputations for a…, Updates all open anomalies for a station to the specified status (acknowledged,…, Resolves all open anomalies for a station (convenience wrapper)., AnomalyEvent, DecisionRecord, TelemetryPayload (+2 more)

### Community 5 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "CORE DIRECTIVE: IMAGE-FIRST WEBSITE DESIGN TO CODE"
Cohesion: 0.06
Nodes (34): 10. IMAGE-FIRST CODEX WEBSITE WORKFLOW, 11. WHEN TO TRIGGER IMAGE GENERATION FIRST, 13. WEBSITE REFERENCE RULE, 15. RESPONSIVE FIRST-VIEW RULE, 16. ANTI-NESTED-BOX RULE, 17. REDUCE MICRO-UI CLUTTER RULE, 18. SECTION IMAGE GENERATION RULE, 19. WEBSITE IMAGE SYSTEM RULE (+26 more)

### Community 7 - "package.json"
Cohesion: 0.05
Nodes (42): dependencies, clsx, lucide-react, next, react, react-dom, @react-three/drei, @react-three/fiber (+34 more)

### Community 8 - "AgentTurnLog"
Cohesion: 0.19
Nodes (11): Config, Settings, AgentTurnLog, ConfluenceResult, AgentDebateService, Any, Local fallback engine delivering instant 2-turn dialogue without external API…, Executes a 2-turn dialogue between Model A (Atmospheric Specialist) and Model B… (+3 more)

### Community 9 - "CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION"
Cohesion: 0.06
Nodes (34): 10. DEVICE MOCKUP FRAME RULE, 11. ONBOARDING FLOW RULE, 12. FIRST SCREEN CLEANLINESS RULE, 13. SAFE AREA AND SYSTEM REGION RULE, 14. NAVIGATION RULE, 15. CLEAN LAYOUT RULE, 16. CREATIVE IMAGE DIRECTION RULE, 17. BACKGROUND TEXTURE AND SURFACE RULE (+26 more)

### Community 10 - "schemas.py"
Cohesion: 0.31
Nodes (10): DecisionListResponse, FaultInjectionRequest, ImputationAcceptRequest, ImputationResult, ShapAttribution, SimulatorStatusResponse, StationOverview, TelemetryIngestResponse (+2 more)

### Community 16 - "typing"
Cohesion: 0.15
Nodes (16): copy, csv, dataclasses, datetime, Enum, math, random, CSV Dataset Playback Reader. Reads pre-generated meteorological CSV datasets… (+8 more)

### Community 17 - "Analysis & Synthesis Instructions"
Cohesion: 0.11
Nodes (18): 1. Define the Atmosphere, 2. Map the Color Palette, 3. Establish Typography Rules, 4. Define the Hero Section, 5. Describe Component Stylings, 6. Define Layout Principles, 7. Define Responsive Rules, 8. Encode Motion Philosophy (+10 more)

### Community 18 - "High-Agency Frontend Skill"
Cohesion: 0.18
Nodes (10): 10. FINAL PRE-FLIGHT CHECK, 1. ACTIVE BASELINE CONFIGURATION, 2. DEFAULT ARCHITECTURE & CONVENTIONS, 3. DESIGN ENGINEERING DIRECTIVES (Bias Correction), 4. CREATIVE PROACTIVITY (Anti-Slop Implementation), 9. THE "MOTION-ENGINE" BENTO PARADIGM, A. Core Design Philosophy, B. The Animation Engine Specs (Perpetual Motion) (+2 more)

### Community 19 - "test_physics.py"
Cohesion: 0.08
Nodes (34): Series, check_physical_bounds(), compute_actual_vapor_pressure(), compute_barometric_tendency_3h(), compute_dew_point(), compute_saturation_vapor_pressure(), compute_thermodynamic_covariance(), extract_physics_features_from_window() (+26 more)

### Community 20 - "SequenceNormalizer"
Cohesion: 0.11
Nodes (17): ndarray, Standardizes [Temperature, Pressure, Relative Humidity] sequences using dataset…, Fit normalization parameters from training arrays., SequenceNormalizer, load_dataset(), Parse flattened sequence columns into (N, 12, 3) tensor and extract labels., Train and evaluate GatekeeperCNN1D., train_model_1() (+9 more)

### Community 21 - "pipeline.py"
Cohesion: 0.15
Nodes (15): dotenv, json, os, pytest, scipy_interpolate, Physical & Multivariate Sensor Imputation Module for AWS Telemetry. When a…, OpenRouter-Powered Model-Driven Dual-Agent LLM Debate Engine. Executes an…, SkyGuard End-to-End AWS Real-Time Anomaly Detection Pipeline. Orchestrates: 1.… (+7 more)

### Community 22 - "EdgeSimulatorTUI"
Cohesion: 0.11
Nodes (15): Layout, Panel, TransmissionResult, EdgeSimulatorTUI, Any, Constructs telemetry gauge table comparing baseline vs processed reading., Constructs banner showcasing active weather anomalies vs hardware defects., Constructs recent transmission event log. (+7 more)

### Community 24 - "FaultInjector"
Cohesion: 0.07
Nodes (16): AutoChaosManager, Orchestrates stochastic state transitions between: 1. Clean nominal atmospheric…, FaultInjector, InjectionState, Any, Applies weather anomalies and/or sensor defects to baseline weather telemetry., Sets or clears the active atmospheric weather anomaly., Toggles a specific hardware sensor defect on or off. (+8 more)

### Community 25 - "Appendix B - Canonical Sources (read these before reinventing)"
Cohesion: 0.09
Nodes (21): APPENDICES - Real Source-Backed Reference Material, Appendix A - Install Commands per Design System, Appendix B - Canonical Sources (read these before reinventing), Appendix C - Apple Liquid Glass: Honest Web Approximation, Apple Liquid Glass (Apple platforms only), Atlassian, Bootstrap, Carbon (+13 more)

### Community 26 - "GatekeeperCNN1D"
Cohesion: 0.13
Nodes (14): GatekeeperCNN1D, Hybrid 1D-CNN + GRU for Model B (Sensor Defect Detector). Processes shape:…, 1D Convolutional Network for Model 1 (Gatekeeper). Processes shape: (batch, 3,…, Bidirectional LSTM for Model A (Weather Anomaly Detector). Processes shape:…, SensorFaultCNN_LSTM, WeatherAnomalyLSTM, evaluate_all(), Evaluate all three trained models. (+6 more)

### Community 27 - "8. THE CREATIVE ARSENAL (High-End Inspiration)"
Cohesion: 0.22
Nodes (9): 8. THE CREATIVE ARSENAL (High-End Inspiration), Cards & Containers, Galleries & Media, Layout & Grids, Micro-Interactions & Effects, Navigation & Menüs, Scroll-Animations, The Standard Hero Paradigm (+1 more)

### Community 28 - "run_simulator.py"
Cohesion: 0.16
Nodes (15): collections, io, msvcrt, rich_console, rich_layout, rich_live, rich_text, Convenience alias pointing directly to run_simulator.py (+7 more)

### Community 29 - "fetch_india_weather.py"
Cohesion: 0.28
Nodes (8): argparse, requests, fetch_all_stations(), fetch_station_data(), DataFrame, Fetch multi-year surface meteorological data for diverse Indian climate zones…, Fetch and return dataframes for all configured Indian stations., Fetch hourly data for a single Indian station.

### Community 30 - "SKILL: Industrial Brutalism & Tactical Telemetry UI"
Cohesion: 0.12
Nodes (16): 1. Skill Meta, 2.1 Swiss Industrial Print, 2.2 Tactical Telemetry & CRT Terminal, 2. Visual Archetypes, 3.1 Macro-Typography (Structural Headers), 3.2 Micro-Typography (Data & Telemetry), 3.3 Textural Contrast (Artistic Disruption), 3. Typographic Architecture (+8 more)

### Community 31 - "CSVPlayer"
Cohesion: 0.16
Nodes (7): CSVPlayer, Any, Streams weather readings from a CSV file with line tracking and verification…, Loads and parses all records from the target CSV file., Returns the next row converted to a WeatherReading object., Returns current verification metadata to embed into outgoing payloads., TestCSVPlayer

### Community 32 - "LLMDebateEngine"
Cohesion: 0.11
Nodes (18): LLMDebateEngine, np_clip_confidence(), Any, Physics-augmented fallback arbiter when OpenRouter API key is unavailable or…, Conduct 2-agent adversarial debate, synthesize verdict with confidence score,…, Parse Arbiter JSON output or synthesize from probabilities., Append record to debate_logs.jsonl., Clamps confidence score between 0.50 and 0.99. (+10 more)

### Community 33 - "7. AI TELLS (Forbidden Patterns)"
Cohesion: 0.33
Nodes (6): 7. AI TELLS (Forbidden Patterns), Content & Data (The "Jane Doe" Effect), External Resources & Components, Layout & Spacing, Typography, Visual & CSS

### Community 34 - "test_physics_and_faults.py"
Cohesion: 0.11
Nodes (18): run_simulator(), get_climate_profile(), Returns climate profile by key, defaulting to mumbai_monsoon., Simulates realistic atmospheric variables governed by physical laws and…, Computes next physical state based on time of day and Ornstein-Uhlenbeck…, WeatherPhysicsEngine, EdgeTransmitter, Any (+10 more)

### Community 35 - "6. TECHNICAL REFERENCE (Dial Definitions)"
Cohesion: 0.50
Nodes (4): 6. TECHNICAL REFERENCE (Dial Definitions), DESIGN_VARIANCE (Level 1-10), MOTION_INTENSITY (Level 1-10), VISUAL_DENSITY (Level 1-10)

### Community 36 - "Agent Skill: Principal UI/UX Architect & Motion Choreographer (Awwwards-Tier)"
Cohesion: 0.14
Nodes (13): 1. Meta Information & Core Directive, 2. THE "ABSOLUTE ZERO" DIRECTIVE (STRICT ANTI-PATTERNS), 3. THE CREATIVE VARIANCE ENGINE, 4. HAPTIC MICRO-AESTHETICS (COMPONENT MASTERY), 6. PERFORMANCE GUARDRAILS, 7. EXECUTION PROTOCOL, 8. PRE-OUTPUT CHECKLIST, A. The "Double-Bezel" (Doppelrand / Nested Architecture) (+5 more)

### Community 37 - "CORE DIRECTIVE: AWWWARDS-LEVEL IMAGE ART DIRECTION"
Cohesion: 0.14
Nodes (14): 10. SECTION RHYTHM RULE, 12. DENSITY & SPACING DISCIPLINE, 14. IMAGE / MEDIA DIRECTION, 16. MULTI-IMAGE CONSISTENCY RULE, 17. CLARITY CHECK, 19. RESPONSE BEHAVIOR, 1. ACTIVE BASELINE CONFIGURATION, 21. FINAL GOAL (+6 more)

### Community 38 - "2. THE COMBINATORIAL VARIATION ENGINE"
Cohesion: 0.14
Nodes (14): 2. THE COMBINATORIAL VARIATION ENGINE, Background Character, Background Mode (per-section), Composition Anchor (per-section), CTA Variation, Hero Architecture, Hero Scale (per-page), Motion-Implied Language (+6 more)

### Community 39 - "Design System: Taste Standard"
Cohesion: 0.14
Nodes (13): 1. Visual Theme & Atmosphere, 2. Color Palette & Roles, 3. Typography Rules, 4. Component Stylings, 5. Hero Section, 6. Layout Principles, 7. Responsive Rules, 9. Anti-Patterns (Banned) (+5 more)

### Community 40 - "inference_hooks.py"
Cohesion: 0.14
Nodes (19): MaintenanceResult, MaintenanceSensorStatus, compute_shap_attributions(), derive_maintenance_status(), get_pipeline(), process_telemetry_pipeline(), Any, Inference Hooks & Real-Time ML Engine for SkyGuard AI… (+11 more)

### Community 41 - "sys"
Cohesion: 0.19
Nodes (12): Path, pathlib, main(), SkyGuard AI - Multi-Suite Test Runner ==================================== Runs…, run_suite(), main(), SkyGuard AI - Unified System Launcher =====================================…, run_backend() (+4 more)

### Community 42 - "test_end_to_end_wiring.py"
Cohesion: 0.12
Nodes (14): fastapi_testclient, End-to-End System Integration Tests for SkyGuard AI. Verifies the complete…, Verify that an injected sensor defect triggers Stage 2/3 and produces…, Verify that operator can acknowledge, resolve, or ignore defects, logging the…, Verify accepting an imputation and reading sensor maintenance diagnostics., Verify starting and stopping the 5-minute automated demo scenario., Verify Edge Simulator transmitter builds a payload that backend accepts., Verify that packets 1 to 11 are labeled as WARMUP, and on packet 12, full… (+6 more)

### Community 43 - "How `generate_dataset.py` Works (Layman's Guide for Judges)"
Cohesion: 0.14
Nodes (13): 1. The Core Idea: Why This Proves "Zero Cheating", 2. The 3 Golden Rules of Real Weather (Simple Analogies), 3. The 4 Indian Climate Zones (IMD Baselines), 4. The Critical Difference: Weather Anomaly vs. Sensor Defect, 5. The 60-Second Presentation Pitch to the Judges, 6. How to Run It During the Demo, How `generate_dataset.py` Works (Layman's Guide for Judges), Rule 1: The Sun Rule (The Diurnal Cycle) (+5 more)

### Community 44 - "SSEBroadcaster"
Cohesion: 0.29
Nodes (3): Any, SSEBroadcaster, Queue

### Community 45 - "4. DESIGN ENGINEERING DIRECTIVES (Bias Correction)"
Cohesion: 0.17
Nodes (12): 4.10 Quotes & Testimonials, 4.11 Page Theme Lock (Light / Dark Mode Consistency), 4.1 Typography, 4.2 Color Calibration, 4.3 Layout Diversification, 4.4 Materiality, Shadows, Cards, 4.5 Interactive UI States, 4.6 Data & Form Patterns (+4 more)

### Community 46 - "numpy"
Cohesion: 0.22
Nodes (14): numpy, pandas, sklearn_metrics, sklearn_model_selection, Extreme Meteorological Event Detector & Augmenter for India. Implements IMD…, PyTorch Neural Network Architectures for AWS Surface Telemetry. Lightweight,…, Comprehensive Model Evaluation Script for SkyGuard System. Evaluates Model 1…, Training script for Model 1 (Gatekeeper). Differentiates between Normal Weather… (+6 more)

### Community 47 - "generate_dataset.py"
Cohesion: 0.21
Nodes (13): hashlib, rich_panel, rich_progress, rich_table, generate_csv_file(), interactive_prompt(), main(), print_welcome_banner() (+5 more)

### Community 48 - "🌟 Key Architecture & Capabilities"
Cohesion: 0.18
Nodes (10): 1.0 Edge Device Layer (ESP32 Deployment & Emulation), 1. Start the Backend API (FastAPI), 2.0 Cloud Analytics Layer (Structured Reasoning), 2. Start the Frontend Dashboard (Next.js 14), 3.0 Visualization & Alerting Layer (Operator Dashboard), 3. Optional Two-Laptop / Edge Simulator Demo, 🌟 Key Architecture & Capabilities, 🚀 Quick Start (Local Run) (+2 more)

### Community 49 - "SkyGuard AWS Edge Device Simulator"
Cohesion: 0.18
Nodes (10): 1. Installation, 2. Generate a Dataset Live (Step 1 of Judge Demo), 3. Stream the CSV through the AWS Edge Simulator (Step 2 of Judge Demo), 4. (Optional) Run Local Mock Ingestion Server, Configuration (`config.json`), Directory Structure, Key Features, Quickstart Guide (+2 more)

### Community 50 - "5. MOTION CHOREOGRAPHY (FLUID DYNAMICS)"
Cohesion: 0.50
Nodes (4): 5. MOTION CHOREOGRAPHY (FLUID DYNAMICS), A. The "Fluid Island" Nav & Hamburger Reveal, B. Magnetic Button Hover Physics, C. Scroll Interpolation (Entry Animations)

### Community 51 - "10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know)"
Cohesion: 0.20
Nodes (10): 10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know), Animation Library Choice, Cards & Containers, Galleries & Media, Hero Paradigms, Layout & Grids, Micro-Interactions & Effects, Navigation & Menus (+2 more)

### Community 52 - "tasteskill: Anti-Slop Frontend Skill"
Cohesion: 0.20
Nodes (10): 13. OUT OF SCOPE, 14. FINAL PRE-FLIGHT CHECK, 1.A Dial Inference (design read → dial values), 1.B Use-Case Presets, 1.C How the Dials Drive Output, 1. THE THREE DIALS (Core Configuration), 2.A When to reach for a real design system (use official packages), 2.B When the brief is an aesthetic, not a system (+2 more)

### Community 53 - ".transform"
Cohesion: 0.22
Nodes (8): 7. DIAL DEFINITIONS (Technical Reference), DESIGN_VARIANCE (Level 1-10), MOTION_INTENSITY (Level 1-10), VISUAL_DENSITY (Level 1-10), 5. PERFORMANCE GUARDRAILS, 7. Subtle Motion & Micro-Animations, 8. Motion & Interaction (Code-Phase Intent), x shape: (batch, seq_len, 3) or (seq_len, 3) returns normalized x of same shape

### Community 54 - "CORE DIRECTIVE: AWWWARDS-LEVEL DESIGN ENGINEERING"
Cohesion: 0.20
Nodes (9): 1. PYTHON-DRIVEN TRUE RANDOMIZATION (BREAKING THE LOOP), 2. AIDA STRUCTURE & SPACING, 3. HERO ARCHITECTURE & THE 2-LINE IRON RULE, 4. THE GAPLESS BENTO GRID, 5. ADVANCED GSAP MOTION & HOVER PHYSICS, 6. COMPONENT ARSENAL & CREATIVITY, 7. CONTENT, ASSETS & STRICT BANS, 8. MANDATORY PRE-FLIGHT <design_plan> (+1 more)

### Community 55 - "22. STYLE VARIATION ENGINE"
Cohesion: 0.20
Nodes (10): 22. STYLE VARIATION ENGINE, Decorative Asset Set, Image Art Direction Bias, Motion-Implied Language, Palette Logic, Signature Component Set, Structure Bias, Texture / Surface Treatment (+2 more)

### Community 56 - "Design Audit"
Cohesion: 0.10
Nodes (19): Code Quality, Color and Surfaces, Component Patterns, Content, Design Audit, Fix Priority, How This Works, Iconography (+11 more)

### Community 57 - "SkyGuard AI — Clean Local Backend"
Cohesion: 0.20
Nodes (9): 1. Quickstart (Running Locally), 2. Ingesting Telemetry from the Edge Simulator, 3. How to Plug in Your Retrained Models, 4. Endpoints Overview, Configure Environment (Optional), Install Dependencies, SkyGuard AI — Clean Local Backend, Start the Server (+1 more)

### Community 58 - "Quickstart Guide"
Cohesion: 0.20
Nodes (9): 1. Configure OpenRouter API (Optional), 2. Run the End-to-End Real-Time Prototype, 3. Re-train Models, 4. Run Comprehensive Benchmark Evaluation, 5. Run Automated Test Suite, Dataset Format Specification, Directory Structure, Quickstart Guide (+1 more)

### Community 59 - "11. COMPONENT EXECUTION GUIDELINES"
Cohesion: 0.22
Nodes (9): 11. COMPONENT EXECUTION GUIDELINES, 3D Cascading Card Deck, Diagonal Staggered Square Masonry, Hover-Accordion Slice Layout, Off-Grid Editorial Layout, Pristine Gapless Bento Grid, Product UI Panel Stack, Turning Polaroid Arc (+1 more)

### Community 60 - "18. EXTRA CREATIVITY & IMPLEMENTATION EDGE"
Cohesion: 0.22
Nodes (9): 18. EXTRA CREATIVITY & IMPLEMENTATION EDGE, Composition variety check, Conversion focus, Cross-section contrast, CTA specificity, Cultural / tonal alignment, Data-viz restraint, Image variety inside one comp (+1 more)

### Community 61 - "Protocol: Premium Utilitarian Minimalism UI Architect"
Cohesion: 0.22
Nodes (8): 1. Protocol Overview, 2. Absolute Negative Constraints (Banned Elements), 3. Typographic Architecture, 4. Color Palette (Warm Monochrome + Spot Pastels), 5. Component Specifications, 6. Iconography & Imagery Directives, 8. Execution Protocol, Protocol: Premium Utilitarian Minimalism UI Architect

### Community 64 - "9. AI TELLS (Forbidden Patterns)"
Cohesion: 0.25
Nodes (8): 9.A Visual & CSS, 9. AI TELLS (Forbidden Patterns), 9.B Typography, 9.C Layout & Spacing, 9.D Content & Data ("Jane Doe" Effect), 9.E External Resources & Components, 9.F Production-Test Tells (banned outright), 9.G EM-DASH BAN (the single most-violated Tell)

### Community 65 - "12. THE COMBINATORIAL VARIATION ENGINE"
Cohesion: 0.25
Nodes (8): 12. THE COMBINATORIAL VARIATION ENGINE, Background Character, Hero Architecture, Motion-Implied Language, Section System, Signature Component Set, Theme Paradigm, Typography Character

### Community 66 - "8. ANTI-AI-SLOP RULES"
Cohesion: 0.25
Nodes (8): 8. ANTI-AI-SLOP RULES, Carousel / marquee slop (layout), Content slop, Data / KPI slop, Density slop, Layout slop, Typography slop, Visual slop

### Community 67 - "mock_receiver.py"
Cohesion: 0.25
Nodes (4): BaseHTTPRequestHandler, http_server, Optional Standalone Mock Ingestion Server. Run this in a separate terminal if…, TelemetryHandler

### Community 68 - "11. REDESIGN PROTOCOL"
Cohesion: 0.29
Nodes (7): 11.A Detect the Mode (first action), 11.B Audit Before Touching, 11.C Preservation Rules, 11.D Modernisation Levers (priority order), 11.E Decision Tree: Targeted Evolution vs Full Redesign, 11.F What Never Changes Silently, 11. REDESIGN PROTOCOL

### Community 69 - "3. DEFAULT ARCHITECTURE & CONVENTIONS"
Cohesion: 0.29
Nodes (7): 3.A Stack, 3.B State, 3.C Icons, 3.D Emoji Policy, 3. DEFAULT ARCHITECTURE & CONVENTIONS, 3.E Responsiveness & Layout Mechanics, 3.F Dependency Verification (mandatory)

### Community 70 - "6. PERFORMANCE & ACCESSIBILITY GUARDRAILS"
Cohesion: 0.29
Nodes (7): 6.A Hardware Acceleration, 6.B Reduced Motion (mandatory), 6.C Dark Mode (mandatory for any consumer-facing page), 6.D Core Web Vitals Targets, 6.E DOM Cost, 6.F Z-Index Restraint, 6. PERFORMANCE & ACCESSIBILITY GUARDRAILS

### Community 71 - "Full-Output Enforcement"
Cohesion: 0.29
Nodes (6): Banned Output Patterns, Baseline, Execution Process, Full-Output Enforcement, Handling Long Outputs, Quick Check

### Community 72 - "33. CATEGORY-SPECIFIC BIAS"
Cohesion: 0.29
Nodes (7): 33. CATEGORY-SPECIFIC BIAS, Commerce, Fintech, Health / Fitness, Productivity, Social, Wellness / Lifestyle

### Community 73 - "13. COLOR & MATERIAL RULES"
Cohesion: 0.29
Nodes (7): 13. COLOR & MATERIAL RULES, Background Confidence Rule, Background-image harmony, Gradient Discipline, Materiality, Palette Discipline, Strong guidance

### Community 74 - "4. HERO MINIMALISM RULES"
Cohesion: 0.29
Nodes (7): 4. HERO MINIMALISM RULES, Absolute Hero Rules, Graphic Restraint, Headline Rule, Hero Composition Bias, Pre-output check, Typography Execution

### Community 76 - "29. ANTI-AI-SLOP RULES"
Cohesion: 0.33
Nodes (6): 29. ANTI-AI-SLOP RULES, Content slop, Density slop, Layout slop, Typography slop, Visual slop

### Community 77 - "5. IMAGE COUNT & PAGE SLICING"
Cohesion: 0.33
Nodes (6): 5. IMAGE COUNT & PAGE SLICING, Continuity Rule, Counting rule, Format, Section size variety, THIS IS THE PRIMARY OUTPUT RULE

### Community 79 - "ingest_telemetry"
Cohesion: 0.33
Nodes (5): ingest_telemetry(), Server-Sent Events endpoint streaming telemetry and anomaly events to Next.js., Primary ingestion endpoint for the Automatic Weather Station (AWS) Edge…, telemetry_stream(), Request

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

### Community 88 - "33. DEFAULT SECTION PACKS"
Cohesion: 0.50
Nodes (4): 12-section pack, 33. DEFAULT SECTION PACKS, 4-section pack, 8-section pack

### Community 89 - "14. HERO MINIMALISM RULES"
Cohesion: 0.50
Nodes (4): 14. HERO MINIMALISM RULES, Absolute Hero Rules, Headline Rule, Hero Cleanliness Rule

### Community 90 - "37. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 37. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 91 - "2. PLATFORM MODE RULE"
Cohesion: 0.50
Nodes (4): 2. PLATFORM MODE RULE, Android-native premium, Cross-platform premium neutral, iOS-native premium

### Community 92 - "37. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 37. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

### Community 93 - "15. DEFAULT SITE PACKS"
Cohesion: 0.50
Nodes (4): 12-section pack, 15. DEFAULT SITE PACKS, 4-section pack, 8-section pack

### Community 94 - "20. EXAMPLE INTERPRETATIONS"
Cohesion: 0.50
Nodes (4): 20. EXAMPLE INTERPRETATIONS, Example 1, Example 2, Example 3

## Knowledge Gaps
- **528 isolated node(s):** `Config`, `nextConfig`, `name`, `version`, `private` (+523 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 767 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SequenceNormalizer` connect `SequenceNormalizer` to `GatekeeperCNN1D`, `pipeline.py`, `.transform`, `numpy`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Why does `tasteskill: Anti-Slop Frontend Skill` connect `tasteskill: Anti-Slop Frontend Skill` to `9. AI TELLS (Forbidden Patterns)`, `11. REDESIGN PROTOCOL`, `3. DEFAULT ARCHITECTURE & CONVENTIONS`, `6. PERFORMANCE & ACCESSIBILITY GUARDRAILS`, `4. DESIGN ENGINEERING DIRECTIVES (Bias Correction)`, `0. BRIEF INFERENCE (Read the Room Before Anything Else)`, `12. THE BLOCK LIBRARY (Contract - Implementations Land Here Iteratively)`, `5. CONTEXT-AWARE PROACTIVITY`, `10. REFERENCE VOCABULARY (Pattern Names the Agent Should Know)`, `8. DARK MODE PROTOCOL`, `.transform`, `Appendix B - Canonical Sources (read these before reinventing)`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `6.A Hardware Acceleration` connect `6. PERFORMANCE & ACCESSIBILITY GUARDRAILS` to `.transform`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **What connects `Config`, `nextConfig`, `name` to the rest of the system?**
  _528 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `backend/main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09009009009009009 - nodes in this community are weakly interconnected._
- **Should `useTelemetryStore` be split into smaller, more focused modules?**
  _Cohesion score 0.06596578025149454 - nodes in this community are weakly interconnected._
- **Should `dataset_builder.py` be split into smaller, more focused modules?**
  _Cohesion score 0.062040816326530614 - nodes in this community are weakly interconnected._