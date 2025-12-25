import jwt
from datetime import datetime, timedelta, timezone
from app.contexts.core.config.setting import settings
from functools import wraps
from flask import request, jsonify, g 


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def create_access_token(data: dict, expire_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def role_required(allowed_roles: list[str]):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"msg": "Missing or invalid token"}), 401       
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                role = payload.get("role")
                user_id = payload.get("id")
                username = payload.get("username")
                email = payload.get("email")
                
                if not role or role not in allowed_roles:
                    return jsonify({"msg": "Access denied: role not allowed"}), 403
                g.user = {
                    "id": user_id,
                    "role": role,
                    "username": username,
                    "email": email
                }

            except jwt.ExpiredSignatureError:
                return jsonify({"msg": "Token expired"}), 401
            except jwt.InvalidTokenError as e:
                return jsonify({"msg": "Invalid token"}), 401

            return f(*args, **kwargs)
        return wrapper
    return decorator


def login_required():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"msg": "Missing or invalid token"}), 401

            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

                if payload.get("type") and payload.get("type") != "access":
                    return jsonify({"msg": "Invalid token type"}), 401

                g.user = {
                    "id": payload.get("id"),
                    "role": payload.get("role"),
                    "username": payload.get("username"),
                    "email": payload.get("email"),
                }
            except jwt.ExpiredSignatureError:
                return jsonify({"msg": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"msg": "Invalid token"}), 401

            return f(*args, **kwargs)
        return wrapper
    return decorator