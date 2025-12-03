from __future__ import annotations

from typing import List, Dict, Union, Any, Final
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.staff.read_model import StaffReadModel

from app.contexts.shared.model_converter import mongo_converter


from app.contexts.shared.services.display_name_service import DisplayNameService

class StudentReadModel(MongoErrorMixin):
    """
    Read-side facade for student use cases.

    Responsibilities:
    - Expose low-level read models for IAM, class, schedule, etc.
    - Provide higher-level queries for "my classes", "my schedule", "my attendance"
      with ObjectIds normalized to strings and names attached for UI.
    """

    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db["students"]

        # underlying read models
        self._iam_read_model: Final[IAMReadModel] = IAMReadModel(self.db)
        self._schedule_read_model: Final[ScheduleReadModel] = ScheduleReadModel(self.db)
        self._class_read_model: Final[ClassReadModel] = ClassReadModel(self.db)
        self._staff_read_model: Final[StaffReadModel] = StaffReadModel(self.db)
        self._attendance_read_model: Final[AttendanceReadModel] = AttendanceReadModel(self.db)
        self._grade_read_model: Final[GradeReadModel] = GradeReadModel(self.db)
        self._subject_read_model: Final[SubjectReadModel] = SubjectReadModel(self.db)
        # shared display-name helper (depends only on read models)
        self._display_name_service: Final[DisplayNameService] = DisplayNameService(
            iam_read_model=self._iam_read_model,
            staff_read_model=self._staff_read_model,
            class_read_model=self._class_read_model,
            subject_read_model=self._subject_read_model,
            student_read_model=self,
        )

    # -------------
    # properties
    # -------------

    @property
    def iam(self) -> IAMReadModel:
        return self._iam_read_model

    @property
    def schedule(self) -> ScheduleReadModel:
        return self._schedule_read_model

    @property
    def classes(self) -> ClassReadModel:
        return self._class_read_model

    @property
    def staff(self) -> StaffReadModel:
        return self._staff_read_model

    @property
    def attendance(self) -> AttendanceReadModel:
        return self._attendance_read_model

    @property
    def grade(self) -> GradeReadModel:
        return self._grade_read_model

    @property
    def subject(self) -> SubjectReadModel:
        return self._subject_read_model

    @property
    def display_name(self) -> DisplayNameService:
        return self._display_name_service

    # -------------
    # basic
    # -------------

    def get_me(self, user_id: ObjectId) -> dict | None:
        """
        Simple pass-through to IAM get_by_id.
        """
        return self.iam.get_by_id(user_id)

    # -------------
    # classes
    # -------------

    def list_my_classes_enriched(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Return the classes where this student is enrolled, with:
        - ids converted to string
        - teacher_name attached

        Shape per item:
        {
          "id": "classId",
          "name": "Grade 7A",
          "teacher_id": "teacherUserId",
          "teacher_name": "Mr. X",
          "student_ids": ["...", "..."],
          "subject_ids": ["...", "..."],
          ...
        }
        """
        oid = mongo_converter.convert_to_object_id(student_id)
        raw_classes = self.classes.list_classes_for_student(oid)  # raw Mongo docs
        return self.display_name.enrich_classes(raw_classes)
      

    def list_my_subjects(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Aggregate all subjects from the classes where this student is enrolled.
        Dedupe by subject_id.

        Return list of subject docs with id as string:

        [
          { "id": "subjectId", "name": "Math", "code": "MATH101", ... },
          ...
        ]
        """
        oid = mongo_converter.convert_to_object_id(student_id)
        class_docs = self.classes.list_classes_for_student(oid)
        if not class_docs:
            return []

        subject_ids: set[ObjectId] = set()
        for c in class_docs:
            for sid in c.get("subject_ids") or []:
                subject_ids.add(mongo_converter.convert_to_object_id(sid))

        if not subject_ids:
            return []

        # you already have SubjectReadModel.list_by_ids
        subject_docs = self.subject.list_by_ids(list(subject_ids))

        result: List[Dict[str, Any]] = []
        for s in subject_docs:
            doc = dict(s)
            sid = doc.pop("_id", None)
            if sid:
                doc["id"] = str(sid)
            result.append(doc)

        return result

    # -------------
    # schedule
    # -------------

    def list_my_schedule(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Build weekly schedule for a student by:

        1) Fetching all classes the student is enrolled in
        2) For each class, fetching its schedule slots
        3) Enriching each slot with:
           - class_name
           - teacher_name
           - teacher_id (string)
        """
        oid = mongo_converter.convert_to_object_id(student_id)
        class_docs = self.classes.list_classes_for_student(oid)
        if not class_docs:
            return []

        # Build class meta: { class_id(ObjectId) -> {"class_name", "teacher_id"} }
        class_ids: List[ObjectId] = []
        teacher_ids: List[ObjectId] = []    
        class_meta_by_id: Dict[ObjectId, Dict[str, Any]] = {}

        for c in class_docs:
            cid: ObjectId = c["_id"]
            class_ids.append(cid)
            tid: ObjectId | None = c.get("teacher_id")

            if tid is not None:
                teacher_ids.append(tid)

            class_meta_by_id[cid] = {
                "class_name": c.get("name", ""),
                "teacher_id": tid,
            }

        # Lookup teacher names
        teacher_name_map = self.staff.list_names_by_user_ids(teacher_ids)
        for cid, meta in class_meta_by_id.items():
            tid = meta.get("teacher_id")
            if tid is not None:
                meta["teacher_name"] = (
                    teacher_name_map.get(tid)
                    or teacher_name_map.get(str(tid), "")
                )
            else:
                meta["teacher_name"] = ""

        # Fetch schedules for all classes
        schedules: List[Dict[str, Any]] = []
        for cid in class_ids:
            class_slots = self.schedule.list_schedules_for_class(cid)
            schedules.extend(class_slots)

        # Enrich + normalize ids
        result: List[Dict[str, Any]] = []
        for s in schedules:
            doc = dict(s)

            sid = doc.pop("_id", None)
            if sid:
                doc["id"] = str(sid)

            cid = doc.get("class_id")
            meta = class_meta_by_id.get(cid)

            # normalize class_id
            if isinstance(cid, ObjectId):
                doc["class_id"] = str(cid)

            if meta:
                doc["class_name"] = meta.get("class_name", "")
                # normalize teacher_id
                tid = meta.get("teacher_id")
                if isinstance(tid, ObjectId):
                    doc["teacher_id"] = str(tid)
                else:
                    doc["teacher_id"] = None
                doc["teacher_name"] = meta.get("teacher_name", "")
            else:
                doc["class_name"] = ""
                doc["teacher_id"] = None
                doc["teacher_name"] = ""

            result.append(doc)

        return result

    # -------------
    # attendance & grades
    # -------------

    def list_my_attendance(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Attendance records for this student, enriched with class_name
        and ids converted to string.

        Shape per item:
        {
          "id": "attendanceId",
          "student_id": "studentId",
          "class_id": "classId",
          "class_name": "Grade 7A",
          "date": "...",
          "status": "present|absent|excused",
          ...
        }
        """
        oid = mongo_converter.convert_to_object_id(student_id)
        records = self.attendance.list_student_attendances(oid)
        if not records:
            return []

        class_ids = {
            rec["class_id"]
            for rec in records
            if rec.get("class_id") is not None
        }

        # {class_id(ObjectId) -> name}
        class_name_map = self.classes.list_class_names_by_ids(list(class_ids))

        result: List[Dict[str, Any]] = []
        for rec in records:
            doc = dict(rec)

            rid = doc.pop("_id", None)
            if rid:
                doc["id"] = str(rid)

            cid = doc.get("class_id")
            if isinstance(cid, ObjectId):
                doc["class_id"] = str(cid)
                doc["class_name"] = class_name_map.get(cid, "")
            else:
                doc["class_name"] = ""

            if isinstance(doc.get("student_id"), ObjectId):
                doc["student_id"] = str(doc["student_id"])

            result.append(doc)

        return result

    def list_my_grades(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Optional helper: list all grades for this student, across classes.
        You can enrich later with subject_name / class_name if needed.
        """
        oid = mongo_converter.convert_to_object_id(student_id)
        records = self.grade.list_grades_for_student(oid)  
        if not records:
            return []
        