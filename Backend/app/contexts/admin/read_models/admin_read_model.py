from typing import List, Tuple, Union, Optional, Final
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin

from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_model import StaffReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.services.display_name_service import DisplayNameService


class AdminReadModel(MongoErrorMixin):
    """
    High-level read-model facade for admin screens.

    It aggregates lower-level read models and exposes helper
    views that are *already decorated* with display names.
    """

    def __init__(self, db: Database):
        self.db = db

        # base read models
        self._iam_read_model: Final[IAMReadModel] = IAMReadModel(self.db)
        self._staff_read_model: Final[StaffReadModel] = StaffReadModel(self.db)
        self._schedule_read_model: Final[ScheduleReadModel] = ScheduleReadModel(self.db)
        self._subject_read_model: Final[SubjectReadModel] = SubjectReadModel(self.db)
        self._class_read_model: Final[ClassReadModel] = ClassReadModel(self.db)
        self._student_read_model: Final[StudentReadModel] = StudentReadModel(self.db)

        # shared display-name helper (depends only on read models)
        self._display_name_service: Final[DisplayNameService] = DisplayNameService(
            iam_read_model=self._iam_read_model,
            staff_read_model=self._staff_read_model,
            class_read_model=self._class_read_model,
            subject_read_model=self._subject_read_model,
            student_read_model=self._student_read_model,
        )

    # ------------- properties -------------
    @property
    def iam_read_model(self) -> IAMReadModel:
        return self._iam_read_model

    @property
    def staff_read_model(self) -> StaffReadModel:
        return self._staff_read_model

    @property
    def schedule_read_model(self) -> ScheduleReadModel:
        return self._schedule_read_model

    @property
    def subject_read_model(self) -> SubjectReadModel:
        return self._subject_read_model

    @property
    def class_read_model(self) -> ClassReadModel:
        return self._class_read_model

    @property
    def student_read_model(self) -> StudentReadModel:
        return self._student_read_model

    @property
    def display_names(self) -> DisplayNameService:
        return self._display_name_service

    # ------------- simple delegates -------------

    def get_staff_by_user_id(self, user_id: ObjectId) -> Optional[dict]:
        return self.staff_read_model.get_by_user_id(user_id)

    def get_user_by_id(self, user_id: ObjectId) -> Optional[dict]:
        return self.iam_read_model.get_by_id(user_id)

    def get_page_by_role(
        self,
        roles: Union[str, List[str]],
        page: int = 1,
        page_size: int = 5,
    ) -> Tuple[List[dict], int]:
        """
        Reuse IAMReadModel pagination (already decorates created_by_name).
        """
        return self.iam_read_model.get_page_by_role(roles, page, page_size)

    # ------------- schedules with names -------------

    def admin_list_schedules_for_class_enriched(self, class_id: Union[str, ObjectId]) -> List[dict]:

        oid = mongo_converter.convert_to_object_id(class_id)
        class_schedules = self.schedule_read_model.list_schedules_for_class(oid)
        if not class_schedules:
            return []
        enriched = self.display_names.enrich_schedules(class_schedules)
        return enriched

    def admin_list_schedules_for_teacher_enriched(self, teacher_id: Union[str, ObjectId]) -> List[dict]:

        oid = mongo_converter.convert_to_object_id(teacher_id)
        teacher_schedules = self.schedule_read_model.list_schedules_for_teacher(oid)
        if not teacher_schedules:
            return []
        enriched = self.display_names.enrich_schedules(teacher_schedules)
        return enriched

    def admin_list_classes_enriched(self) -> List[dict]:
        classes = self.class_read_model.list_all()
        if not classes:
            return []
        enriched = self.display_names.enrich_classes(classes)
        return enriched


    # ------------- dropdowns / selects -------------

    def admin_list_teacher_select(self) -> List[dict]:
        """
        For teacher dropdowns: returns raw staff docs with {user_id, staff_name, ...}
        Frontend RemoteSelect will map to label/value.
        """
        return self.staff_read_model.list_staff_name_options(role="teacher")

    def admin_list_student_select(self) -> List[dict]:
        """
        For student dropdowns: returns [{_id, username}, ...] for students.
        """
        return self.iam_read_model.list_usernames_by_role(role="student")

    def admin_list_class_select(self) -> List[dict]:
        """
        For class dropdowns: returns [{_id, name}, ...] for classes.
        """
        return self.class_read_model.list_class_names()

    def admin_get_schedule_by_id(self, slot_id: Union[str, ObjectId]) -> Optional[dict]:
        """
        For schedule dropdowns: returns raw schedule docs with {_id, name, ...}
        Frontend RemoteSelect will map to label/value.
        """
        return self.schedule_read_model.get_by_id(slot_id)




    # ------------- helpers -------------
    """
    check relationship before delete
    """
    def admin_count_schedules_for_teacher(self, teacher_id: Union[str, ObjectId]) -> int:
        """
        if teacher has schedules, return number of schedules
        else return 0
        """
        return self.schedule_read_model.count_schedules_for_teacher(teacher_id)

    def admin_count_classes_for_teacher(self, teacher_id: Union[str, ObjectId]) -> int:
        """
        if teacher has classes, return number of classes
        else return 0
        """
        return self.class_read_model.count_classes_for_teacher(teacher_id)