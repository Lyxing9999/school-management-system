from __future__ import annotations
from contextlib import contextmanager
from pymongo.database import Database


@contextmanager
def mongo_transaction(db: Database):
    """
    Uses a transaction if MongoDB supports it (replica set).
    If not supported, it still executes the block without transaction.
    """
    client = db.client
    try:
        with client.start_session() as session:
            with session.start_transaction():
                yield session
    except Exception:
        # fallback: run without session
        yield None