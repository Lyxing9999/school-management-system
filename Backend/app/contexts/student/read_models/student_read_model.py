from __future__ import annotations

from typing import List, Dict, Union, Any, Final, Iterable
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
    # basic
    # -------------
    def get_by_user_id(self, user_id: ObjectId):
            return self.collection.find_one({"user_id": user_id})
            
    def get_me(self, user_id: ObjectId) -> dict | None:
        """
        Simple pass-through to IAM get_by_id.
        """
        return self.get_by_user_id(user_id)

    def get_by_student_code(self, code: str):
            return self.collection.find_one({"student_id_code": code})

    def get_student_names_by_ids(self, student_ids: list) -> dict:
            ids = [mongo_converter.convert_to_object_id(sid) for sid in student_ids if sid]
            cursor = self.collection.find(
                {"_id": {"$in": ids}},
                {"first_name_en": 1, "last_name_en": 1}
            )
            names = {}
            for doc in cursor:
                full_name = f"{doc.get('first_name_en')} {doc.get('last_name_en')}"
                names[doc["_id"]] = full_name
            return names

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
        raw_classes = self._class_read_model.list_classes_for_student(oid)  # raw Mongo docs
        return self._display_name_service.enrich_classes(raw_classes)
      

    def list_my_subjects(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Aggregate all subjects from the classes where this student is enrolled.
        Dedupe by subject_id.

        Return list of subject docs with:
        - id: str
        - label: "Name (CODE)" for selects
        """
        oid = mongo_converter.convert_to_object_id(student_id)
        class_docs = self._class_read_model.list_classes_for_student(oid)
        if not class_docs:
            return []

        subject_ids: set[ObjectId] = set()
        for c in class_docs:
            for sid in c.get("subject_ids") or []:
                subject_ids.add(mongo_converter.convert_to_object_id(sid))

        if not subject_ids:
            return []

        subject_docs = self.subject.list_by_ids(list(subject_ids))

        result: List[Dict[str, Any]] = []
        for s in subject_docs:
            doc = dict(s)
            sid = doc.pop("_id", None)
            if sid:
                doc["id"] = str(sid)

            # build label once here
            name = doc.get("name") or ""
            code = doc.get("code") or ""
            if name and code:
                doc["label"] = f"{name} ({code})"
            else:
                doc["label"] = name or code

            result.append(doc)

        # optional: sort alphabetically by label (nice for UI)
        result.sort(key=lambda d: d.get("label") or d.get("name") or "")
        return result

    # -------------
    # schedule
    # -------------



    def list_my_schedule_enriched(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Build weekly schedule for a student by:

        1) Fetching all classes the student is enrolled in
        2) For those classes, fetching their schedule slots
        3) Enriching each slot with:
           - class_name
           - teacher_name
           - subject_label (if available in schedule docs)
        """

        oid = mongo_converter.convert_to_object_id(student_id)

        class_docs = self._class_read_model.list_classes_for_student(oid)
        if not class_docs:
            return []
        class_ids: List[ObjectId] = []
        for c in class_docs:
            if "_id" in c:
                class_ids.append(c["_id"])
            elif "id" in c:
                class_ids.append(mongo_converter.convert_to_object_id(c["id"]))

        if not class_ids:
            return []
        schedule_docs = self._schedule_read_model.list_schedules_for_classes(class_ids)

        schedule_enriched = self._display_name_service.enrich_schedules(schedule_docs)

        schedule_enriched.sort(
            key=lambda s: (
                s.get("day_of_week", 0),
                s.get("start_time", ""),
            )
        )

        return schedule_enriched
    # -------------
    # attendance & grades
    # -------------

    def list_my_attendance_enriched(self, student_id: Union[str, ObjectId], class_ids: List[Union[str, ObjectId]]) -> List[Dict[str, Any]]:
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
        records = self._attendance_read_model.list_attendance_for_class_and_student(class_id=class_ids, student_id=student_id)
        if not records:
            return []
        return self._display_name_service.enrich_attendance(records)


    def list_my_grades_enriched(self, student_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Optional helper: list all grades for this student, across classes.
        You can enrich later with subject_name / class_name if needed.
        """
        oid = mongo_converter.convert_to_object_id(student_id)
        records = self._grade_read_model.list_grades_for_student(oid)  
        if not records:
            return []
        return self._display_name_service.enrich_grades(records)

        


    def count_active_students(self) -> int:
        """
        Return the count of active students.
        """
        return self._iam.count_active_users("student")