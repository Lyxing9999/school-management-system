from flask import Flask
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
    CORS(app, resources={r"/*": {"origins": "*"}})  # replace * with frontend URLs in prod

    # Extensions
    init_extensions(app)
    # global error handlers
    register_error_handlers(app)
    # OAuth
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url=settings.GOOGLE_DISCOVERY_URL,
        client_kwargs={'scope': 'openid email profile'},
    )

    # Blueprints
    from .uploads.students import upload_bp
    from .contexts.iam.routes import iam_bp
    from .contexts.academic.routes import academic_bp
    from .contexts.admin.routes import admin_bp, register_routes
    # from .contexts.hr.routes import hr_bp
    app.register_blueprint(upload_bp, url_prefix='/uploads')
    app.register_blueprint(iam_bp, url_prefix='/api/iam')
    app.register_blueprint(academic_bp, url_prefix='/api/academic')
    register_routes()
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    # app.register_blueprint(hr_bp, url_prefix='/api/hr')

    # Swagger UI
    app.register_blueprint(
        get_swaggerui_blueprint(
            '/api/docs',
            '/api/docs/openapi.yaml',  # centralized docs
            config={'app_name': 'School Management System'}
        ),
        url_prefix='/api/docs'
    )
    # Debug routes
    if settings.DEBUG:
        for rule in app.url_map.iter_rules():
            print(f"{rule} -> methods: {rule.methods}")

    return app