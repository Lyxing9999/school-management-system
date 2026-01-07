from typing import Any, Dict, Iterable, List, Optional
from pymongo.cursor import Cursor
from pymongo.database import Database
import re
from bson import ObjectId
from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.shared.lifecycle.filters import ShowDeleted, by_show_deleted, not_deleted
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.student.domain.student import StudentStatus  

ACTIVE_STUDENT_STATUS = StudentStatus.ACTIVE.value  

class StudentReadModel(MongoErrorMixin):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db["students"]

        from app.contexts.iam.read_models.iam_read_model import IAMReadModel
        self._iam_read_model = IAMReadModel(db)

    def _oid(self, id_: str | ObjectId | None) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def _normalize_ids(self, ids: Iterable[str | ObjectId | None]) -> List[ObjectId]:
        normalized: List[ObjectId] = []
        for raw_id in ids:
            if raw_id is None:
                continue
            if isinstance(raw_id, str) and not raw_id.strip():
                continue
            normalized.append(self._oid(raw_id))
        return normalized
 
    # --------------------------
    # Core queries (no forced status)
    # --------------------------

    def get_by_user_id(
        self,
        user_id: ObjectId | str,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any] | None:
        uid = self._oid(user_id)
        try:
            return self.collection.find_one(by_show_deleted(show_deleted, {"user_id": uid}))
        except Exception as e:
            self._handle_mongo_error("get_by_user_id", e)
            return None

    def get_by_id(
        self,
        student_id: ObjectId | str,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any] | None:
        sid = self._oid(student_id)
        try:
            return self.collection.find_one(by_show_deleted(show_deleted, {"_id": sid}))
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)
            return None

    def get_me(self, user_id: ObjectId | str) -> Dict[str, Any] | None:
        return self.get_by_user_id(user_id)

    def get_by_student_code(
        self,
        code: str,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any] | None:
        code = (code or "").strip()
        if not code:
            return None
        try:
            return self.collection.find_one(by_show_deleted(show_deleted, {"student_id_code": code}))
        except Exception as e:
            self._handle_mongo_error("get_by_student_code", e)
            return None

    # --------------------------
    # BUSINESS-ACTIVE students (enforced)
    # --------------------------

    def count_active_students(self) -> int:
        try:
            return int(self.collection.count_documents(not_deleted({"status": ACTIVE_STUDENT_STATUS})))
        except Exception as e:
            self._handle_mongo_error("count_active_students", e)
            return 0

    def find_active_students_by_ids(self, student_ids: List[ObjectId | str]) -> Cursor:
        ids = self._normalize_ids(student_ids)
        query = not_deleted({"_id": {"$in": ids}, "status": ACTIVE_STUDENT_STATUS})
        return self.collection.find(query)

    # --------------------------
    # Names / options (default to business-active)
    # --------------------------

    def list_student_names_by_ids(
        self,
        student_ids: Iterable[ObjectId | str | None],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        ids = self._normalize_ids(student_ids)
        if not ids:
            return []

        projection = {
            "first_name_en": 1,
            "last_name_en": 1,
            "first_name_kh": 1,
            "last_name_kh": 1,
        }

        extra: Dict[str, Any] = {"_id": {"$in": ids}}

        if show_deleted == "active":
            extra["status"] = ACTIVE_STUDENT_STATUS

        try:
            cursor = self.collection.find(by_show_deleted(show_deleted, extra), projection)
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_student_names_by_ids", e)
            return []

    def list_student_name_options(
        self,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, int]] = None,
        limit: Optional[int] = None,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        extra = dict(filter or {})

        proj = projection or {
            "_id": 1,
            "first_name_en": 1,
            "last_name_en": 1,
            "first_name_kh": 1,
            "last_name_kh": 1,
        }

        if show_deleted == "active" and "status" not in extra:
            extra["status"] = ACTIVE_STUDENT_STATUS

        try:
            cursor = self.collection.find(by_show_deleted(show_deleted, extra), proj)
            if limit is not None:
                cursor = cursor.limit(int(limit))
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_student_name_options", e)
            return []

    # --------------------------
    # Class membership (default to business-active)
    # --------------------------

    def list_student_ids_in_class(
        self,
        class_id: ObjectId | str,
        *,
        session=None,
        show_deleted: ShowDeleted = "active",
    ) -> set[ObjectId]:
        cid = self._oid(class_id)

        extra: Dict[str, Any] = {"current_class_id": cid}
        if show_deleted == "active":
            extra["status"] = ACTIVE_STUDENT_STATUS

        query = by_show_deleted(show_deleted, extra)

        try:
            cur = self.collection.find(query, {"_id": 1}, session=session)
            return {d["_id"] for d in cur if d.get("_id")}
        except Exception as e:
            self._handle_mongo_error("list_student_ids_in_class", e)
            return set()

    def list_students_in_class(
        self,
        class_id: ObjectId | str,
        *,
        projection: Optional[Dict[str, int]] = None,
        sort: Optional[List[tuple[str, int]]] = None,
        session=None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        cid = self._oid(class_id)

        extra: Dict[str, Any] = {"current_class_id": cid}
        if show_deleted == "active":
            extra["status"] = ACTIVE_STUDENT_STATUS

        query = by_show_deleted(show_deleted, extra)

        try:
            if projection is None:
                cur = self.collection.find(query, session=session)
            else:
                cur = self.collection.find(query, projection=projection, session=session)

            cur = cur.sort(sort if sort else [("lifecycle.created_at", -1)])
            return list(cur)
        except Exception as e:
            self._handle_mongo_error("list_students_in_class", e)
            return []

    # --------------------------
    # Generic utilities
    # --------------------------

    def exists(
        self,
        student_id: ObjectId | str,
        *,
        session=None,
        show_deleted: ShowDeleted = "active",
    ) -> bool:
        sid = self._oid(student_id)
        query = by_show_deleted(show_deleted, {"_id": sid})
        try:
            return self.collection.count_documents(query, limit=1, session=session) == 1
        except Exception as e:
            self._handle_mongo_error("exists", e)
            return False

    def get_current_class_id(
        self,
        student_id: ObjectId | str,
        *,
        session=None,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[ObjectId]:
        sid = self._oid(student_id)
        query = by_show_deleted(show_deleted, {"_id": sid})

        try:
            doc = self.collection.find_one(query, {"current_class_id": 1}, session=session)
            return doc.get("current_class_id") if doc else None
        except Exception as e:
            self._handle_mongo_error("get_current_class_id", e)
            return None

    def search_ids_by_name(
        self,
        text: str,
        *,
        limit: int = 50,
        show_deleted: ShowDeleted = "active",
        active_only: bool = True,
    ) -> List[ObjectId]:
        """
        Return student _id list matched by human search text.

        Rules:
          - If show_deleted="active": lifecycle.deleted_at == None (via by_show_deleted)
          - If active_only=True and show_deleted="active": status == ACTIVE
          - Multi-token search: every token must match at least one of the name fields
          - Fast path: student_id_code exact match
        """
        q = (text or "").strip()
        if not q:
            return []

        # Debug / direct ObjectId support
        if ObjectId.is_valid(q):
            return [ObjectId(q)]

        # Safety limits
        limit = int(limit or 50)
        if limit < 1:
            limit = 1
        if limit > 200:
            limit = 200

        # Fields we want to match (add/remove based on your schema)
        name_fields = [
            "first_name_en",
            "last_name_en",
            "first_name_kh",
            "last_name_kh",
            # if you store these in students collection, keep them:
            "full_name_en",
            "full_name_kh",
        ]

        # 1) Fast path: student code exact match (if user typed a code)
        #    Example: "STU-00012"
        #    If you want "starts with" behavior, convert to regex anchored with ^.
        code_query: Dict[str, Any] = {"student_id_code": q}

        base_extra: Dict[str, Any] = {}
        if show_deleted == "active" and active_only:
            base_extra["status"] = ACTIVE_STUDENT_STATUS

        try:
            code_hit = self.collection.find_one(
                by_show_deleted(show_deleted, {**base_extra, **code_query}),
                projection={"_id": 1},
            )
            if code_hit and code_hit.get("_id"):
                return [code_hit["_id"]]
        except Exception as e:
            self._handle_mongo_error("search_ids_by_name.code_hit", e)

        # 2) Tokenized name search
        tokens = [t for t in re.split(r"\s+", q) if t]
        if not tokens:
            return []

        # For each token, it must match at least one of the fields
        and_clauses: List[Dict[str, Any]] = []
        for tok in tokens:
            safe = re.escape(tok)
            and_clauses.append(
                {
                    "$or": [
                        {f: {"$regex": safe, "$options": "i"}}
                        for f in name_fields
                    ]
                }
            )

        name_query: Dict[str, Any]
        if len(and_clauses) == 1:
            name_query = and_clauses[0]
        else:
            name_query = {"$and": and_clauses}

        final_query = by_show_deleted(show_deleted, {**base_extra, **name_query})

        try:
            cur = self.collection.find(
                final_query,
                projection={"_id": 1},
            ).limit(limit)

            return [d["_id"] for d in cur if d.get("_id")]
        except Exception as e:
            self._handle_mongo_error("search_ids_by_name", e)
            return []