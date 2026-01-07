from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.lifecycle.filters import ShowDeleted, by_show_deleted, FIELDS


class TeacherAssignmentReadModel:
    def __init__(self, db: Database) -> None:
        self._collection: Collection = db["teacher_subject_assignments"]

    def _oid(self, v: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    def _q(
        self,
        extra: Optional[Dict[str, Any]] = None,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any]:
        return by_show_deleted(show_deleted, dict(extra or {}))


    def get_active_by_class_subject(
        self,
        class_id: Union[str, ObjectId],
        subject_id: Union[str, ObjectId],
    ) -> Optional[dict]:
        cid = self._oid(class_id)
        sid = self._oid(subject_id)
        q = self._q({"class_id": cid, "subject_id": sid}, show_deleted="active")
        return self._collection.find_one(q)

    def find_one_active(self, *, class_id: ObjectId, subject_id: ObjectId) -> Optional[dict]:
        return self.get_active_by_class_subject(class_id, subject_id)

    def list_for_class(
        self,
        class_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[dict]:
        cid = self._oid(class_id)
        q = self._q({"class_id": cid}, show_deleted=show_deleted)
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))

    def list_for_teacher(
        self,
        teacher_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[dict]:
        tid = self._oid(teacher_id)
        q = self._q({"teacher_id": tid}, show_deleted=show_deleted)
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))


    def exists(
        self,
        filters: Dict[str, Any],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> bool:
        q = by_show_deleted(show_deleted, filters)
        doc = self._collection.find_one(q, projection={"_id": 1})
        return doc is not None