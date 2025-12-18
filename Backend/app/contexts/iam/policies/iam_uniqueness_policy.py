from __future__ import annotations

from typing import Optional
from bson import ObjectId

from app.contexts.iam.error.iam_exception import (
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
)
from app.contexts.iam.read_models.iam_read_model import IAMReadModel

class IAMUniquenessPolicy:
    """
    Read-side uniqueness checks for IAM fields.
    Used by services/factories for nice error messages.
    Note: DB unique indexes are still required for true enforcement.
    """

    def __init__(self, iam_read_model: IAMReadModel):
        self._iam_read_model = iam_read_model

    def ensure_unique(
        self,
        *,
        username: Optional[str] = None,
        email: Optional[str] = None,
        exclude_user_id: Optional[ObjectId] = None,
    ) -> None:
        query = {"$or": []}

        if username:
            query["$or"].append({"username": username})
        if email:
            query["$or"].append({"email": email})

        if not query["$or"]:
            return

        if exclude_user_id:
            query = {"$and": [{"_id": {"$ne": exclude_user_id}}, query]}

        existing = self._iam_read_model.find_one(query)
        if not existing:
            return

        if username and existing.get("username") == username:
            raise UsernameAlreadyExistsException(username)

        if email and existing.get("email") == email:
            raise EmailAlreadyExistsException(email)