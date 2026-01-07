import re
from typing import Any, Dict, Final, List, Optional, Tuple, Union

from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.shared.lifecycle.filters import ShowDeleted
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.services.display_name_service import DisplayNameService
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.student.domain.student import StudentStatus

class AdminReadModel(MongoErrorMixin):
    """
    High-level read-model facade for admin screens.

    Aggregates lower-level read models and exposes helper
    views that are already decorated with display names.

    Lifecycle consistency:
    - Default to active data (not deleted)
    - Where the underlying read model supports it, pass through show_deleted
    """

    def __init__(self, db: Database):
        self.db = db

        self._iam_read_model: Final[IAMReadModel] = IAMReadModel(self.db)
        self._staff_read_model: Final[StaffReadModel] = StaffReadModel(self.db)
        self._schedule_read_model: Final[ScheduleReadModel] = ScheduleReadModel(self.db)
        self._subject_read_model: Final[SubjectReadModel] = SubjectReadModel(self.db)
        self._class_read_model: Final[ClassReadModel] = ClassReadModel(self.db)
        self._student_read_model: Final[StudentReadModel] = StudentReadModel(self.db)

        self._display_name_service: Final[DisplayNameService] = DisplayNameService(
            iam_read_model=self._iam_read_model,
            staff_read_model=self._staff_read_model,
            class_read_model=self._class_read_model,
            subject_read_model=self._subject_read_model,
            student_read_model=self._student_read_model,
        )

    def _oid(self, id_: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def get_staff_by_user_id(self, user_id: ObjectId) -> Optional[dict]:
        return self._staff_read_model.get_by_user_id(user_id)

    def admin_get_student_by_user_id(
        self,
        user_id: ObjectId | str,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[dict]:
        uid = self._oid(user_id) if isinstance(user_id, str) else user_id
        return self._student_read_model.get_by_user_id(uid, show_deleted=show_deleted)

    def get_user_by_id(
        self,
        user_id: ObjectId | str,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[dict]:
        return self._iam_read_model.get_by_id(user_id, show_deleted=show_deleted)

    def get_page_by_role(
        self,
        roles: Union[str, List[str]],
        page: int = 1,
        page_size: int = 5,
        search: Optional[str] = None,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Tuple[List[dict], int]:
        return self._iam_read_model.get_page_by_role(
            roles=roles,
            page=page,
            page_size=page_size,
            search=search,
            show_deleted=show_deleted,
        )

    def admin_list_schedules_for_class_enriched(
        self,
        class_id: Union[str, ObjectId],
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        oid = self._oid(class_id)

        items, total = self._schedule_read_model.list_schedules_for_class_paginated(
            class_id=oid,
            page=page,
            page_size=page_size,
        )

        if not items:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

        enriched_items = self._display_name_service.enrich_schedules(items)

        return {
            "items": enriched_items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def admin_get_class(self, class_id: Union[str, ObjectId]) -> Optional[dict]:
        return self._class_read_model.get_by_id(class_id)


    def admin_list_schedules_for_teacher_enriched(
        self,
        teacher_id: Union[str, ObjectId],
        page: int = 1,
        page_size: int = 10,
        class_id: Union[str, ObjectId] | None = None,
        day_of_week: int | None = None,
    ) -> Dict[str, Any]:
        oid = self._oid(teacher_id)

        items, total = self._schedule_read_model.list_schedules_for_teacher_paginated(
            teacher_id=oid,
            page=page,
            page_size=page_size,
            class_id=class_id,
            day_of_week=day_of_week,
        )

        if not items:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

        enriched_items = self._display_name_service.enrich_schedules(items)

        return {
            "items": enriched_items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def admin_list_classes_enriched(
        self,
        *,
        q: str = "",
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
        deleted_only: bool = False,
        status: str | None = None,
    ) -> Tuple[List[dict], int]:
        docs, total = self._class_read_model.list_page_numbered(
            q=q,
            status=status,
            include_deleted=include_deleted,
            deleted_only=deleted_only,
            page=page,
            page_size=page_size,
        )
        enriched = self._display_name_service.enrich_classes(docs) if docs else []
        return enriched, total

    def admin_list_teacher_select(self) -> List[dict]:
        active_user_ids = self._iam_read_model.list_active_user_ids_by_role(role="teacher")
        options = self._staff_read_model.list_staff_name_options(
            role="teacher",
            active_user_ids=active_user_ids,
            show_deleted="active",
        )
        return options

    def admin_list_student_select(self, *, show_deleted: ShowDeleted = "active") -> List[dict]:
        docs = self._student_read_model.list_student_name_options(show_deleted=show_deleted)

        items: List[dict] = []
        for d in docs:
            sid = d.get("_id")
            if not sid:
                continue

            first_en = (d.get("first_name_en") or "").strip()
            last_en = (d.get("last_name_en") or "").strip()
            first_kh = (d.get("first_name_kh") or "").strip()
            last_kh = (d.get("last_name_kh") or "").strip()

            full_en = f"{first_en} {last_en}".strip()
            full_kh = f"{last_kh} {first_kh}".strip()

            label = full_en
            if full_kh:
                label = f"{full_en} / {full_kh}".strip(" /")

            items.append({"value": str(sid), "label": label})

        items.sort(key=lambda x: (x["label"] or "").lower())
        return items


    def admin_search_enrollment_student_select(
        self,
        class_id: Union[str, ObjectId],
        *,
        q: str,
        limit: int = 20,
        show_deleted: ShowDeleted = "active",
    ) -> List[dict]:
        """
        Find students eligible to enroll:
        - status must be ACTIVE
        - current_class_id must be missing/None/""
        - optional name/code search when q length >= 2
        """
        q = (q or "").strip()
        limit = max(1, min(int(limit or 20), 50))

        eligible_or = [
            {"current_class_id": {"$exists": False}},
            {"current_class_id": None},
            {"current_class_id": ""},
        ]

        base_filter = {
            "status": StudentStatus.ACTIVE.value,  # "active"
            "$or": eligible_or,
        }

        # No search query -> just return eligible students
        if q == "":
            docs = self._student_read_model.list_student_name_options(
                filter=base_filter,
                projection={"_id": 1},
                limit=limit,
                show_deleted=show_deleted,
            )
            ids = [d["_id"] for d in docs if d.get("_id")]
            return self._display_name_service.student_select_options_for_ids(ids)

        # Too short -> prevent noisy regex scan
        if len(q) < 2:
            return []

        rx = re.compile(re.escape(q), re.IGNORECASE)

        search_or = [
            {"first_name_en": rx},
            {"last_name_en": rx},
            {"first_name_kh": rx},
            {"last_name_kh": rx},
            {"student_id_code": rx},  # FIX: was "code"
            {"phone_number": rx},     # optional, remove if you don't want
        ]

        filter_ = {
            "status": StudentStatus.ACTIVE.value,
            "$and": [
                {"$or": eligible_or},
                {"$or": search_or},
            ],
        }

        docs = self._student_read_model.list_student_name_options(
            filter=filter_,
            projection={"_id": 1},
            limit=limit,
            show_deleted=show_deleted,
        )
        ids = [d["_id"] for d in docs if d.get("_id")]
        return self._display_name_service.student_select_options_for_ids(ids)
    def admin_list_students_in_class_select(
        self,
        class_id: str | ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[dict]:
        """
        List students currently in a class (select options):
        - status must be ACTIVE
        - current_class_id == class_id
        """
        coid = self._oid(class_id)

        filter_ = {
            "status": StudentStatus.ACTIVE.value,
            "current_class_id": coid,
        }

        docs = self._student_read_model.list_student_name_options(
            filter=filter_,
            projection={"_id": 1},
            show_deleted=show_deleted,
        )
        student_ids = [d["_id"] for d in docs if d.get("_id")]
        return self._display_name_service.student_select_options_for_ids(student_ids)

    def admin_list_class_select(self) -> List[dict]:
        return self._class_read_model.list_class_name_options()

    def admin_get_schedule_by_id(self, slot_id: Union[str, ObjectId]) -> Optional[dict]:
        return self._schedule_read_model.get_by_id(slot_id)

    def admin_list_subjects_select_in_class(self, class_id: str | ObjectId) -> List[Dict[str, Any]]:
        coid = self._oid(class_id)

        subject_ids = self._class_read_model.list_subject_ids_for_class(coid) or []
        label_map = self._display_name_service.subject_labels_for_ids(subject_ids)

        seen: set[str] = set()
        result: List[Dict[str, Any]] = []

        for sid in subject_ids:
            if not sid:
                continue

            oid = sid if isinstance(sid, ObjectId) else self._oid(sid)
            sid_str = str(oid)

            if sid_str in seen:
                continue
            seen.add(sid_str)

            label = label_map.get(oid)
            if not label:
                continue

            result.append({"value": sid_str, "label": label})

        return result

    def admin_count_schedules_for_teacher(self, teacher_id: Union[str, ObjectId]) -> int:
        return self._schedule_read_model.count_schedules_for_teacher(teacher_id)

    def admin_count_classes_for_teacher(self, homeroom_teacher_id: Union[str, ObjectId]) -> int:
        return self._class_read_model.count_classes_for_teacher(homeroom_teacher_id)