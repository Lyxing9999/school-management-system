from typing import List, Dict, Union, Any, Final, Tuple
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
from app.contexts.staff.read_models.staff_read_model import StaffReadModel

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

    def list_student_ids_for_teacher(
        self,
        teacher_id: Union[str, ObjectId],
    ) -> List[ObjectId]:
        """
        Return the list of student_ids (ObjectId) enrolled in the given class.
        - teacher_id: ObjectId
        - return: Student Object ID Current Teacher Teach List[ObjectId]
        """
        t_oid = mongo_converter.convert_to_object_id(teacher_id)

        class_docs = self.classes.list_classes_for_teacher(t_oid)
        class_ids = [c["_id"] for c in class_docs if c.get("_id")]
        if not class_ids:
            return []

        return self.student.list_student_ids_by_current_class_ids(class_ids)

    def list_my_classes_enriched(self, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
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
        raw_classes = self.classes.list_classes_for_teacher(oid)
        if not raw_classes:
            return []
        enriched_classes = self.display_names.enrich_classes(raw_classes)
        return enriched_classes






    def list_subject_ids_for_class(self, class_id: Union[str, ObjectId]) -> List[ObjectId]:
        return self.classes.list_subject_ids_for_class(class_id)

    # ----------------- select options (for dropdowns) -----------------


    def list_my_students_in_class(self, class_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        student = self.student.list_students_by_current_class_id(class_id)
        return student


    def list_student_name_options_in_class(
        self,
        class_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
    
        students = self.student.list_students_by_current_class_ids([class_id])
        if not students:
            return []
        student_ids = [s["_id"] for s in students if s.get("_id")]
        return self.display_names.student_select_options_for_ids(student_ids)




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
        subject_ids = self.list_subject_ids_for_class(class_id)
        if not subject_ids:
            return []

        # subject_names_for_ids => { ObjectId: "Math (MTH101)", ... }
        name_map = self.display_names.subject_labels_for_ids(subject_ids)

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
        return self.classes.list_class_name_options_for_teacher(teacher_id)

    # ----------------- schedule -----------------

    def list_schedule_for_teacher_enriched(self, teacher_id: Union[str, ObjectId]) -> List[dict]:
        """
        For now: raw schedule docs for this teacher.

        Later you can enrich with:
        - class_name via display_names.class_names_for_ids
        - maybe subject_name if you add subject_id to schedule
        """
        oid = mongo_converter.convert_to_object_id(teacher_id)
        schedules = self.schedule.list_schedules_for_teacher(oid)
        if not schedules:
            return []
        return self.display_names.enrich_schedules(schedules)

    # ----------------- grades & attendance -----------------

    def list_grades_for_class_enriched(self, class_id: Union[str, ObjectId]) -> List[dict]:
        """
        Currently returns raw grade docs for a class.

        You can later use DisplayNameService to attach student_name, subject_name:
        - display_names.username_for_id(...)
        - display_names.subject_name_for_id(...)
        """
        grades = self.grade.list_grades_for_class(class_id)
        if not grades:
            return []
        return self.display_names.enrich_grades(grades)









    def list_attendance_for_class_enriched(
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
        attendances = self.attendance.list_attendance_for_class(class_id)
        if not attendances:
            return []
        return self.display_names.enrich_attendance(attendances)

    def list_teacher_classes_with_summary(self, teacher_id: Union[str, ObjectId]) -> Tuple[List[Dict], Dict]:
        docs, summary = self.classes.list_classes_for_teacher_with_summary(teacher_id)
        enriched = self.display_names.enrich_classes(docs)
        return enriched, summary