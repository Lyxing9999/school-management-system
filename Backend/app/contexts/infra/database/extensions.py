from flask_cors import CORS 
from pymongo import MongoClient 
from flask_debugtoolbar import DebugToolbarExtension 
from app.contexts.core.config.setting import settings
from app.contexts.infra.http.errors import register_error_handlers
cors = CORS()
mongo_client = None
toolbar = DebugToolbarExtension()

def init_extensions(app):
    global mongo_client
    app.config["DATABASE_URI"] = settings.DATABASE_URI
    if mongo_client is None:
        mongo_client = MongoClient(app.config["DATABASE_URI"])
    cors.init_app(app)
    toolbar.init_app(app)
    register_error_handlers(app)