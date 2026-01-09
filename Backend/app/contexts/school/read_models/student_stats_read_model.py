from typing import Any, Final, Dict, List, Optional, Union
from datetime import datetime
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.school.domain.class_section import ClassSectionStatus
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.shared.lifecycle.filters import ShowDeleted
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.services.display_name_service import DisplayNameService
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.student.domain.student import StudentStatus
from app.contexts.student.read_models.student_read_model import StudentReadModel


class StudentStatsReadModel(MongoErrorMixin):
    """
    Student-facing stats/data read model.

    Policy:
    - only ACTIVE students are allowed to see data here
    - only ACTIVE classes are considered valid current class
    - lifecycle filtering stays at underlying read models (show_deleted defaults active)
    """

    def __init__(self, db: Database):
        self.db = db

        self._student_read: Final[StudentReadModel] = StudentReadModel(db)
        self._class_read: Final[ClassReadModel] = ClassReadModel(db)
        self._schedule_read: Final[ScheduleReadModel] = ScheduleReadModel(db)
        self._attendance_read: Final[AttendanceReadModel] = AttendanceReadModel(db)
        self._grade_read: Final[GradeReadModel] = GradeReadModel(db)
        self._subject_read: Final[SubjectReadModel] = SubjectReadModel(db)
        self._iam_read: Final[IAMReadModel] = IAMReadModel(db)
        self._staff_read: Final[StaffReadModel] = StaffReadModel(db)

        self._display: Final[DisplayNameService] = DisplayNameService(
            iam_read_model=self._iam_read,
            staff_read_model=self._staff_read,
            class_read_model=self._class_read,
            subject_read_model=self._subject_read,
            student_read_model=self._student_read,
        )

    def _oid(self, v: Union[str, ObjectId, None]) -> Optional[ObjectId]:
        if v is None:
            return None
        try:
            return mongo_converter.convert_to_object_id(v)
        except Exception:
            return None

    def _get_active_student_doc(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        sid = self._oid(student_id)
        if not sid:
            return None

        doc = self._student_read.get_by_id(sid, show_deleted=show_deleted)
        if not doc:
            return None

        # IMPORTANT: enforce StudentStatus
        if doc.get("status") != StudentStatus.ACTIVE.value:
            return None

        return doc

    def _get_active_current_class_doc(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        stu_doc = self._get_active_student_doc(student_id, show_deleted=show_deleted)
        if not stu_doc:
            return None

        cid = self._oid(stu_doc.get("current_class_id"))
        if not cid:
            return None

        class_doc = self._class_read.get_by_id(cid, show_deleted=show_deleted)
        if not class_doc:
            return None

        # IMPORTANT: enforce ClassSectionStatus
        if class_doc.get("status") != ClassSectionStatus.ACTIVE.value:
            return None

        return class_doc
    def _enrich_attendance_with_schedule_and_subject(
        self,
        items: List[Dict[str, Any]],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        if not items:
            return []

        # collect ids
        slot_ids: List[ObjectId] = []
        subject_ids: List[ObjectId] = []

        for it in items:
            sid = self._oid(it.get("schedule_slot_id"))
            if sid:
                slot_ids.append(sid)

            subid = self._oid(it.get("subject_id"))
            if subid:
                subject_ids.append(subid)

        # fetch schedules by ids
        schedules_by_id: Dict[str, Dict[str, Any]] = {}
        if slot_ids:
            schedule_docs = self._schedule_read.list_by_ids(slot_ids, show_deleted=show_deleted)
            for s in schedule_docs:
                _id = s.get("_id")
                if _id is not None:
                    schedules_by_id[str(_id)] = s

        # fetch subjects by ids
        subjects_by_id: Dict[str, Dict[str, Any]] = {}
        if subject_ids:
            subject_docs = self._subject_read.list_by_ids(subject_ids, show_deleted=show_deleted)
            for sub in subject_docs:
                _id = sub.get("_id")
                if _id is not None:
                    subjects_by_id[str(_id)] = sub

        # attach schedule + subject fields
        for it in items:
            slot_key = str(it.get("schedule_slot_id")) if it.get("schedule_slot_id") is not None else None
            sub_key = str(it.get("subject_id")) if it.get("subject_id") is not None else None

            # schedule
            if slot_key and slot_key in schedules_by_id:
                s = schedules_by_id[slot_key]
                it["day_of_week"] = s.get("day_of_week")
                it["start_time"] = s.get("start_time")
                it["end_time"] = s.get("end_time")
                it["room"] = s.get("room")

                # if attendance subject_id missing, fallback from schedule.subject_id
                if not it.get("subject_id") and s.get("subject_id") is not None:
                    it["subject_id"] = str(s.get("subject_id"))

            # subject
            if sub_key and sub_key in subjects_by_id:
                sub = subjects_by_id[sub_key]
                name = (sub.get("name") or "").strip()
                code = (sub.get("code") or "").strip()
                it["subject_label"] = f"{name} ({code})" if (name and code) else (name or code)

        return items
    # -------------------------
    # Public methods
    # -------------------------

    def list_my_classes_enriched(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        class_doc = self._get_active_current_class_doc(student_id, show_deleted=show_deleted)
        if not class_doc:
            return []
        return self._display.enrich_classes([class_doc])

    def list_my_subjects(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        class_doc = self._get_active_current_class_doc(student_id, show_deleted=show_deleted)
        if not class_doc:
            return []

        subject_ids = class_doc.get("subject_ids") or []
        if not isinstance(subject_ids, list) or not subject_ids:
            return []

        soids: List[ObjectId] = []
        for raw in subject_ids:
            oid = self._oid(raw)
            if oid:
                soids.append(oid)

        if not soids:
            return []

        subject_docs = self._subject_read.list_by_ids(soids, show_deleted=show_deleted)  # ensure your SubjectReadModel supports this
        result: List[Dict[str, Any]] = []

        for s in subject_docs:
            doc = dict(s)
            sid = doc.pop("_id", None)
            if sid is not None:
                doc["id"] = str(sid)

            name = (doc.get("name") or "").strip()
            code = (doc.get("code") or "").strip()
            doc["label"] = f"{name} ({code})" if (name and code) else (name or code)

            result.append(doc)

        result.sort(key=lambda d: (d.get("label") or "").lower())
        return result

    def list_my_schedule_enriched(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        class_doc = self._get_active_current_class_doc(student_id, show_deleted=show_deleted)
        if not class_doc:
            return []

        class_id = class_doc["_id"]
        schedule_docs = self._schedule_read.list_schedules_for_classes([class_id], show_deleted=show_deleted) 
        if not schedule_docs:
            return []

        enriched = self._display.enrich_schedules(schedule_docs)
        enriched.sort(key=lambda s: (int(s.get("day_of_week") or 0), str(s.get("start_time") or "")))
        return enriched

    def list_my_attendance_enriched(
        self,
        student_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId, None] = None,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        stu_doc = self._get_active_student_doc(student_id, show_deleted=show_deleted)
        if not stu_doc:
            return []

        sid = stu_doc["_id"]

        # If caller provides class_id, use it; else use current class
        cid = self._oid(class_id) if class_id is not None else self._oid(stu_doc.get("current_class_id"))
        if not cid:
            return []

        # Optional hardening: only allow current class
        # if cid != self._oid(stu_doc.get("current_class_id")):
        #     return []

        records = self._attendance_read.list_attendance_for_class_and_student(
            class_id=cid,
            student_id=sid,
            show_deleted=show_deleted,
        )
        if not records:
            return []

        enriched = self._display.enrich_attendance(records)


        enriched = self._enrich_attendance_with_schedule_and_subject(enriched, show_deleted=show_deleted)

        return enriched
    def list_my_grades_enriched(
        self,
        student_id: Union[str, ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
        page: int = 1,
        page_size: int = 10,
        term: Optional[str] = None,
        grade_type: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        class_id: Optional[Union[str, ObjectId]] = None,
        subject_id: Optional[Union[str, ObjectId]] = None,
        sort: str = "-created_at",
    ) -> Dict[str, Any]:
        stu_doc = self._get_active_student_doc(student_id, show_deleted=show_deleted)
        if not stu_doc:
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "pages": 1}

        sid = stu_doc["_id"]

        records = self._grade_read.list_grades_for_student_paged(
            sid,
            page=page,
            page_size=page_size,
            term=term,
            grade_type=grade_type,
            q=q,
            date_from=date_from,
            date_to=date_to,
            class_id=class_id,
            subject_id=subject_id,
            show_deleted=show_deleted,
            sort=sort,
        )

        items = records.get("items") or []
        records["items"] = self._display.enrich_grades(items)
        return records