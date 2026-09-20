from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from data.store import store
from models.schemas import AnomalyEvent, AnomalyUpdateRequest, OperatorFeedback

router = APIRouter(prefix="/anomalies", tags=["Anomalies & Explainability"])

@router.get("", response_model=List[AnomalyEvent])
async def list_anomalies(
    status: Optional[str] = Query(None, description="Filter by status: open, acknowledged, resolved, false_alarm"),
    limit: int = Query(50, ge=1, le=200)
):
    """Lists detected anomalies, sorted by most recent."""
    return store.get_anomalies(status=status, limit=limit)

@router.get("/{anomaly_id}", response_model=AnomalyEvent)
async def get_anomaly(anomaly_id: str):
    """Get detailed anomaly with SHAP feature attribution."""
    anomaly = store.get_anomaly_by_id(anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly

@router.patch("/{anomaly_id}", response_model=AnomalyEvent)
async def update_anomaly(anomaly_id: str, payload: AnomalyUpdateRequest):
    """Operator action: acknowledge, resolve, or mark an anomaly."""
    updated = store.update_anomaly(anomaly_id, payload.status, payload.resolution_note)
    if not updated:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return updated

@router.post("/feedback", status_code=200)
async def submit_operator_feedback(feedback: OperatorFeedback):
    """
    Operator Active Learning Feedback loop.
    Flags false alarms or confirms faults for latent clustering & threshold tuning.
    """
    store.log_feedback(feedback)
    return {
        "status": "success",
        "message": f"Feedback logged for anomaly {feedback.anomaly_id}. Status marked as {feedback.label}.",
        "total_feedback_events": store.get_feedback_count()
    }
