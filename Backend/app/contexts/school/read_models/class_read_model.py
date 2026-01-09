from typing import Optional, List, Dict, Any, Tuple
import re

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import ShowDeleted, by_show_deleted
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.school.domain.class_section import ClassSectionStatus


ACTIVE_CLASS_STATUS = ClassSectionStatus.ACTIVE.value


class ClassReadModel:
    """
    Read-side helper for Class data (plain Mongo dicts).

    Defaults are UI-safe:
    - show_deleted="active"  -> hide soft-deleted
    - only_active_status=True -> hide inactive/archived
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["classes"]

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def _oids(self, ids: List[str | ObjectId]) -> List[ObjectId]:
        return [self._oid(id_) for id_ in ids]

    def _q(
        self,
        extra: Optional[Dict[str, Any]] = None,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> Dict[str, Any]:
        """
        Build a mongo filter with consistent defaults.

        - show_deleted="active": excludes soft-deleted docs
        - only_active_status=True: defaults to status == 'active', but does NOT
          override an explicitly provided 'status' in extra.
        """
        filt = dict(extra or {})

        if only_active_status:
            # do NOT overwrite if caller explicitly passed status
            filt.setdefault("status", ACTIVE_CLASS_STATUS)

        return by_show_deleted(show_deleted, filt)

    # -----------------------------
    # Single fetches
    # -----------------------------

    def get_by_id(
        self,
        id_: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> Optional[Dict[str, Any]]:
        oid = self._oid(id_)
        return self.collection.find_one(
            self._q({"_id": oid}, show_deleted=show_deleted, only_active_status=only_active_status)
        )

    def get_by_name(
        self,
        name: str,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> Optional[Dict[str, Any]]:
        return self.collection.find_one(
            self._q({"name": name}, show_deleted=show_deleted, only_active_status=only_active_status)
        )

    def get_name_by_id(
        self,
        class_id: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> Optional[str]:
        oid = self._oid(class_id)
        doc = self.collection.find_one(
            self._q({"_id": oid}, show_deleted=show_deleted, only_active_status=only_active_status),
            {"name": 1},
        )
        return None if not doc else doc.get("name")

    # -----------------------------
    # Bulk fetches
    # -----------------------------

    def list_by_ids(
        self,
        class_ids: List[str | ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> List[Dict[str, Any]]:
        oids = self._oids(class_ids)
        if not oids:
            return []
        return list(
            self.collection.find(
                self._q({"_id": {"$in": oids}}, show_deleted=show_deleted, only_active_status=only_active_status)
            )
        )

    # -----------------------------
    # Paginated listing (UI/admin)
    # -----------------------------

    def list_page_numbered(
        self,
        *,
        q: str,
        status: str | None,
        include_deleted: bool,
        deleted_only: bool,
        page: int,
        page_size: int,
        only_active_status: bool = True,
        sort_archived_last: bool = False,  
    ) -> Tuple[List[Dict[str, Any]], int]:
        # Decide show_deleted mode
        if deleted_only:
            show_deleted: ShowDeleted = "deleted"
            only_active_status = False
        elif include_deleted:
            show_deleted = "all"
        else:
            show_deleted = "active"

        filt: Dict[str, Any] = {}

        # Explicit status filter overrides default
        if status:
            filt["status"] = ClassSectionStatus(status).value

        if q:
            rx = re.compile(re.escape(q), re.IGNORECASE)
            filt["$or"] = [{"name": rx}, {"code": rx}]

        mongo_filter = self._q(
            filt,
            show_deleted=show_deleted,
            only_active_status=only_active_status,
        )

        total = self.collection.count_documents(mongo_filter)
        skip = (page - 1) * page_size

        # If archived-last sorting requested AND not filtering to a single status,
        # use aggregation to keep pagination correct.
        if sort_archived_last and not status:
            pipeline = [
                {"$match": mongo_filter},
                {
                    "$addFields": {
                        "__status_rank": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$status", ClassSectionStatus.ACTIVE.value]}, "then": 0},
                                    {"case": {"$eq": ["$status", ClassSectionStatus.INACTIVE.value]}, "then": 1},
                                    {"case": {"$eq": ["$status", ClassSectionStatus.ARCHIVED.value]}, "then": 2},
                                ],
                                "default": 3,
                            }
                        }
                    }
                },
                {"$sort": {"__status_rank": 1, "_id": -1}},  # archived goes last
                {"$skip": skip},
                {"$limit": page_size},
                {"$unset": "__status_rank"},
            ]
            docs = list(self.collection.aggregate(pipeline))
            return docs, total

        # Default sort (unchanged behavior)
        docs = list(
            self.collection.find(mongo_filter)
            .sort([("_id", -1)])
            .skip(skip)
            .limit(page_size)
        )
        return docs, total
    # -----------------------------
    # Teacher-scoped queries (UI-safe by default)
    # -----------------------------

    def list_classes_for_teacher(
        self,
        homeroom_teacher_id: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> List[Dict[str, Any]]:
        oid = self._oid(homeroom_teacher_id)
        return list(
            self.collection.find(
                self._q(
                    {"homeroom_teacher_id": oid},
                    show_deleted=show_deleted,
                    only_active_status=only_active_status,
                )
            )
        )

    def count_classes_for_teacher(
        self,
        homeroom_teacher_id: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> int:
        oid = self._oid(homeroom_teacher_id)
        return self.collection.count_documents(
            self._q(
                {"homeroom_teacher_id": oid},
                show_deleted=show_deleted,
                only_active_status=only_active_status,
            )
        )

    def list_classes_for_teacher_with_summary(
        self,
        homeroom_teacher_id: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        oid = self._oid(homeroom_teacher_id)
        docs: List[Dict[str, Any]] = list(
            self.collection.find(
                self._q(
                    {"homeroom_teacher_id": oid},
                    show_deleted=show_deleted,
                    only_active_status=only_active_status,
                )
            )
        )

        total_classes = len(docs)
        total_students = 0
        total_subjects = 0

        for doc in docs:
            enrolled_count = doc.get("enrolled_count")
            if isinstance(enrolled_count, int):
                total_students += enrolled_count
            else:
                student_ids = doc.get("student_ids") or []
                if isinstance(student_ids, list):
                    total_students += len(student_ids)

            subject_ids = doc.get("subject_ids") or []
            if isinstance(subject_ids, list):
                total_subjects += len(subject_ids)

        summary = {
            "total_classes": total_classes,
            "total_students": total_students,
            "total_subjects": total_subjects,
        }

        return docs, summary

    # -----------------------------
    # Select helpers (UI-safe)
    # -----------------------------

    def list_class_names(
        self,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> List[Dict[str, Any]]:
        cursor = self.collection.find(
            self._q(show_deleted=show_deleted, only_active_status=only_active_status),
            {"name": 1},
        )
        return list(cursor)

    def list_class_name_options(
        self,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> List[Dict[str, str]]:
        cursor = self.collection.find(
            self._q(show_deleted=show_deleted, only_active_status=only_active_status),
            {"name": 1},
        )
        return [{"value": str(doc["_id"]), "label": doc.get("name", "")} for doc in cursor]

    def list_class_name_options_for_teacher(
        self,
        homeroom_teacher_id: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> List[Dict[str, str]]:
        oid = self._oid(homeroom_teacher_id)
        cursor = self.collection.find(
            self._q(
                {"homeroom_teacher_id": oid},
                show_deleted=show_deleted,
                only_active_status=only_active_status,
            ),
            {"name": 1},
        )
        return [{"value": str(doc["_id"]), "label": doc.get("name", "")} for doc in cursor]

    # -----------------------------
    # Class relations / subject list
    # -----------------------------

    def list_subject_ids_for_class(
        self,
        class_id: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,
    ) -> List[ObjectId]:
        oid = self._oid(class_id)
        doc = self.collection.find_one(
            self._q({"_id": oid}, show_deleted=show_deleted, only_active_status=only_active_status),
            {"subject_ids": 1},
        )
        if not doc:
            return []
        subject_ids = doc.get("subject_ids") or []
        return [self._oid(sid) for sid in subject_ids]

    def list_class_names_by_ids(
        self,
        class_ids: List[ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
        only_active_status: bool = True,  
    ) -> Dict[ObjectId, str]:
        if not class_ids:
            return {}

        cursor = self.collection.find(
            self._q(
                {"_id": {"$in": class_ids}},
                show_deleted=show_deleted,
                only_active_status=only_active_status,
            ),
            {"_id": 1, "name": 1},
        )

        result: Dict[ObjectId, str] = {}
        for doc in cursor:
            cid = doc.get("_id")
            name = doc.get("name")
            if cid is not None and name is not None:
                result[cid] = name
        return result

    # -----------------------------
    # Stats
    # -----------------------------

    def count_active_classes(self) -> int:
        return self.collection.count_documents(self._q(show_deleted="active", only_active_status=True))