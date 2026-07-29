import json
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.security import decode_token
from app.notifications.websocket_manager import manager

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    user_id_str = str(user_id)
    await manager.connect(user_id_str, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")

            if msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

            elif msg_type == "subscribe":
                pass

            elif msg_type == "unsubscribe":
                pass

            elif msg_type == "mark_read":
                notif_id = msg.get("notification_id")
                if notif_id:
                    await websocket.send_text(json.dumps({
                        "type": "ack",
                        "action": "mark_read",
                        "notification_id": notif_id,
                    }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("ws_error", user_id=user_id_str, error=str(e))
    finally:
        await manager.disconnect(user_id_str, websocket)
