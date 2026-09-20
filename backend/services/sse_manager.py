import asyncio
import json
import logging
from typing import Set, Dict, Any

logger = logging.getLogger("sse_manager")

class SSEBroadcastManager:
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subscribers.add(queue)
            logger.info(f"New SSE client connected. Total clients: {len(self._subscribers)}")
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        async with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)
                logger.info(f"SSE client disconnected. Total clients: {len(self._subscribers)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcasts an SSE message formatted as:
        event: <event_type>
        data: <json_string>
        """
        if not self._subscribers:
            return

        payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

        # Broadcast to all active subscriber queues non-blocking
        dead_queues = []
        async with self._lock:
            for q in self._subscribers:
                try:
                    if q.full():
                        # Drop oldest to avoid lag
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                    q.put_nowait(payload)
                except Exception:
                    dead_queues.append(q)

            for dead in dead_queues:
                if dead in self._subscribers:
                    self._subscribers.remove(dead)

    @property
    def client_count(self) -> int:
        return len(self._subscribers)

sse_manager = SSEBroadcastManager()
