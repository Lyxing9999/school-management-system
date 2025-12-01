from typing import List, Dict, Union, Any, Final
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.staff.read_model import StaffReadModel

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.services.display_name_service import DisplayNameService


class TeacherReadModel(MongoErrorMixin):
    """
    Read-side facade for teacher use cases.

    - Exposes lower-level read models via properties
    - Adds helper methods for "teacher views" (classes, schedules, attendance, etc.)
    - Returns UI-friendly dicts (ObjectId -> str, includes display names where useful)
    """

    def __init__(self, db: Database) -> None:
        # base read models
        self._iam: Final = IAMReadModel(db)
        self._schedule: Final = ScheduleReadModel(db)
        self._classes: Final = ClassReadModel(db)
        self._attendance: Final = AttendanceReadModel(db)
        self._grade: Final = GradeReadModel(db)
        self._student: Final = StudentReadModel(db)
        self._subject: Final = SubjectReadModel(db)
        self._staff: Final = StaffReadModel(db)

        # shared display-name helper (depends only on read models)
        self._display_name_service: Final[DisplayNameService] = DisplayNameService(
            iam_read_model=self._iam,
            staff_read_model=self._staff,
            class_read_model=self._classes,
            subject_read_model=self._subject,
            student_read_model=self._student,
        )

    # ----------------- properties (low-level accessors) -----------------

    @property
    def iam(self) -> IAMReadModel:
        return self._iam

    @property
    def schedule(self) -> ScheduleReadModel:
        return self._schedule

    @property
    def classes(self) -> ClassReadModel:
        return self._classes

    @property
    def attendance(self) -> AttendanceReadModel:
        return self._attendance

    @property
    def grade(self) -> GradeReadModel:
        return self._grade

    @property
    def student(self) -> StudentReadModel:
        return self._student

    @property
    def subject(self) -> SubjectReadModel:
        return self._subject

    @property
    def staff(self) -> StaffReadModel:
        return self._staff

    @property
    def display_names(self) -> DisplayNameService:
        return self._display_name_service

    # ----------------- simple helpers -----------------

    def get_me(self, user_id: ObjectId) -> dict | None:
        return self.iam.get_by_id(user_id)

    # ----------------- classes -----------------

    def list_my_classes(self, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """
        Classes for this teacher, with:
        - ids converted to str
        - teacher_name attached

        Returned shape per item:
        {
          "id": "....",
          "name": "Grade 7A",
          "teacher_id": "....",
          "teacher_name": "Mr X",
          "student_ids": ["...", "..."],
          "subject_ids": ["...", "..."],
          ...
        }
        """
        oid = mongo_converter.convert_to_object_id(teacher_id)
        raw_classes = self.classes.list_teacher_classes(oid)

        # returns { user_id(ObjectId) -> staff_name }
        name_map = self.staff.list_names_by_user_ids([oid])
        teacher_name = name_map.get(oid) or name_map.get(str(oid), "")

        result: List[Dict[str, Any]] = []
        for c in raw_classes:
            # make a shallow copy so we can safely mutate
            doc = dict(c)

            # normalize ids to strings for DTO/frontend
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]

            if "teacher_id" in doc and doc["teacher_id"] is not None:
                doc["teacher_id"] = str(doc["teacher_id"])

            if "student_ids" in doc and isinstance(doc["student_ids"], list):
                doc["student_ids"] = [str(sid) for sid in doc["student_ids"]]

            if "subject_ids" in doc and isinstance(doc["subject_ids"], list):
                doc["subject_ids"] = [str(sid) for sid in doc["subject_ids"]]

            # attach display name
            doc["teacher_name"] = teacher_name

            result.append(doc)

        return result

    def list_student_ids_in_class(self, class_id: Union[str, ObjectId]) -> List[ObjectId]:
        return self.classes.list_student_ids_in_class(class_id)

    def list_subject_ids_in_class(self, class_id: Union[str, ObjectId]) -> List[ObjectId]:
        return self.classes.list_subject_ids_in_class(class_id)

    # ----------------- select options (for dropdowns) -----------------

    def list_student_name_options_in_class(
        self,
        class_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        """
        Return student options for a given class, shaped for UI select:

        [
          { "id": "ObjectIdString", "username": "student1" },
          { "id": "ObjectIdString", "username": "student2" },
          ...
        ]

        NOTE: Currently uses IAM.username. Later you can switch to
        student full_name via DisplayNameService if you want.
        """
        student_ids = self.list_student_ids_in_class(class_id)
        if not student_ids:
            return []

        # list_usernames_by_ids -> [{_id, username}, ...]
        docs = self.iam.list_usernames_by_ids(user_ids=student_ids, role="student")
        options: List[Dict[str, Any]] = []
        for d in docs:
            sid = d.get("_id")
            if not sid:
                continue
            options.append(
                {
                    "id": str(sid),
                    "username": d.get("username", ""),
                }
            )
        return options

    def list_subject_name_options_in_class(
        self,
        class_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        """
        Return subject options for a class, shaped for UI select:

        [
          { "id": "ObjectIdString", "name": "Math (MTH101)" },
          ...
        ]

        Uses SubjectReadModel.list_names_by_ids which returns {ObjectId: name}
        (or you can route this through DisplayNameService.subject_names_for_ids).
        """
        subject_ids = self.list_subject_ids_in_class(class_id)
        if not subject_ids:
            return []

        # subject_names_for_ids => { ObjectId: "Math (MTH101)", ... }
        name_map = self.display_names.subject_names_for_ids(subject_ids)

        options: List[Dict[str, Any]] = []
        for sid, label in name_map.items():
            options.append(
                {
                    "id": str(sid),
                    "name": label,
                }
            )
        return options

    def list_class_name_options_for_teacher(
        self,
        teacher_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        """
        Return class options for a teacher, shaped for UI select:

        [
          { "id": "ObjectIdString", "name": "Grade 7A" },
          ...
        ]
        """
        oid = mongo_converter.convert_to_object_id(teacher_id)
        docs = self.classes.list_teacher_classes(oid)
        options: List[Dict[str, Any]] = []
        for c in docs:
            cid = c.get("_id")
            if not cid:
                continue
            options.append(
                {
                    "id": str(cid),
                    "name": c.get("name", ""),
                }
            )
        return options

    # ----------------- schedule -----------------

    def list_my_schedule(self, teacher_id: Union[str, ObjectId]) -> List[dict]:
        """
        For now: raw schedule docs for this teacher.

        Later you can enrich with:
        - class_name via display_names.class_names_for_ids
        - maybe subject_name if you add subject_id to schedule
        """
        oid = mongo_converter.convert_to_object_id(teacher_id)
        return self.schedule.list_teacher_schedules(oid)

    # ----------------- grades & attendance -----------------

    def list_class_grades(self, class_id: Union[str, ObjectId]) -> List[dict]:
        """
        Currently returns raw grade docs for a class.

        You can later use DisplayNameService to attach student_name, subject_name:
        - display_names.username_for_id(...)
        - display_names.subject_name_for_id(...)
        """
        return self.grade.list_class_grades(class_id)

    def list_class_attendance_for_teacher(
        self,
        class_id: Union[str, ObjectId],
    ) -> List[dict]:
        """
        Attendance records for a class, with student_name attached.

        Returned shape per item:
        {
          "id": "...",
          "student_id": "ObjectIdString",
          "student_name": "student1",
          "class_id": "ObjectIdString",
          "date": "...",
          "status": "...",
          ...
        }
        """
        attendances = self.attendance.list_class_attendance(class_id)
        if not attendances:
            return []

        # collect student_ids
        student_ids = list({rec["student_id"] for rec in attendances if rec.get("student_id")})
        if not student_ids:
            return attendances

        # map {ObjectId -> username}
        user_docs = self.iam.list_usernames_by_ids(student_ids, role="student")
        username_by_id = {
            doc["_id"]: doc.get("username", "")
            for doc in user_docs
            if doc.get("_id") is not None
        }

        result: List[dict] = []
        for rec in attendances:
            r = dict(rec)

            # normalize ids to strings for UI
            if "_id" in r:
                r["id"] = str(r["_id"])
                del r["_id"]

            sid = r.get("student_id")
            if isinstance(sid, ObjectId):
                r["student_id"] = str(sid)

            cid = r.get("class_id")
            if isinstance(cid, ObjectId):
                r["class_id"] = str(cid)

            # attach display name
            r["student_name"] = username_by_id.get(rec.get("student_id"), "")

            result.append(r)

        return result