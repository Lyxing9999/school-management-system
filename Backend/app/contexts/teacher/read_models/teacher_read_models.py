from typing import List
from bson import ObjectId
from pymongo.database import Database
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel

from app.contexts.student.read_models.student_read_model import StudentReadModel


class TeacherReadModel(MongoErrorMixin):
    def __init__(self, db: Database):
        self.db = db

        self._iam_read_model: IAMReadModel | None = None
        self._schedule_read_model: ScheduleReadModel | None = None
        self._class_read_model: ClassReadModel | None = None
        self._attendance_read_model: AttendanceReadModel | None = None
        self._grade_read_model: GradeReadModel | None = None
        self._student_read_model: StudentReadModel | None = None
    @property
    def iam(self) -> IAMReadModel:
        if self._iam_read_model is None:
            self._iam_read_model = IAMReadModel(self.db)
        return self._iam_read_model

    @property
    def schedule(self) -> ScheduleReadModel:
        if self._schedule_read_model is None:
            self._schedule_read_model = ScheduleReadModel(self.db)
        return self._schedule_read_model


    @property
    def classes(self) -> ClassReadModel:
        if self._class_read_model is None:
            self._class_read_model = ClassReadModel(self.db)
        return self._class_read_model

    @property
    def attendance(self) -> AttendanceReadModel:
        if self._attendance_read_model is None:
            self._attendance_read_model = AttendanceReadModel(self.db)
        return self._attendance_read_model

    @property
    def grade(self) -> GradeReadModel:
        if self._grade_read_model is None:
            self._grade_read_model = GradeReadModel(self.db)
        return self._grade_read_model

    @property
    def student(self) -> StudentReadModel:
        if self._student_read_model is None:
            self._student_read_model = StudentReadModel(self.db)
        return self._student_read_model







    def get_me(self, user_id: ObjectId) -> dict | None:
        return self.iam.get_by_id(user_id)



    def list_my_students_in_class(self, class_id: ObjectId) -> List[dict]:
        return self.classes.list_student_classes(class_id)

    def list_my_classes(self, teacher_id: str | ObjectId) -> List[dict]:
        return self.classes.list_teacher_classes(teacher_id)

    def list_my_schedule(self, teacher_id: ObjectId) -> List[dict]:
        return self.schedule.list_teacher_schedules(teacher_id)

    def list_class_attendance(self, class_id: ObjectId) -> List[dict]:
        return self.attendance.list_class_attendance(class_id)

    def list_class_grades(self, class_id: ObjectId) -> List[dict]:
        return self.grade.list_class_grades(class_id)
