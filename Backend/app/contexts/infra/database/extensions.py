# app/contexts/infra/database/extensions.py
from flask_cors import CORS
from pymongo import MongoClient
from flask_debugtoolbar import DebugToolbarExtension
from app.contexts.core.config.setting import settings
from app.contexts.infra.http.errors import register_error_handlers

cors = CORS()
mongo_client: MongoClient | None = None
toolbar = DebugToolbarExtension()


def init_extensions(app):
    global mongo_client

    app.config["DATABASE_URI"] = settings.DATABASE_URI
    app.config["DATABASE_NAME"] = getattr(settings, "DATABASE_NAME", None)

    if mongo_client is None:
        mongo_client = MongoClient(app.config["DATABASE_URI"])

    cors.init_app(app)
    toolbar.init_app(app)
    register_error_handlers(app)


def get_mongo_client() -> MongoClient:
    if mongo_client is None:
        raise RuntimeError("MongoClient not initialized. Did you forget to call init_extensions(app)?")
    return mongo_client