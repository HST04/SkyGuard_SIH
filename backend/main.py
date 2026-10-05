import asyncio
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.config import settings
from backend.schemas import (
    TelemetryPayload,
    AnomalyEvent,
    StationOverview,
    ConfluenceResult,
    TelemetryIngestResponse,
    FaultInjectionRequest,
    SimulatorStatusResponse,
    ImputationAcceptRequest,
    ImputationResult,
    MaintenanceResult,
    PitchScriptStatus,
    DecisionRecord,
    DecisionListResponse,
    AgentTurnLog
)
from backend.database import db
from backend.services.sse_broadcaster import sse_broadcaster
from backend.services.inference_hooks import (
    process_telemetry_pipeline,
    derive_maintenance_status
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SkyGuard AI Automatic Weather Station (AWS) anomaly detection backend with multi-agent debate and physics imputation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory simulator status state
active_simulator_fault = "normal"
pitch_script_status: Optional[PitchScriptStatus] = None
pitch_script_task: Optional[asyncio.Task] = None

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "Unified PyTorch + Multi-Agent Engine"
    }

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# --- Edge Simulator Telemetry Ingestion ---

@app.post("/api/v1/telemetry", response_model=TelemetryIngestResponse)
@app.post("/api/telemetry", response_model=TelemetryIngestResponse)
async def ingest_telemetry(request: Request):
    """
    Primary ingestion endpoint for the Automatic Weather Station (AWS) Edge Simulator.
    Supports both flattened TelemetryPayload and nested AWS IoT Greengrass schema.
    1. Manages length-12 rolling window buffer per station (packets 1-11 in WARMUP).
    2. Runs Stage 1 Gatekeeper CNN-1D, Stage 2 Model A/B, and Stage 3 LLM Debate.
    3. Triggers Sensor Imputation (Data Repair) for physical sensor faults.
    4. Persists locally in SQLite and broadcasts to the Frontend via SSE.
    """
    global active_simulator_fault
    body = await request.json()

    # Adapter: If nested AWS IoT Greengrass payload format
    if "telemetry" in body and isinstance(body["telemetry"], dict):
        tel = body["telemetry"]
        station_id = body.get("deviceId") or body.get("station_id", "AGRA-01")
        temp = tel.get("temperature_c", 25.0)
        rh = tel.get("relative_humidity_pct", tel.get("humidity_pct", 60.0))
        press = tel.get("pressure_hpa", 1013.25)
        wind = tel.get("wind_speed_mps", tel.get("wind_speed_ms", 2.0))
        wind_dir = tel.get("wind_direction_deg", 180.0)
        solar = tel.get("solar_radiation_wm2", 400.0)
        gt = body.get("_ground_truth", {})
        labels = gt.get("active_labels", ["NORMAL"])
        fault = "normal"
        if any("CALIBRATION_DRIFT" in l or "temp_drift" in l for l in labels):
            fault = "temp_drift"
        elif any("DRIFT" in l or "drift" in l.lower() for l in labels):
            fault = "humidity_drift"
        elif any("STUCK" in l or "stuck" in l.lower() for l in labels):
            fault = "stuck_temp" if any("TEMP" in l for l in labels) else "stuck_humidity"
        elif any("NOISE" in l or "noise" in l.lower() for l in labels):
            fault = "sensor_noise"
        elif any("SPIKE" in l or "spike" in l.lower() for l in labels):
            fault = "heat_spike"
        elif any("STORM" in l or "squall" in l.lower() for l in labels):
            fault = "valid_squall"
        elif any("HEATWAVE" in l for l in labels):
            fault = "heatwave"
        elif any("COLD" in l for l in labels):
            fault = "cold_snap"
        elif gt.get("status") not in (None, "NORMAL"):
            fault = labels[0].lower()

        payload = TelemetryPayload(
            station_id=station_id,
            timestamp=body.get("isoTime") or datetime.utcnow().isoformat(),
            temperature_c=temp,
            humidity_pct=rh,
            pressure_hpa=press,
            wind_speed_ms=wind,
            wind_dir_deg=wind_dir,
            solar_radiation_wm2=solar,
            fault_type=fault,
            source="edge_simulator",
            extra_data=body
        )
    else:
        payload = TelemetryPayload.model_validate(body)

    # Apply active simulator fault override from chaos harness if payload is nominal
    if active_simulator_fault != "normal" and (not payload.fault_type or payload.fault_type == "normal"):
        payload.fault_type = active_simulator_fault

    # Step 1: Execute End-to-End Multi-Stage ML Pipeline
    payload, anomaly_event, decision_record = process_telemetry_pipeline(payload)

    # Step 2: Handle Anomaly Event Trigger
    if anomaly_event:
        db.insert_anomaly(anomaly_event)
        await sse_broadcaster.broadcast_anomaly(anomaly_event)

    # Step 3: Handle Decision Audit Logging & Broadcast
    if decision_record:
        db.insert_decision(decision_record)
        await sse_broadcaster.broadcast_decision(decision_record)

    # Step 4: Persist in SQLite
    db.insert_telemetry(payload)
    if payload.confluence:
        db.insert_agent_log(
            station_id=payload.station_id,
            classification=payload.confluence.classification,
            reasoning=payload.confluence.summary,
            dialogue=payload.confluence.agent_dialogue
        )

    # Step 5: Real-time broadcast to Frontend via SSE
    await sse_broadcaster.broadcast_telemetry(payload)

    confluence = payload.confluence or ConfluenceResult()
    return TelemetryIngestResponse(
        status="success",
        classification=confluence.classification,
        reasoning=confluence.summary,
        agent_dialogue=confluence.agent_dialogue,
        confluence=confluence,
        telemetry=payload
    )

