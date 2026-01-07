import re
from typing import Optional, List, Dict, Any, Union, Iterable, Tuple, Sequence
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.shared.lifecycle.filters import FIELDS, ShowDeleted, by_show_deleted
from app.contexts.shared.model_converter import mongo_converter

_LABEL_CODE_RE = re.compile(r"\((?P<code>[^)]+)\)")
_CODE_LIKE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$")


class SubjectReadModel(MongoErrorMixin):
    """
    Read-only access for subject documents.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.

    Soft-delete support via lifecycle filter:
      show_deleted = "active" (default) -> only not deleted
      show_deleted = "all"             -> include deleted + not deleted
      show_deleted = "deleted"         -> only deleted
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["subjects"]

    def _normalize_id(self, id_: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def _q(self, extra: Optional[Dict[str, Any]] = None, show_deleted: ShowDeleted = "active") -> Dict[str, Any]:
        return by_show_deleted(show_deleted, extra)

    def get_by_id(
        self,
        subject_id: Union[str, ObjectId],
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        oid = self._normalize_id(subject_id)
        try:
            return self.collection.find_one(self._q({"_id": oid}, show_deleted=show_deleted))
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)
            return None

    def get_by_code(
        self,
        code: str,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one(self._q({"code": code.upper()}, show_deleted=show_deleted))
        except Exception as e:
            self._handle_mongo_error("get_by_code", e)
            return None

    def get_by_name(
        self,
        name: str,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        try:
            return self.collection.find_one(self._q({"name": name}, show_deleted=show_deleted))
        except Exception as e:
            self._handle_mongo_error("get_by_name", e)
            return None

    def get_name_by_id(
        self,
        subject_id: Union[str, ObjectId],
        show_deleted: ShowDeleted = "active",
    ) -> Optional[str]:
        oid = self._normalize_id(subject_id)
        try:
            doc = self.collection.find_one(self._q({"_id": oid}, show_deleted=show_deleted), {"name": 1})
            if not doc:
                return None
            return doc.get("name")
        except Exception as e:
            self._handle_mongo_error("get_name_by_id", e)
            return None

    def get_code_by_id(
        self,
        subject_id: Union[str, ObjectId],
        show_deleted: ShowDeleted = "active",
    ) -> Optional[str]:
        oid = self._normalize_id(subject_id)
        try:
            doc = self.collection.find_one(self._q({"_id": oid}, show_deleted=show_deleted), {"code": 1})
            if not doc:
                return None
            return doc.get("code")
        except Exception as e:
            self._handle_mongo_error("get_code_by_id", e)
            return None

    def list_paginated(
        self,
        extra: Optional[Dict[str, Any]] = None,
        *,
        page: int = 1,
        page_size: int = 20,
        show_deleted: ShowDeleted = "active",
        sort: Optional[Sequence[tuple[str, int]]] = None,
        projection: Optional[Dict[str, int]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        page = max(1, int(page))
        page_size = max(1, min(200, int(page_size)))
        skip = (page - 1) * page_size

        query = self._q(extra, show_deleted=show_deleted)
        sort_spec = list(sort) if sort else [(FIELDS.k(FIELDS.created_at), -1)]

        try:
            total = self.collection.count_documents(query)
            cursor = (
                self.collection.find(query, projection)
                .sort(sort_spec)
                .skip(skip)
                .limit(page_size)
            )
            return list(cursor), total
        except Exception as e:
            self._handle_mongo_error("list_paginated", e)
            return [], 0

    def list_by_ids(
        self,
        subject_ids: List[Union[str, ObjectId]],
        show_deleted: ShowDeleted = "active",
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        if not subject_ids:
            return []

        normalized_ids = [self._normalize_id(sid) for sid in subject_ids]
        extra: Dict[str, Any] = {"_id": {"$in": normalized_ids}}

        if active_only:
            extra["is_active"] = True

        try:
            return list(self.collection.find(self._q(extra, show_deleted=show_deleted)))
        except Exception as e:
            self._handle_mongo_error("list_by_ids", e)
            return []

    def list_names_by_ids(
        self,
        subject_ids: Iterable[Union[str, ObjectId]],
        show_deleted: ShowDeleted = "active",
        active_only: bool = True,
    ) -> Dict[ObjectId, str]:
        normalized_ids = [self._normalize_id(sid) for sid in subject_ids]
        if not normalized_ids:
            return {}

        extra: Dict[str, Any] = {"_id": {"$in": normalized_ids}}
        if active_only:
            extra["is_active"] = True

        try:
            cursor = self.collection.find(self._q(extra, show_deleted=show_deleted), {"_id": 1, "name": 1})
            result: Dict[ObjectId, str] = {}
            for doc in cursor:
                _id = doc.get("_id")
                if _id is not None:
                    result[_id] = doc.get("name") or ""
            return result
        except Exception as e:
            self._handle_mongo_error("list_names_by_ids", e)
            return {}

    def list_codes_by_ids(
        self,
        subject_ids: Iterable[Union[str, ObjectId]],
        show_deleted: ShowDeleted = "active",
        active_only: bool = True,
    ) -> Dict[ObjectId, str]:
        normalized_ids = [self._normalize_id(sid) for sid in subject_ids]
        if not normalized_ids:
            return {}

        extra: Dict[str, Any] = {"_id": {"$in": normalized_ids}}
        if active_only:
            extra["is_active"] = True

        try:
            cursor = self.collection.find(self._q(extra, show_deleted=show_deleted), {"_id": 1, "code": 1})
            result: Dict[ObjectId, str] = {}
            for doc in cursor:
                _id = doc.get("_id")
                if _id is not None:
                    result[_id] = doc.get("code") or ""
            return result
        except Exception as e:
            self._handle_mongo_error("list_codes_by_ids", e)
            return {}

    def list_subject_for_class(
        self,
        class_id: Union[str, ObjectId],
        show_deleted: ShowDeleted = "active",
        active_only: bool = False,
    ) -> List[Dict[str, Any]]:
        oid = self._normalize_id(class_id)
        extra: Dict[str, Any] = {"class_id": oid}
        if active_only:
            extra["is_active"] = True

        try:
            cursor = self.collection.find(self._q(extra, show_deleted=show_deleted))
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_subject_for_class", e)
            return []

    def list_subject_ids_for_class(
        self,
        class_id: Union[str, ObjectId],
        show_deleted: ShowDeleted = "active",
        active_only: bool = False,
    ) -> List[ObjectId]:
        subjects = self.list_subject_for_class(class_id, show_deleted=show_deleted, active_only=active_only)
        return [s["_id"] for s in subjects if isinstance(s.get("_id"), ObjectId)]

    def count_active_subjects(self, show_deleted: ShowDeleted = "active") -> int:
        try:
            return self.collection.count_documents(self._q({"is_active": True}, show_deleted=show_deleted))
        except Exception as e:
            self._handle_mongo_error("count_active_subjects", e)
            return 0

    def list_all_name_select(
        self,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        query = self._q({"is_active": True}, show_deleted=show_deleted)
        projection = {"_id": 1, "name": 1}

        try:
            cursor = self.collection.find(query, projection).sort("name", 1)
            return [{"value": str(d["_id"]), "label": d.get("name", "")} for d in cursor]
        except Exception as e:
            self._handle_mongo_error("list_all_name_select", e)
            return []


    def search_ids_by_label_or_code(
        self,
        text: str,
        *,
        limit: int = 25,
        show_deleted: ShowDeleted = "active",
        active_only: bool = True,
    ) -> List[ObjectId]:
        """
        Resolve subject ids from human search text.

        Matches:
          - code: exact / prefix
          - name: contains (case-insensitive)
          - label-like: "Subject Name (CODE)" -> extracts CODE and searches it

        Returns:
          List[ObjectId] limited by `limit`.
        """
        q = (text or "").strip()
        if not q:
            return []

        limit = max(1, min(int(limit), 200))

        ors: list[dict] = []

        # 1) If user typed something like "Math (MATH)" extract "MATH"
        m = _LABEL_CODE_RE.search(q)
        if m:
            code_raw = (m.group("code") or "").strip()
            if code_raw:
                code = code_raw.upper()
                # exact and prefix (prefix regex can still use index if anchored)
                ors.append({"code": code})
                ors.append({"code": {"$regex": f"^{re.escape(code)}", "$options": "i"}})

        # 2) If the whole query looks like a code, treat it strongly as code
        if _CODE_LIKE_RE.match(q):
            code = q.upper()
            ors.append({"code": code})
            ors.append({"code": {"$regex": f"^{re.escape(code)}", "$options": "i"}})

        # 3) Always allow name contains (more flexible)
        # NOTE: contains regex is not index-friendly; acceptable for small/medium datasets.
        ors.append({"name": {"$regex": re.escape(q), "$options": "i"}})

        extra: dict = {"$or": ors} if ors else {}
        if active_only:
            extra["is_active"] = True

        try:
            cursor = (
                self.collection.find(self._q(extra, show_deleted=show_deleted), {"_id": 1})
                .limit(limit)
            )
            return [d["_id"] for d in cursor if isinstance(d.get("_id"), ObjectId)]
        except Exception as e:
            self._handle_mongo_error("search_ids_by_label_or_code", e)
            return []