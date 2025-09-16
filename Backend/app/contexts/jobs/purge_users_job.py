from datetime import datetime, timedelta
from typing import Union, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import logging
from app.contexts.users.error.user_exceptions import NotFoundUserException

logger = logging.getLogger(__name__)

class UserCleanupJob:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db["users"]

    def purge_soft_deleted_users(self) -> Dict[str, int]:
        """Permanently delete users soft-deleted for 30+ days."""
        threshold = datetime.utcnow() - timedelta(days=30)
        result = self.collection.delete_many({
            "is_deleted": True,
            "deleted_at": {"$lte": threshold}
        })
        logger.info(f"Purged {result.deleted_count} users soft-deleted >30 days")
        return {"purged": result.deleted_count}

    def delete_user(self, user_id: Union[str, ObjectId], deleted_by: Union[str, ObjectId]) -> Dict[str, Any]:
        """Soft delete user and track who deleted them"""
        validated_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        deleter_id = ObjectId(deleted_by) if isinstance(deleted_by, str) else deleted_by

        # Log operation
        logger.info(f"Soft deleting user {validated_id} by {deleter_id}")

        # Find the user
        raw = self.collection.find_one({"_id": validated_id})
        if not raw:
            raise NotFoundUserException(user_id)

        # Soft delete
        update_data = {
            "deleted_at": datetime.utcnow(),
            "deleted_by": deleter_id,
            "is_deleted": True
        }
        self.collection.update_one({"_id": validated_id}, {"$set": update_data})

        # Wrap response
        return {
            "deleted_user": {
                "id": str(raw["_id"]),
                "email": raw.get("email"),
                "role": raw.get("role"),
                "username": raw.get("username"),
            },
            "deleted_by": str(deleter_id),
            "deleted_at": update_data["deleted_at"].isoformat()
        }