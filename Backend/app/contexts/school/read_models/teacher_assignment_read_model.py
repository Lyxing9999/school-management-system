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

    @staticmethod
    def _match_oid_or_str(field: str, oid: ObjectId) -> Dict[str, Any]:
        # Works when DB stores either ObjectId(...) OR "..."
        return {"$or": [{field: oid}, {field: str(oid)}]}

    def get_active_by_class_subject(
        self,
        class_id: Union[str, ObjectId],
        subject_id: Union[str, ObjectId],
    ) -> Optional[dict]:
        cid = self._oid(class_id)
        sid = self._oid(subject_id)

        q = self._q(
            {
                "$and": [
                    self._match_oid_or_str("class_id", cid),
                    self._match_oid_or_str("subject_id", sid),
                ]
            },
            show_deleted="active",
        )
        return self._collection.find_one(q)

    def list_for_class(
        self,
        class_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[dict]:
        cid = self._oid(class_id)
        q = self._q(self._match_oid_or_str("class_id", cid), show_deleted=show_deleted)
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))

    def list_for_teacher(
        self,
        teacher_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[dict]:
        tid = self._oid(teacher_id)
        q = self._q(self._match_oid_or_str("teacher_id", tid), show_deleted=show_deleted)
        return list(self._collection.find(q).sort(FIELDS.k(FIELDS.created_at), -1))

    def exists(
        self,
        filters: Dict[str, Any],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> bool:
        q = self._q(filters, show_deleted=show_deleted)
        doc = self._collection.find_one(q, projection={"_id": 1})
        return doc is not None


    def list_subject_ids_for_teacher_in_class(
        self,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[ObjectId]:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)

        q = self._q({"teacher_id": tid, "class_id": cid}, show_deleted=show_deleted)
        docs = list(self._collection.find(q, projection={"subject_id": 1}))

        out: List[ObjectId] = []
        for d in docs:
            sid = d.get("subject_id")
            if isinstance(sid, ObjectId):
                out.append(sid)
            elif sid:
                # tolerate string ids
                out.append(self._oid(sid))
        return out



    def list_teacher_ids_for_class_subject(
        self,
        class_id: Union[str, ObjectId],
        subject_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[ObjectId]:
        cid = self._oid(class_id)
        sid = self._oid(subject_id)

        q = self._q({"class_id": cid, "subject_id": sid}, show_deleted=show_deleted)
        cursor = self._collection.find(q, projection={"teacher_id": 1})
        out: List[ObjectId] = []
        for d in cursor:
            tid = d.get("teacher_id")
            if tid:
                out.append(tid)
        # de-dup
        return list({ObjectId(str(x)) for x in out})