from typing import Optional, Union
from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.shared.lifecycle.filters import ShowDeleted


class NotificationRecipientResolver:
    def __init__(self, db: Database):
        self._student_read = StudentReadModel(db)
        self._staff_read = StaffReadModel(db)

    def _oid(self, v: Union[str, ObjectId, None]) -> Optional[ObjectId]:
        if v is None:
            return None
        try:
            return mongo_converter.convert_to_object_id(v)
        except Exception:
            return None

    def student_to_user_id(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[str]:
        sid = self._oid(student_id)
        if not sid:
            return None
        doc = self._student_read.get_by_id(sid, show_deleted=show_deleted)
        if not doc:
            return None
        uid = doc.get("user_id")
        return str(uid) if uid else None

    def staff_to_user_id(
        self,
        staff_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[str]:
        tid = self._oid(staff_id)
        if not tid:
            return None
        doc = self._staff_read.get_by_id(tid, show_deleted=show_deleted)
        if not doc:
            return None
        uid = doc.get("user_id")
        return str(uid) if uid else None

    def best_effort_user_id(
        self,
        maybe_user_or_staff_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[str]:
        # try resolve as staff_id first
        uid = self.staff_to_user_id(maybe_user_or_staff_id, show_deleted=show_deleted)
        if uid:
            return uid
        # fallback: assume already IAM user_id
        return str(maybe_user_or_staff_id) if maybe_user_or_staff_id else None