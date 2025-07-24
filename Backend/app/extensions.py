from flask_cors import CORS  # type: ignore
from pymongo import MongoClient # type: ignore
from flask_debugtoolbar import DebugToolbarExtension # type: ignore
from config import Config
from app.error.error_handlers import register_error_handlers
cors = CORS()
mongo_client = None
toolbar = DebugToolbarExtension()

def init_extensions(app):
    global mongo_client
    app.config["DATABASE_URI"] = Config.DATABASE_URI
    if mongo_client is None:
        mongo_client = MongoClient(app.config["DATABASE_URI"])
    cors.init_app(app)
    toolbar.init_app(app)
    register_error_handlers(app)