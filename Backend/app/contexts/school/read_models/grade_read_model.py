
import re
from datetime import datetime
from typing import Any, Dict, Optional, Union, Literal, List, Tuple
import math


from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import (
    ShowDeleted,
    by_show_deleted,
    build_date_range,
    FIELDS,
)
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.school.domain.grade import GradeType
PASS_MARK: int = 50
SortDir = Literal[1, -1]


_MAX_PAGE_SIZE = 200
_SEARCH_ID_CAP = 50  


class GradeReadModel:
    def __init__(
        self,
        db: Database,
        *,
        student_read: StudentReadModel = None,
        subject_read: SubjectReadModel = None,
    ):
        """
        student_read/subject_read are OPTIONAL dependencies used for search `q`.
        If you don't pass them, `q` still works for type/term and ObjectId direct hits.
        """
        self.collection: Collection = db["grades"]
        self.student_read = student_read
        self.subject_read = subject_read


    # -----------------------------
    # Helpers
    # -----------------------------


    def _oid(self, v: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    def get_by_id(self, id_: Union[str, ObjectId]) -> dict | None:
        return self.collection.find_one({"_id": self._oid(id_)})

    def _q(
        self,
        extra: Optional[Dict[str, Any]] = None,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any]:
        return by_show_deleted(show_deleted, dict(extra or {}))

    def _normalize_page(self, page: int, page_size: int) -> Tuple[int, int, int]:
        p = int(page or 1)
        s = int(page_size or 10)

        if p < 1:
            p = 1
        if s < 1:
            s = 10
        if s > _MAX_PAGE_SIZE:
            s = _MAX_PAGE_SIZE

        skip = (p - 1) * s
        return p, s, skip

    def _term_filter(self, term: Optional[str]) -> Dict[str, Any]:
        """
        Supports:
          - "2025-S1" -> exact match
          - "S1"/"S2" -> suffix match "-S1"/"-S2" (any year)
        """
        if not term:
            return {}

        t = str(term).strip()
        if not t:
            return {}

        if t in ("S1", "S2"):
            return {"term": {"$regex": f"-{t}$"}}

        return {"term": t}

    def _type_filter(self, grade_type: Optional[str]) -> Dict[str, Any]:
        if not grade_type:
            return {}
        t = str(grade_type).strip()
        return {"type": t} if t else {}

    def _sort(self, sort: str) -> List[Tuple[str, int]]:
        """
        Stable sorting:
          - "-created_at" (default) newest first
          - "created_at"
          - "-updated_at"
          - "-score"
        Adds "_id" tie-breaker for stable pagination.
        """
        s = str(sort or "-created_at").strip()
        dir_: SortDir = -1 if s.startswith("-") else 1
        key = s[1:] if s.startswith("-") else s

        if key == "created_at":
            return [(FIELDS.k(FIELDS.created_at), dir_), ("_id", dir_)]
        if key == "updated_at":
            return [(FIELDS.k(FIELDS.updated_at), dir_), ("_id", dir_)]
        if key == "score":
            return [("score", dir_), ("_id", dir_)]

        # fallback
        return [(FIELDS.k(FIELDS.created_at), -1), ("_id", -1)]

    def _normalize_out_ids(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert ObjectId fields to strings for JSON response.
        Uses "id" (not "_id") to match your API shape.
        """
        out = dict(doc)

        if "_id" in out:
            out["id"] = str(out.pop("_id"))

        for k in ("class_id", "student_id", "teacher_id", "subject_id"):
            if k in out and isinstance(out[k], ObjectId):
                out[k] = str(out[k])

        return out

    def _search_filter(self, q: Optional[str]) -> Dict[str, Any]:
        """
        Search strategy:
          1) If q is ObjectId => allow direct hits on student_id/subject_id/teacher_id
          2) Else resolve student_ids / subject_ids using read models (if injected)
          3) Always allow partial match on type + term (safe regex)
        """
        if not q:
            return {}

        text = str(q).strip()
        if not text:
            return {}

        # direct ObjectId match (useful debugging + power users)
        if ObjectId.is_valid(text):
            oid = ObjectId(text)
            return {"$or": [{"student_id": oid}, {"subject_id": oid}, {"teacher_id": oid}]}

        safe = re.escape(text)
        ors: List[Dict[str, Any]] = []

        # Resolve IDs by name/code if dependencies exist
        if self.student_read is not None and hasattr(self.student_read, "search_ids_by_name"):
            ids = self.student_read.search_ids_by_name(text) or []
            ids = ids[:_SEARCH_ID_CAP]
            if ids:
                ors.append({"student_id": {"$in": ids}})

        if self.subject_read is not None and hasattr(self.subject_read, "search_ids_by_label_or_code"):
            ids = self.subject_read.search_ids_by_label_or_code(text) or []
            ids = ids[:_SEARCH_ID_CAP]
            if ids:
                ors.append({"subject_id": {"$in": ids}})

        # Lightweight fallbacks (no extra queries)
        ors.append({"type": {"$regex": safe, "$options": "i"}})
        ors.append({"term": {"$regex": safe, "$options": "i"}})

        return {"$or": ors} if ors else {}

    def _build_match(
        self,
        *,
        class_id: Optional[Union[str, ObjectId]] = None,
        student_id: Optional[Union[str, ObjectId]] = None,
        subject_id: Optional[Union[str, ObjectId]] = None,
        term: Optional[str] = None,
        grade_type: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any]:
        match: Dict[str, Any] = {}

        if class_id is not None:
            match["class_id"] = self._oid(class_id)

        if student_id is not None:
            match["student_id"] = self._oid(student_id)

        if subject_id is not None:
            match["subject_id"] = self._oid(subject_id)

        match.update(self._term_filter(term))
        match.update(self._type_filter(grade_type))
        match.update(self._search_filter(q))

        match.update(
            build_date_range(
                FIELDS.k(FIELDS.created_at),
                date_from=date_from,
                date_to=date_to,
                end_exclusive=True,
            )
        )

        return self._q(match, show_deleted=show_deleted)

    # -----------------------------
    # Paged queries
    # -----------------------------


    def list_grades_for_class_paged(
        self,
        *,
        class_id: Union[str, ObjectId],
        teacher_id: Optional[Union[str, ObjectId]] = None,
        subject_id: Optional[Union[str, ObjectId]] = None,
        page: int = 1,
        page_size: int = 10,
        term: Optional[str] = None,
        grade_type: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort: str = "-created_at",
        show_deleted: ShowDeleted = "active",
        projection: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        page, page_size, skip = self._normalize_page(page, page_size)

        match = self._build_match(
            class_id=class_id,
            term=term,
            grade_type=grade_type,
            q=q,
            date_from=date_from,
            date_to=date_to,
            show_deleted=show_deleted,
        )

        # optional extra filters
        if teacher_id is not None:
            match["teacher_id"] = self._oid(teacher_id)

        if subject_id is not None:
            match["subject_id"] = self._oid(subject_id)

        total = int(self.collection.count_documents(match))
        sort_spec = self._sort(sort)

        cursor = (
            self.collection.find(match, projection)
            .sort(sort_spec)
            .skip(skip)
            .limit(page_size)
        )

        items = [self._normalize_out_ids(doc) for doc in cursor]
        pages = max((total + page_size - 1) // page_size, 1)

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }
    def list_grades_for_student_paged(
        self,
        student_id: Union[str, ObjectId],
        *,
        page: int = 1,
        page_size: int = 10,
        term: Optional[str] = None,
        grade_type: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        class_id: Optional[Union[str, ObjectId]] = None,
        subject_id: Optional[Union[str, ObjectId]] = None,
        show_deleted: ShowDeleted = "active",
        sort: str = "-created_at",
        projection: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        page, page_size, skip = self._normalize_page(page, page_size)

        query = self._build_match(
            student_id=student_id,
            term=term,
            grade_type=grade_type,
            q=q,
            date_from=date_from,
            date_to=date_to,
            class_id=class_id,
            subject_id=subject_id,
            show_deleted=show_deleted,
        )

        total = int(self.collection.count_documents(query))
        sort_spec = self._sort(sort)

        cursor = (
            self.collection.find(query, projection)
            .sort(sort_spec)
            .skip(skip)
            .limit(page_size)
        )

        items = [self._normalize_out_ids(doc) for doc in cursor]
        pages = max((total + page_size - 1) // page_size, 1)

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }


    # -----------------------------
    # Aggregations
    # -----------------------------

    def aggregate_avg_score_by_subject(
        self,
        *,
        class_id: Optional[Union[str, ObjectId]] = None,
        term: Optional[str] = None,
        grade_type: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        match = self._build_match(
            class_id=class_id,
            term=term,
            grade_type=grade_type,
            date_from=date_from,
            date_to=date_to,
            show_deleted=show_deleted,
            q=q,
        )

        pipeline: List[Dict[str, Any]] = [
            {"$match": match},
            {
                "$group": {
                    "_id": "$subject_id",
                    "avg_score": {"$avg": "$score"},
                    "sample_size": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "subject_id": {"$toString": "$_id"},
                    "avg_score": {"$round": ["$avg_score", 2]},
                    "sample_size": 1,
                }
            },
            {"$sort": {"subject_id": 1}},
        ]
        return list(self.collection.aggregate(pipeline))

    def aggregate_grade_distribution(
        self,
        *,
        class_id: Optional[Union[str, ObjectId]] = None,
        term: Optional[str] = None,
        grade_type: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        match = self._build_match(
            class_id=class_id,
            term=term,
            grade_type=grade_type,
            date_from=date_from,
            date_to=date_to,
            show_deleted=show_deleted,
            q=q,
        )

        pipeline: List[Dict[str, Any]] = [
            {"$match": match},
            {
                "$project": {
                    "bucket": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lt": ["$score", 50]}, "then": "0-49"},
                                {
                                    "case": {"$and": [{"$gte": ["$score", 50]}, {"$lt": ["$score", 70]}]},
                                    "then": "50-69",
                                },
                                {
                                    "case": {"$and": [{"$gte": ["$score", 70]}, {"$lt": ["$score", 90]}]},
                                    "then": "70-89",
                                },
                            ],
                            "default": "90-100",
                        }
                    }
                }
            },
            {"$group": {"_id": "$bucket", "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "range": "$_id", "count": 1}},
        ]

        rows = list(self.collection.aggregate(pipeline))
        order = ["0-49", "50-69", "70-89", "90-100"]
        rows.sort(key=lambda r: order.index(r["range"]) if r["range"] in order else 999)
        return rows

    def aggregate_pass_rate_by_class(
        self,
        *,
        term: Optional[str] = None,
        grade_type: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        pass_mark: int = PASS_MARK,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        match = self._build_match(
            term=term,
            grade_type=grade_type,
            date_from=date_from,
            date_to=date_to,
            show_deleted=show_deleted,
            q=q,
        )

        pipeline: List[Dict[str, Any]] = [
            {"$match": match},
            {
                "$group": {
                    "_id": "$class_id",
                    "avg_score": {"$avg": "$score"},
                    "total": {"$sum": 1},
                    "passed": {"$sum": {"$cond": [{"$gte": ["$score", pass_mark]}, 1, 0]}},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "class_id": {"$toString": "$_id"},
                    "avg_score": {"$round": ["$avg_score", 2]},
                    "total": 1,
                    "passed": 1,
                    "pass_rate": {
                        "$cond": [
                            {"$gt": ["$total", 0]},
                            {"$round": [{"$divide": ["$passed", "$total"]}, 4]},
                            None,
                        ]
                    },
                }
            },
            {"$sort": {"class_id": 1}},
        ]
        return list(self.collection.aggregate(pipeline))