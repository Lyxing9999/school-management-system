from typing import List, Tuple
from bson import ObjectId
from pymongo.database import Database
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel


class StudentReadModel(MongoErrorMixin):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db["students"]
        self._iam_read_model: IAMReadModel | None = None
        self._schedule_read_model: ScheduleReadModel | None = None
        self._class_read_model: ClassReadModel | None = None

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


    def get_me(self, user_id: ObjectId) -> dict | None:
        return self.iam.get_by_id(user_id)

    def list_my_classes(self, student_id: ObjectId) -> List[dict]:
        return self.classes.list_student_classes(student_id)

    def list_my_schedule(self, student_id: ObjectId) -> List[dict]:
        return self.schedule.list_student_schedules(student_id)

