# app/__init__.py
from flask import Flask, request, g
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from flask_swagger_ui import get_swaggerui_blueprint

import uuid

from app.contexts.core.config.setting import settings
from app.contexts.infra.database.extensions import init_extensions
from app.contexts.infra.http.errors import register_error_handlers
from app.contexts.infra.realtime.socketio_ext import init_socketio
from app.contexts.infra.database.db import get_db
from app.contexts.infra.database.indexes import ensure_indexes

oauth = OAuth()


def _normalize_origins(origins) -> list[str]:
    """
    Make origin matching predictable:
    - strip whitespace
    - remove trailing slash
    - unique values
    """
    out: list[str] = []
    for o in (origins or []):
        s = str(o or "").strip()
        if not s:
            continue
        if s.endswith("/"):
            s = s[:-1]
        out.append(s)

    # unique preserve order
    seen = set()
    uniq: list[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    allowed_origins = _normalize_origins(getattr(settings, "CORS_ALLOWED_ORIGINS", []))

    # 1) Flask-CORS (normal path) — scope only to API/upload
    CORS(
        app,
        resources={
            r"/api/*": {"origins": allowed_origins},
            r"/uploads/*": {"origins": allowed_origins},
        },
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Request-Id"],
        expose_headers=["X-Request-Id"],
        max_age=600,
        vary_header=True,
        always_send=True,
    )

    # 2) before_request
    @app.before_request
    def _before():
        # Request id for tracing
        g.request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

        # Optional: fast-return preflight
        if request.method == "OPTIONS":
            return ("", 200)

    # 3) after_request: force headers even on error responses / early returns
    @app.after_request
    def _after(resp):
        resp.headers["X-Request-Id"] = getattr(g, "request_id", "")

        origin = request.headers.get("Origin")
        if origin:
            origin = origin[:-1] if origin.endswith("/") else origin

        # Only allow exact origins (required when credentials = true)
        if origin and origin in allowed_origins:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-Id"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            # optional but helpful for preflight caching
            resp.headers["Access-Control-Max-Age"] = "600"

        return resp

    # Extensions + errors + realtime
    init_extensions(app)
    register_error_handlers(app)
    init_socketio(app)

    # OAuth (optional)
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url=settings.GOOGLE_DISCOVERY_URL,
        client_kwargs={"scope": "openid email profile"},
    )

    # Blueprints
    from app.uploads.students import upload_bp
    from app.contexts.iam.routes.iam_route import iam_bp
    from app.contexts.admin.routes import admin_bp, register_routes
    from app.contexts.student.routes import student_bp, register_routes as register_student_routes
    from app.contexts.teacher.routes import teacher_bp, register_routes as register_teacher_routes
    from app.contexts.notifications.routes.notification_route import notification_bp

    app.register_blueprint(upload_bp, url_prefix="/uploads")
    app.register_blueprint(iam_bp, url_prefix="/api/iam")

    register_routes()
    register_student_routes()
    register_teacher_routes()

    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(teacher_bp, url_prefix="/api/teacher")
    app.register_blueprint(notification_bp, url_prefix="/api/notifications")

    # Swagger UI
    app.register_blueprint(
        get_swaggerui_blueprint(
            "/api/docs",
            "/api/docs/openapi.yaml",
            config={"app_name": "School Management System"},
        ),
        url_prefix="/api/docs",
    )

    if getattr(settings, "DEBUG", False):
        for rule in app.url_map.iter_rules():
            print(f"{rule} -> methods: {rule.methods}")

    # Indexes (run inside app context)
    with app.app_context():
        ensure_indexes(get_db())

    return app