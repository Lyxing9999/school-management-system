from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator, Optional

from pymongo.database import Database
from pymongo.client_session import ClientSession


@lru_cache(maxsize=8)
def _transactions_supported(client_identity: int, client) -> bool:
    """
    Cached check per MongoClient instance.
    """
    try:
        info = client.admin.command("hello")    
        return bool(info.get("setName") or info.get("msg") == "isdbgrid")
    except Exception:
        return False


@contextmanager
def mongo_transaction(db: Database) -> Iterator[Optional[ClientSession]]:
    """
    Use only for multi-document operations that need atomicity.
    For single-document updates, do NOT use transactions (faster).
    """
    client = db.client

    if not _transactions_supported(id(client), client):
        yield None
        return

    session = client.start_session()
    try:
        with session:
            with session.start_transaction():
                yield session
    finally:
        try:
            session.end_session()
        except Exception:
            pass


def _sess(session: Optional[ClientSession]) -> dict:
    """
    Helper to pass session only when it exists.
    """
    return {"session": session} if session else {}