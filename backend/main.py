from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers.telemetry import router as telemetry_router
from routers.anomalies import router as anomalies_router
from routers.simulator import router as simulator_router
from simulator.edge_simulator import simulator
from services.mqtt_subscriber import mqtt_subscriber

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.MQTT_ENABLED:
        print("[SkyGuard Core] Starting MQTT telemetry subscriber...")
        mqtt_subscriber.start()
    else:
        print("[SkyGuard Core] Starting Virtual Edge Telemetry Simulator...")
        simulator.start()
    yield
    if settings.MQTT_ENABLED:
        print("[SkyGuard Core] Stopping MQTT telemetry subscriber...")
        mqtt_subscriber.stop()
    else:
        print("[SkyGuard Core] Stopping Virtual Edge Telemetry Simulator...")
        simulator.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Edge-to-Cloud Anomaly Detection Engine for Automatic Weather Stations with 3D Digital Twin",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(anomalies_router, prefix=settings.API_V1_STR)
app.include_router(simulator_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "station_id": settings.STATION_ID,
        "edge_simulator_running": simulator.running,
        "mqtt_enabled": settings.MQTT_ENABLED,
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to SkyGuard AI API Core",
        "docs_url": "/docs",
        "station_id": settings.STATION_ID,
        "stream_endpoint": f"{settings.API_V1_STR}/telemetry/stream"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
