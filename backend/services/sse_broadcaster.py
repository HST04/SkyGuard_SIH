import asyncio
import json
from typing import Set, Dict, Any
from backend.schemas import TelemetryPayload, AnomalyEvent

class SSEBroadcaster:
    def __init__(self):
        self._clients: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def register(self) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._clients.add(queue)
        return queue

    async def unregister(self, queue: asyncio.Queue):
        async with self._lock:
            self._clients.discard(queue)

    async def broadcast_telemetry(self, payload: TelemetryPayload):
        msg = f"event: telemetry\ndata: {payload.model_dump_json()}\n\n"
        await self._dispatch(msg)

    async def broadcast_anomaly(self, anomaly: AnomalyEvent):
        msg = f"event: anomaly\ndata: {anomaly.model_dump_json()}\n\n"
        await self._dispatch(msg)

    async def broadcast_decision(self, decision: Any):
        data_str = decision.model_dump_json() if hasattr(decision, "model_dump_json") else json.dumps(decision)
        msg = f"event: decision_event\ndata: {data_str}\n\n"
        await self._dispatch(msg)

    async def broadcast_custom(self, event_name: str, data: Dict[str, Any]):
        msg = f"event: {event_name}\ndata: {json.dumps(data)}\n\n"
        await self._dispatch(msg)

    async def _dispatch(self, message: str):
        async with self._lock:
            dead_queues = []
            for q in self._clients:
                try:
                    if q.full():
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                    q.put_nowait(message)
                except Exception:
                    dead_queues.append(q)
            for dq in dead_queues:
                self._clients.discard(dq)

sse_broadcaster = SSEBroadcaster()
