from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from pymongo.database import Database
from pymongo.client_session import ClientSession
from pymongo.errors import ConfigurationError, OperationFailure


@contextmanager
def mongo_transaction(db: Database) -> Iterator[Optional[ClientSession]]:
    """
    Yield a MongoDB session running in a transaction when supported (replica set).
    If not supported, yield None and run without a transaction.

    IMPORTANT:
    - Your repository methods must accept `session: ClientSession | None`
      and pass it to pymongo ops only when not None.
    """
    client = db.client

    # Step 1: try to create a session
    try:
        session = client.start_session()
    except (ConfigurationError, OperationFailure):
        # No sessions => no transactions
        yield None
        return

    # Step 2: try to start a transaction
    try:
        with session:
            try:
                with session.start_transaction():
                    yield session
            except (ConfigurationError, OperationFailure):
                # Transactions unsupported (e.g. standalone)
                yield None
    finally:
        # `with session:` already ends it, but keep cleanup explicit/safe
        try:
            session.end_session()
        except Exception:
            pass