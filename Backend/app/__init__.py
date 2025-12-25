from flask import Flask, request
from app.contexts.core.config.setting import settings
from app.contexts.infra.database.extensions import init_extensions
from authlib.integrations.flask_client import OAuth
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from app.contexts.infra.http.errors import register_error_handlers

oauth = OAuth()

def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    # CORS
    CORS(
        app,
        origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # FORCE CORS headers on every response (including errors)
    @app.after_request
    def add_cors_headers(resp):
        origin = request.headers.get("Origin")
        if origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return resp

    # Extensions
    init_extensions(app)

    # global error handlers
    register_error_handlers(app)

    # OAuth
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url=settings.GOOGLE_DISCOVERY_URL,
        client_kwargs={"scope": "openid email profile"},
    )

    # Blueprints
    from .uploads.students import upload_bp
    from .contexts.iam.routes.iam_route import iam_bp
    from .contexts.admin.routes import admin_bp, register_routes
    from .contexts.student.routes import student_bp, register_routes as register_student_routes
    from .contexts.teacher.routes import teacher_bp, register_routes as register_teacher_routes

    app.register_blueprint(upload_bp, url_prefix="/uploads")
    app.register_blueprint(iam_bp, url_prefix="/api/iam")
    register_routes()
    register_student_routes()
    register_teacher_routes()
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(teacher_bp, url_prefix="/api/teacher")

    # Swagger UI
    app.register_blueprint(
        get_swaggerui_blueprint(
            "/api/docs",
            "/api/docs/openapi.yaml",
            config={"app_name": "School Management System"},
        ),
        url_prefix="/api/docs",
    )

    if settings.DEBUG:
        for rule in app.url_map.iter_rules():
            print(f"{rule} -> methods: {rule.methods}")

    return app