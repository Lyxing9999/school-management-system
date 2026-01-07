from flask import request
from flask_socketio import join_room
import jwt

from app.contexts.iam.auth.jwt_utils import SECRET_KEY, ALGORITHM
from app.contexts.infra.realtime.socketio_ext import socketio

@socketio.on("connect", namespace="/")
def on_connect():
    token = request.args.get("token")
    if not token:
        return False

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return False

    user_id = str(payload.get("id") or "")
    if not user_id:
        return False
    join_room(user_id)
    return True