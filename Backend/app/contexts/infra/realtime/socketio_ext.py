
from flask import Flask
from flask_socketio import SocketIO

from app.contexts.core.config.setting import settings

socketio = SocketIO(
    cors_allowed_origins=getattr(settings, "CORS_ALLOWED_ORIGINS", []),
    async_mode="eventlet",
    ping_timeout=20,
    ping_interval=25,
)


def init_socketio(app: Flask) -> SocketIO:
    socketio.init_app(app)
    return socketio