import asyncio
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List

from config import settings
from data.store import store
from models.schemas import TelemetryPayload, StationOverview
from services.sse_manager import sse_manager

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@router.get("/latest", response_model=Optional[TelemetryPayload])
async def get_latest_telemetry(station_id: str = Query(settings.STATION_ID)):
    """Hydration endpoint: gets the most recent telemetry packet."""
    return store.get_latest_telemetry()

@router.get("/history", response_model=List[TelemetryPayload])
async def get_telemetry_history(
    station_id: str = Query(settings.STATION_ID),
    limit: int = Query(60, ge=5, le=500)
):
    """Retrieves recent rolling telemetry history for chart visualization."""
    return store.get_telemetry_history(limit=limit)

@router.get("/overview", response_model=StationOverview)
async def get_station_overview(station_id: str = Query(settings.STATION_ID)):
    """Summary overview for Station AGRA-01."""
    latest = store.get_latest_telemetry()
    anomalies = store.get_anomalies(status="open", limit=10)
    
    # Determine station status
    status = "normal"
    if anomalies:
        highest_sev = max(a.severity_score for a in anomalies)
        status = "anomaly" if highest_sev >= 0.70 else "warning"

    return StationOverview(
        station_id=settings.STATION_ID,
        station_name=settings.STATION_NAME,
        latitude=settings.LATITUDE,
        longitude=settings.LONGITUDE,
        elevation_m=settings.ELEVATION_M,
        status=status,
        latest_telemetry=latest,
        active_anomalies=anomalies,
        total_anomalies_detected=len(store.get_anomalies(limit=500)),
        connection_status="connected"
    )

@router.get("/stream")
async def stream_telemetry(request: Request, station_id: str = Query(settings.STATION_ID)):
    """
    Server-Sent Events (SSE) live telemetry and anomaly stream at 1 Hz.
    Directly consumes from the Edge Telemetry Simulator.
    """
    async def event_generator():
        client_queue = await sse_manager.subscribe()
        try:
            # Yield immediate initial heartbeat + latest snapshot
            latest = store.get_latest_telemetry()
            if latest:
                yield f"event: telemetry\ndata: {latest.model_dump_json()}\n\n"

            while True:
                # Disconnect if client closed connection
                if await request.is_disconnected():
                    break

                try:
                    # Wait for next broadcast message or timeout for heartbeat
                    message = await asyncio.wait_for(client_queue.get(), timeout=15.0)
                    yield message
                except asyncio.TimeoutError:
                    yield f"event: heartbeat\ndata: {{\"status\": \"ok\", \"station\": \"{station_id}\"}}\n\n"
        finally:
            await sse_manager.unsubscribe(client_queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )
