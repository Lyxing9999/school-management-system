from app.contexts.infra.realtime.socketio_ext import socketio

EVENT_NAME = "notification:new"

def emit_notification(user_id: str, payload: dict) -> None:
    try:
        socketio.emit(EVENT_NAME, payload, room=str(user_id), namespace="/")
    except Exception:
        pass