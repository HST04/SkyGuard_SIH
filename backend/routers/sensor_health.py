from fastapi import APIRouter, Query

from config import settings
from models.schemas import ImputationAcceptRequest
from services.sensor_health import sensor_health
from services.sse_manager import sse_manager

router = APIRouter(tags=["Maintenance & Imputation"])


@router.get("/maintenance")
async def get_maintenance(station_id: str = Query(settings.STATION_ID)):
    """Current drift state, baseline fit, and recently accepted imputations."""
    return sensor_health.snapshot(station_id)


@router.post("/imputation/accept")
async def accept_imputation(body: ImputationAcceptRequest):
    """Operator clicked "Accept & Impute" on the Data Repair tab."""
    rec = sensor_health.accept_imputation(body.model_dump())
    await sse_manager.broadcast("imputation_accepted", rec)
    return {"status": "success", "record": rec}
