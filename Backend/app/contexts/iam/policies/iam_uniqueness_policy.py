
from typing import Optional

from bson import ObjectId

from app.contexts.iam.errors.iam_exception import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.shared.lifecycle.filters import ShowDeleted


class IAMUniquenessPolicy:
    """
    Read-side uniqueness checks for IAM fields.

    Consistency rule:
    - Default to checking ONLY active (not-deleted) users.
    - Optionally allow checking against "all" if you want to reserve usernames/emails forever.
    """

    def __init__(self, iam_read_model: IAMReadModel):
        self._iam_read_model = iam_read_model

    def ensure_unique(
        self,
        *,
        username: Optional[str] = None,
        email: Optional[str] = None,
        exclude_user_id: Optional[ObjectId] = None,
        show_deleted: ShowDeleted = "active",
    ) -> None:
        username_norm = (username or "").strip()
        email_norm = (email or "").strip()

        query: dict = {"$or": []}

        if username_norm:
            query["$or"].append({"username": username_norm})
        if email_norm:
            query["$or"].append({"email": email_norm})

        if not query["$or"]:
            return

        if exclude_user_id:
            query = {"$and": [{"_id": {"$ne": exclude_user_id}}, query]}

        existing = self._iam_read_model.find_one(query, show_deleted=show_deleted)
        if not existing:
            return

        if username_norm and (existing.get("username") or "") == username_norm:
            raise UsernameAlreadyExistsException(username_norm)

        if email_norm and (existing.get("email") or "") == email_norm:
            raise EmailAlreadyExistsException(email_norm)