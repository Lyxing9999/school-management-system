from __future__ import annotations

from pymongo import MongoClient
from pymongo.database import Database

from app.contexts.core.config.setting import settings
from app.contexts.infra.database import extensions as db_ext


def get_job_db() -> Database:
    client = db_ext.mongo_client

    if client is None:
        uri = getattr(settings, "DATABASE_URI", None)
        if not uri:
            raise RuntimeError("DATABASE_URI is missing. Ensure your env/settings load in job scripts.")
        client = MongoClient(uri)

    db_name = getattr(settings, "DATABASE_NAME", None) or "mvp-lite"
    return client[db_name]