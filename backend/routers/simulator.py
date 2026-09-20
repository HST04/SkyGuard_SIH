from fastapi import APIRouter
from data.store import store
from models.schemas import FaultInjectionRequest, PitchScriptStatus
from simulator.edge_simulator import simulator

router = APIRouter(prefix="/simulator", tags=["Edge Simulator & Fault Injector"])

@router.post("/inject")
async def inject_fault(request: FaultInjectionRequest):
    """
    Injects a physical sensor fault or environmental transient into the virtual edge stream.
    Faults include: heat_spike, pressure_drop, stuck_humidity, humidity_drift, cross_decoupling, sensor_noise.
    """
    store.set_fault(
        fault_type=request.fault_type,
        intensity=request.intensity,
        duration_seconds=request.duration_seconds
    )
    return {
        "status": "success",
        "active_fault": request.fault_type,
        "intensity": request.intensity,
        "duration_seconds": request.duration_seconds
    }

@router.post("/reset")
async def reset_simulator():
    """Resets simulator to clean nominal weather with zero faults."""
    store.set_fault("normal")
    simulator.stop_pitch_script()
    return {"status": "success", "message": "Simulator reset to baseline normal."}

@router.post("/pitch-script/start")
async def start_pitch_script():
    """
    Launches the 5-Minute Auto-Scenario Pitch Script:
    - T+0:00 (Baseline): Normal diurnal cycle (Green)
    - T+1:30 (True Negative Test): Thunderstorm squall with valid physics (Green)
    - T+3:00 (Degradation Test): Injects subtle +15% capacitive humidity drift
    - T+3:45 (Detection): Autoencoder threshold trips, 3D Twin pulses Red, SHAP attribution opens
    """
    simulator.trigger_pitch_script()
    return {
        "status": "started",
        "message": "5-Minute Pitch Script initiated. Watch the 3D twin and live metrics update."
    }

@router.post("/pitch-script/stop")
async def stop_pitch_script():
    """Cancels running pitch script."""
    simulator.stop_pitch_script()
    return {"status": "stopped", "message": "Pitch script stopped."}

@router.get("/status")
async def get_simulator_status():
    """Returns current edge simulator status and pitch script progress."""
    pitch_status = simulator.get_pitch_script_status()
    return {
        "active_fault": store.get_active_fault(),
        "fault_intensity": store.get_fault_intensity(),
        "pitch_script": pitch_status.model_dump()
    }