# --- SSE Stream Endpoint ---

@app.get("/api/v1/telemetry/stream")
async def telemetry_stream(request: Request, station_id: str = Query("AGRA-01")):
    """
    Server-Sent Events endpoint streaming telemetry and anomaly events to Next.js.
    """
    queue = await sse_broadcaster.register()

    async def event_generator():
        try:
            # Send initial connection acknowledgment
            yield f"event: ping\ndata: {{\"connected\": true, \"station_id\": \"{station_id}\"}}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield message
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep browser SSE connection open
                    yield ": heartbeat\n\n"
        finally:
            await sse_broadcaster.unregister(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# --- Telemetry & Overview Queries ---

@app.get("/api/v1/telemetry/latest", response_model=Optional[TelemetryPayload])
def get_latest_telemetry(station_id: str = Query("AGRA-01")):
    return db.get_latest_telemetry(station_id)

@app.get("/api/v1/telemetry/history", response_model=List[TelemetryPayload])
def get_telemetry_history(station_id: str = Query("AGRA-01"), limit: int = Query(60)):
    return db.get_telemetry_history(station_id, limit)

@app.get("/api/v1/telemetry/overview", response_model=StationOverview)
def get_station_overview(station_id: str = Query("AGRA-01")):
    latest = db.get_latest_telemetry(station_id)
    anomalies = db.get_anomalies(station_id, status="open", limit=10)
    status_str = "anomaly" if anomalies else "normal"
    conn_status = "connected" if latest else "standby"
    return StationOverview(
        station_id=station_id,
        status=status_str,
        latest_telemetry=latest,
        active_anomalies=anomalies,
        total_anomalies_detected=len(anomalies),
        connection_status=conn_status
    )

# --- Anomaly Management ---

@app.get("/api/v1/anomalies", response_model=List[AnomalyEvent])
def get_anomalies(
    station_id: str = Query("AGRA-01"),
    status: Optional[str] = Query(None),
    limit: int = Query(50)
):
    return db.get_anomalies(station_id, status, limit)

@app.patch("/api/v1/anomalies/{anomaly_id}", response_model=Optional[AnomalyEvent])
async def update_anomaly(anomaly_id: str, req: dict):
    global active_simulator_fault
    new_status = req.get("status", "open")
    note = req.get("resolution_note")
    updated = db.update_anomaly_status(anomaly_id, new_status, note)
    if not updated:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    # Requirement 2: When an anomaly is acknowledged, resolved, or ignored:
    # Log the decision in the audit trail, reset simulator fault & clear active episode
    # so the system assumes all sensors OK and shows the current nominal state.
    if new_status in ["acknowledged", "resolved", "ignored", "false_alarm"]:
        from backend.services.inference_hooks import clear_active_incident
        clear_active_incident(updated.station_id)
        active_simulator_fault = "normal"

        action_verbs = {
            "acknowledged": "Acknowledged",
            "resolved": "Resolved",
            "ignored": "Ignored",
            "false_alarm": "Flagged as False Alarm"
        }
        verb = action_verbs.get(new_status, new_status.capitalize())
        dec_record = DecisionRecord(
            decision_id=f"dec_{uuid.uuid4().hex[:8]}",
            station_id=updated.station_id,
            timestamp=datetime.utcnow().isoformat(),
            classification="Nominal Baseline",
            confidence_score=99.0,
            trigger_reason=f"Operator Action [{verb}]: Sensor defect #{anomaly_id} logged. System state restored to Nominal (All Sensors OK).",
            culprit_sensors=[],
            action_recommended="Station nominal. Continuous 1 Hz monitoring.",
            dialogue=[
                AgentTurnLog(
                    sender="Operator Console",
                    role="arbiter",
                    message=f"Defect #{anomaly_id} marked as '{new_status}' by operator. {note or 'Incident logged.'} System assumes all sensors nominal."
                )
            ],
            reconstruction_error=0.015,
            transmitted_data=updated.transmitted_data,
            decision_reasoning=updated.decision_reasoning,
            summary=f"Operator {verb.lower()} sensor defect #{anomaly_id}. System state restored to Nominal (All Sensors OK)."
        )
        db.insert_decision(dec_record)
        await sse_broadcaster.broadcast_decision(dec_record)

    await sse_broadcaster.broadcast_anomaly(updated)
    return updated

@app.post("/api/v1/anomalies/resolve-all")
@app.post("/api/v1/anomalies/bulk-action")
async def bulk_action_anomalies(
    station_id: str = Query("AGRA-01"),
    status: str = Query("resolved"),
    note: Optional[str] = Query(None)
):
    global active_simulator_fault
    count = db.bulk_update_anomalies(station_id, status=status, note=note)
    from backend.services.inference_hooks import clear_active_incident
    clear_active_incident(station_id)
    active_simulator_fault = "normal"

    action_record = DecisionRecord(
        decision_id=f"dec_{uuid.uuid4().hex[:8]}",
        station_id=station_id,
        timestamp=datetime.utcnow().isoformat(),
        classification="Nominal Baseline",
        confidence_score=99.0,
        trigger_reason=f"Bulk operator action: {count} open defects marked as '{status}'. System state restored to Nominal (All Sensors OK).",
        culprit_sensors=[],
        action_recommended="Station nominal. Continuous 1 Hz observation.",
        dialogue=[
            AgentTurnLog(
                sender="Operator Console",
                role="arbiter",
                message=f"Bulk action [{status.upper()}] completed for {count} defects. All hardware alarms cleared."
            )
        ],
        reconstruction_error=0.015,
        summary=f"Bulk action: {count} defects {status}. All sensors assumed OK."
    )
    db.insert_decision(action_record)
    await sse_broadcaster.broadcast_decision(action_record)
    return {"status": "success", "count": count, "action": status, "resolved_count": count}

@app.post("/api/v1/anomalies/feedback")
async def submit_feedback(req: dict):
    ano_id = req.get("anomaly_id")
    label = req.get("label", "false_alarm")
    note = req.get("note", "Operator feedback")
    if ano_id:
        new_status = "false_alarm" if label == "false_alarm" else "acknowledged"
        return await update_anomaly(ano_id, {"status": new_status, "resolution_note": note})
    return {"status": "ok", "message": "Feedback recorded and anomaly updated"}

# --- Decision Audit Trail Endpoints ---

@app.get("/api/v1/decisions", response_model=DecisionListResponse)
def get_decisions(
    station_id: str = Query("AGRA-01"),
    limit: int = Query(50),
    classification: Optional[str] = Query(None)
):
    """
    Retrieves chronological AI confluence decisions and audit records for the station.
    """
    records = db.get_decisions(station_id=station_id, limit=limit, classification=classification)
    return DecisionListResponse(status="success", total=len(records), decisions=records)

# --- Sensor Imputation & Maintenance Endpoints ---

@app.post("/api/v1/imputation/accept")
async def accept_imputation(req: ImputationAcceptRequest):
    """
    Accepts physics-suggested sensor imputation and stores in database.
    Broadcasts 'imputation_accepted' event to all connected dashboard clients.
    """
    db.insert_accepted_imputation(req.model_dump())
    await sse_broadcaster.broadcast_custom("imputation_accepted", req.model_dump())
    return {"status": "success", "record": req.model_dump()}

@app.get("/api/v1/imputation/history")
def get_imputation_history(station_id: str = Query("AGRA-01"), limit: int = Query(20)):
    return db.get_accepted_imputations(station_id, limit)

@app.get("/api/v1/maintenance", response_model=MaintenanceResult)
def get_maintenance(station_id: str = Query("AGRA-01")):
    latest = db.get_latest_telemetry(station_id)
    if latest and latest.maintenance:
        return latest.maintenance
    anomalies = db.get_anomalies(station_id, status="open", limit=5)
    is_drift = any("drift" in (a.diagnostic_message or "").lower() for a in anomalies)
    return derive_maintenance_status(station_id=station_id, is_drift=is_drift)

@app.post("/api/v1/system/reset")
def reset_system():
    global active_simulator_fault
    active_simulator_fault = "normal"
    db.reset_database()
    from backend.services.inference_hooks import reset_station_buffers
    reset_station_buffers()
    return {"status": "success", "message": "System reset to clean standby state"}

# --- Simulator Controls & Automated Pitch Script ---

@app.post("/api/v1/simulator/inject")
def inject_fault(req: FaultInjectionRequest):
    global active_simulator_fault
    active_simulator_fault = req.fault_type
    return {"status": "success", "active_fault": active_simulator_fault}

@app.post("/api/v1/simulator/reset")
def reset_simulator():
    global active_simulator_fault
    active_simulator_fault = "normal"
    return {"status": "success", "active_fault": "normal"}

@app.get("/api/v1/simulator/status")
def get_simulator_status():
    global active_simulator_fault, pitch_script_status
    return {
        "active_fault": active_simulator_fault,
        "pitch_script": pitch_script_status.model_dump() if pitch_script_status else None
    }

async def _pitch_script_runner():
    """Background worker executing the 5-minute judge pitch scenario sequence."""
    global active_simulator_fault, pitch_script_status
    total_seconds = 300
    try:
        for elapsed in range(total_seconds + 1):
            if elapsed < 90:
                p_id = "BASELINE"
                p_title = "Baseline Diurnal"
                p_desc = "Normal weather cycles. 3D Twin Green."
                active_simulator_fault = "normal"
            elif elapsed < 180:
                p_id = "TRUE_NEGATIVE_STORM"
                p_title = "Thunderstorm True-Negative"
                p_desc = "Violent pressure drop & humidity surge. CNN respects natural physics. Zero false alarm."
                active_simulator_fault = "valid_squall"
            elif elapsed < 225:
                p_id = "CAPACITIVE_DRIFT"
                p_title = "Subtle Capacitive Drift"
                p_desc = "Injected +15% humidity bias. Bypasses static rules. 1D-CNN accumulates error."
                active_simulator_fault = "humidity_drift"
            else:
                p_id = "ANOMALY_TRIGGERED"
                p_title = "AI Anomaly & SHAP"
                p_desc = "Autoencoder threshold trips! 3D twin pulses Red, SHAP isolates sensor."
                active_simulator_fault = "humidity_drift"

            pitch_script_status = PitchScriptStatus(
                active=True,
                phase_id=p_id,
                phase_title=p_title,
                phase_description=p_desc,
                elapsed_seconds=elapsed
            )
            await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        pass
    else:
        pitch_script_status = None
        active_simulator_fault = "normal"

@app.post("/api/v1/simulator/pitch-script/start")
async def start_pitch_script():
    global pitch_script_task, pitch_script_status
    if pitch_script_task and not pitch_script_task.done():
        pitch_script_task.cancel()
    pitch_script_task = asyncio.create_task(_pitch_script_runner())
    pitch_script_status = PitchScriptStatus(
        active=True,
        phase_id="BASELINE",
        phase_title="Baseline Diurnal",
        phase_description="Normal weather cycles. 3D Twin Green.",
        elapsed_seconds=0
    )
    return {"status": "started", "pitch_script": pitch_script_status.model_dump()}

@app.post("/api/v1/simulator/pitch-script/stop")
async def stop_pitch_script():
    global pitch_script_task, pitch_script_status, active_simulator_fault
    if pitch_script_task and not pitch_script_task.done():
        pitch_script_task.cancel()
    pitch_script_status = None
    active_simulator_fault = "normal"
    return {"status": "stopped", "active_fault": "normal"}
