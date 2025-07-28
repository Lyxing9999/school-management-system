from app.extensions import mongo_client

import logging

def get_db(name="mvp-lite"):
    if mongo_client is None:
        raise RuntimeError("MongoClient not initialized. Did you forget to call init_extensions(app)?")
    logging.debug(f"Accessing MongoDB database: {name}")
    return mongo_client[name]