import json
import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        logger.info("ws_connected", user_id=user_id, total_connections=sum(len(v) for v in self._connections.values()))

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info("ws_disconnected", user_id=user_id, total_connections=sum(len(v) for v in self._connections.values()))

    async def send_to_user(self, user_id: str, message: dict) -> None:
        if user_id not in self._connections:
            return
        payload = json.dumps(message)
        stale = set()
        for ws in self._connections[user_id]:
            try:
                await ws.send_text(payload)
            except Exception:
                stale.add(ws)
        for ws in stale:
            self._connections[user_id].discard(ws)
        if not self._connections[user_id]:
            del self._connections[user_id]

    async def broadcast(self, message: dict) -> None:
        payload = json.dumps(message)
        all_stale = set()
        for user_id, connections in list(self._connections.items()):
            for ws in connections:
                try:
                    await ws.send_text(payload)
                except Exception:
                    all_stale.add((user_id, ws))
        for user_id, ws in all_stale:
            self._connections[user_id].discard(ws)
            if not self._connections[user_id]:
                del self._connections[user_id]

    def get_connected_users(self) -> list[str]:
        return list(self._connections.keys())

    def get_connection_count(self) -> int:
        return sum(len(v) for v in self._connections.values())


manager = ConnectionManager()
