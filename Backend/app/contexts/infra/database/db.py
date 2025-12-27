from app.contexts.infra.database.extensions import mongo_client
from app.contexts.infra.database import extensions
import logging


def get_db(name: str = "mvp-lite"):
    if extensions.mongo_client is None:
        raise RuntimeError("MongoClient not initialized. Did you forget to call init_extensions(app)?")
    logging.debug(f"Accessing MongoDB database: {name}")
    return extensions.mongo_client[name]