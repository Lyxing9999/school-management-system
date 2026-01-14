from datetime import timedelta
from typing import Iterable

import secrets
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from flask_swagger_ui import get_swaggerui_blueprint

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from werkzeug.middleware.proxy_fix import ProxyFix

from app.contexts.core.config.setting import settings
from app.contexts.infra.database.extensions import init_extensions
from app.contexts.infra.http.errors import register_error_handlers
from app.contexts.infra.realtime.socketio_ext import init_socketio
from app.contexts.infra.database.db import get_db
from app.contexts.infra.database.indexes import ensure_indexes

oauth = OAuth()


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=getattr(settings, "RATE_LIMIT_STORAGE_URI", "memory://"),
    strategy=getattr(settings, "RATE_LIMIT_STRATEGY", "fixed-window"),
    headers_enabled=True,
)


def _normalize_origins(origins: Iterable[str] | None) -> list[str]:
    """
    Make origin matching predictable:
    - strip whitespace
    - remove trailing slash
    - unique values (preserve order)
    """
    out: list[str] = []
    for o in (origins or []):
        s = str(o or "").strip()
        if not s:
            continue
        if s.endswith("/"):
            s = s[:-1]
        out.append(s)

    seen = set()
    uniq: list[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def _build_csp(allowed_origins: list[str]) -> str:
    """
    A pragmatic CSP that keeps Swagger UI and SPA working.
    Tighten in production if you remove inline scripts/styles.
    """
    connect_src = ["'self'"] + allowed_origins
    return "; ".join(
        [
            "default-src 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "img-src 'self' data:",
            "font-src 'self' data:",
            "style-src 'self' 'unsafe-inline'",
            "script-src 'self' 'unsafe-inline'",
            f"connect-src {' '.join(connect_src)}",
            "form-action 'self'",
        ]
    )


def _gen_request_id() -> str:
    return secrets.token_urlsafe(16)


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    # -------------------------
    # Senior security defaults
    # -------------------------
    app.config["MAX_CONTENT_LENGTH"] = getattr(settings, "MAX_CONTENT_LENGTH", 16 * 1024 * 1024)

    # Cookie security defaults (important if refresh token stored in cookies)
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"))
    app.config.setdefault("SESSION_COOKIE_SECURE", getattr(settings, "SESSION_COOKIE_SECURE", False))
    app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(days=7))

    # If behind proxy/LB, trust forwarded headers (HTTPS detection, client IP)
    if getattr(settings, "BEHIND_PROXY", False):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    allowed_origins = _normalize_origins(getattr(settings, "CORS_ALLOWED_ORIGINS", []))

    # -------------------------
    # CORS
    # -------------------------
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

    # -------------------------
    # Rate Limiting
    # -------------------------
    limiter.init_app(app)

    default_limits = getattr(settings, "RATE_LIMIT_DEFAULT", "300 per minute; 5000 per hour")
    limiter.default_limits = [x.strip() for x in default_limits.split(";") if x.strip()]

    # Stricter policy for auth endpoints
    auth_limit = getattr(settings, "RATE_LIMIT_AUTH", "10 per minute")
    reset_limit = getattr(settings, "RATE_LIMIT_PASSWORD_RESET", "5 per minute")

    def _is_auth_path(p: str) -> bool:
        return p.startswith("/api/iam/login") or p.startswith("/api/iam/refresh")

    def _is_reset_path(p: str) -> bool:
        return p.startswith("/api/iam/reset-password")

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return (
            jsonify(
                {
                    "error": "rate_limited",
                    "message": "Too many requests. Please slow down.",
                    "request_id": getattr(g, "request_id", ""),
                }
            ),
            429,
        )

    # -------------------------
    # Request lifecycle hooks
    # -------------------------
    @app.before_request
    def _before():
        # Request id for tracing
        g.request_id = request.headers.get("X-Request-Id") or _gen_request_id()

        # Fast-return preflight
        if request.method == "OPTIONS":
            return ("", 200)

        # Path-based stricter limits (no need to edit route decorators)
        path = request.path or ""
        if _is_auth_path(path):
            limiter.limit(auth_limit, override_defaults=False)(lambda: None)()
        elif _is_reset_path(path):
            limiter.limit(reset_limit, override_defaults=False)(lambda: None)()

    @app.after_request
    def _after(resp):
        # Always attach request id
        resp.headers["X-Request-Id"] = getattr(g, "request_id", "")

        # -------------------------
        # Security Headers (Senior)
        # -------------------------
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

        # HSTS only on HTTPS (or HTTPS detected via ProxyFix)
        if request.is_secure and getattr(settings, "ENABLE_HSTS", True):
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        # CSP (keep Swagger UI working)
        if getattr(settings, "ENABLE_CSP", True):
            resp.headers.setdefault("Content-Security-Policy", _build_csp(allowed_origins))

        # -------------------------
        # CORS: force headers even on errors/early returns
        # -------------------------
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
            resp.headers["Access-Control-Max-Age"] = "600"

        return resp

    # -------------------------
    # Extensions + errors + realtime
    # -------------------------
    init_extensions(app)
    register_error_handlers(app)
    init_socketio(app)

    # -------------------------
    # OAuth (optional)
    # -------------------------
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url=settings.GOOGLE_DISCOVERY_URL,
        client_kwargs={"scope": "openid email profile"},
    )

    # -------------------------
    # Blueprints
    # -------------------------
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