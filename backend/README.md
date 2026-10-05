# SkyGuard AI — Clean Local Backend

Lightweight, 100% local FastAPI backend scaffolding for Automatic Weather Station anomaly detection, multi-agent AI dialogue via OpenRouter, and real-time streaming to the Next.js Digital Twin.

---

## 1. Quickstart (Running Locally)

### Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Configure Environment (Optional)
Copy `.env.example` to `.env` inside `backend/` or repo root:
```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```
*(Note: If no API key is provided, the backend automatically uses an intelligent local deterministic debate engine with zero errors.)*

### Start the Server
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Swagger UI will be available at: `http://localhost:8000/docs`

---

## 2. Ingesting Telemetry from the Edge Simulator

Your custom Edge Simulator can send telemetry packets via HTTP REST:

- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/telemetry`
- **Headers**: `Content-Type: application/json`
- **Body Example**:
```json
{
  "station_id": "AGRA-01",
  "temperature_c": 28.4,
  "humidity_pct": 72.0,
  "pressure_hpa": 1008.2,
  "wind_speed_ms": 3.4,
  "wind_dir_deg": 190.0,
  "solar_radiation_wm2": 510.0,
  "sequence": 101,
  "fault_type": "normal"
}
```

### The 3 Core Outputs Returned
The ingestion response contains:
1. `classification`: `"Nominal Baseline"`, `"Natural Weather Event"`, or `"Sensor Defect"`
2. `agent_dialogue`: Array of turns:
   - Turn 1: Model A (Atmospheric Specialist)
   - Turn 2: Model B (Hardware Diagnostician)
   - Consensus: Synthesizer summary
3. `reasoning`: Clear synthesized explanation behind the decision

```json
{
  "status": "success",
  "classification": "Sensor Defect",
  "reasoning": "Psychrometric dew-point divergence and capacitive degradation signature confirm sensor drift.",
  "agent_dialogue": [
    {
      "sender": "Model A (Atmospheric Specialist)",
      "role": "model_a",
      "message": "...",
      "timestamp": "..."
    },
    {
      "sender": "Model B (Hardware Diagnostician)",
      "role": "model_b",
      "message": "...",
      "timestamp": "..."
    }
  ],
  "confluence": { ... },
  "telemetry": { ... }
}
```

---

## 3. How to Plug in Your Retrained Models

Open [`backend/services/inference_hooks.py`](file:///backend/services/inference_hooks.py):
- `run_model_a(features)`: Load and call your Model A (Meteorological model).
- `run_model_b(features)`: Load and call your Model B (Hardware defect model).
- `compute_shap_attributions(features)`: Return feature importance weights.

---

## 4. Endpoints Overview
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/telemetry` | Ingest edge telemetry, run debate, broadcast |
| `GET` | `/api/v1/telemetry/stream` | Server-Sent Events (SSE) stream for Next.js |
| `GET` | `/api/v1/telemetry/latest` | Fetch latest reading |
| `GET` | `/api/v1/telemetry/history` | Fetch past $N$ readings for charts |
| `GET` | `/api/v1/anomalies` | Query anomaly records |
| `GET` | `/api/v1/health` | Service health check |
