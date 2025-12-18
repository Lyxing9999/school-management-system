from __future__ import annotations

from typing import Final, List, Dict, Any, Union, Optional
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin

from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.staff.read_model import StaffReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.services.display_name_service import DisplayNameService


class StudentStatsReadModel(MongoErrorMixin):\

    def __init__(self, db: Database):
        self.db = db

        # base read models
        self._student_read: Final[StudentReadModel] = StudentReadModel(db)
        self._class_read: Final[ClassReadModel] = ClassReadModel(db)
        self._schedule_read: Final[ScheduleReadModel] = ScheduleReadModel(db)
        self._attendance_read: Final[AttendanceReadModel] = AttendanceReadModel(db)
        self._grade_read: Final[GradeReadModel] = GradeReadModel(db)
        self._subject_read: Final[SubjectReadModel] = SubjectReadModel(db)
        self._iam_read: Final[IAMReadModel] = IAMReadModel(db)
        self._staff_read: Final[StaffReadModel] = StaffReadModel(db)

        # shared enrichment
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
        return mongo_converter.convert_to_object_id(v)

    def _get_current_class_id(self, student_id: Union[str, ObjectId]) -> Optional[ObjectId]:
        sid = self._oid(student_id)
        if not sid:
            return None
        stu_doc = self._student_read.get_by_id(sid)  
        if not stu_doc:
            return None
        return stu_doc.get("current_class_id")

    # ---------------- CLASSES ----------------

    def list_my_classes_enriched(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        class_id = self._get_current_class_id(student_id)
        if not class_id:
            return []

        class_doc = self._class_read.get_by_id(class_id)
        if not class_doc:
            return []

        # enrich_classes expects Iterable[dict]
        return self._display.enrich_classes([class_doc])

    # ---------------- SUBJECTS ----------------

    def list_my_subjects(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        class_id = self._get_current_class_id(student_id)
        if not class_id:
            return []

        class_doc = self._class_read.get_by_id(class_id)
        if not class_doc:
            return []

        subject_ids = class_doc.get("subject_ids") or []
        if not subject_ids:
            return []

        # normalize ids
        soids: List[ObjectId] = []
        for raw in subject_ids:
            oid = self._oid(raw)
            if oid:
                soids.append(oid)

        if not soids:
            return []

        subject_docs = self._subject_read.list_by_ids(soids)
        result: List[Dict[str, Any]] = []

        for s in subject_docs:
            doc = dict(s)
            sid = doc.pop("_id", None)
            if sid:
                doc["id"] = str(sid)

            name = (doc.get("name") or "").strip()
            code = (doc.get("code") or "").strip()
            if name and code:
                doc["label"] = f"{name} ({code})"
            else:
                doc["label"] = name or code

            result.append(doc)

        result.sort(key=lambda d: (d.get("label") or "").lower())
        return result

    # ---------------- SCHEDULE ----------------

    def list_my_schedule_enriched(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        class_id = self._get_current_class_id(student_id)
        if not class_id:
            return []

        schedule_docs = self._schedule_read.list_schedules_for_classes([class_id])
        if not schedule_docs:
            return []

        enriched = self._display.enrich_schedules(schedule_docs)
        enriched.sort(key=lambda s: (s.get("day_of_week", 0), s.get("start_time", "")))
        return enriched

    # ---------------- ATTENDANCE ----------------

    def list_my_attendance_enriched(
        self,
        student_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId, None] = None,
    ) -> List[Dict[str, Any]]:
        sid = self._oid(student_id)
        if not sid:
            return []

        cid = self._oid(class_id) if class_id else self._get_current_class_id(sid)
        if not cid:
            return []

        records = self._attendance_read.list_attendance_for_class_and_student(
            class_id=cid,
            student_id=sid,
        )
        if not records:
            return []

        return self._display.enrich_attendance(records)

    # ---------------- GRADES ----------------

    def list_my_grades_enriched(
        self,
        student_id: Union[str, ObjectId],
        term: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        sid = self._oid(student_id)
        if not sid:
            return []

        records = self._grade_read.list_grades_for_student(sid, term=term) if term else self._grade_read.list_grades_for_student(sid)
        if not records:
            return []

        return self._display.enrich_grades(records)