from typing import List, Tuple, Union, Optional, Final
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin

from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
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


    # ------------- simple delegates -------------

    def get_staff_by_user_id(self, user_id: ObjectId) -> Optional[dict]:
        return self._staff_read_model.get_by_user_id(user_id)

    def admin_get_student_by_user_id(self, user_id: ObjectId | str) -> Optional[dict]:
        if isinstance(user_id, str):
            user_id = mongo_converter.convert_to_object_id(user_id)
        return self._student_read_model.get_by_user_id(user_id)

    def get_user_by_id(self, user_id: ObjectId) -> Optional[dict]:
        return self._iam_read_model.get_by_id(user_id)

    def get_page_by_role(
        self,
        roles: Union[str, List[str]],
        page: int = 1,
        page_size: int = 5,
        search: Optional[str] = None,
    ) -> Tuple[List[dict], int]:
        """
        Reuse IAMReadModel pagination (already decorates created_by_name).
        """
        return self._iam_read_model.get_page_by_role(roles, page, page_size, search)

    # ------------- schedules with names -------------

    def admin_list_schedules_for_class_enriched(self, class_id: Union[str, ObjectId]) -> List[dict]:

        oid = mongo_converter.convert_to_object_id(class_id)
        class_schedules = self._schedule_read_model.list_schedules_for_class(oid)
        if not class_schedules:
            return []
        enriched = self._display_name_service.enrich_schedules(class_schedules)
        return enriched

    def admin_list_schedules_for_teacher_enriched(self, teacher_id: Union[str, ObjectId]) -> List[dict]:

        oid = mongo_converter.convert_to_object_id(teacher_id)
        teacher_schedules = self._schedule_read_model.list_schedules_for_teacher(oid)
        if not teacher_schedules:
            return []
        enriched = self._display_name_service.enrich_schedules(teacher_schedules)
        return enriched

    def admin_list_classes_enriched(self) -> List[dict]:
        classes = self._class_read_model.list_all()
        if not classes:
            return []
        enriched = self._display_name_service.enrich_classes(classes)
        return enriched


    # ------------- dropdowns / selects -------------

    def admin_list_teacher_select(self) -> List[dict]:
        """
        For teacher dropdowns: returns raw staff docs with {user_id, staff_name, ...}
        Frontend RemoteSelect will map to label/value.
        """
        return self._staff_read_model.list_staff_name_options(role="teacher")

    def admin_list_student_select(self) -> List[dict]:
        """
        For student dropdowns:
        returns [{ "value": "<student_id>", "label": "First Last / KH Name" }, ...]
        """
        docs = self._student_read_model.list_student_name_options()

        items: List[dict] = []
        for d in docs:
            sid = d.get("_id")
            if not sid:
                continue

            first_en = (d.get("first_name_en") or "").strip()
            last_en  = (d.get("last_name_en") or "").strip()
            first_kh = (d.get("first_name_kh") or "").strip()
            last_kh  = (d.get("last_name_kh") or "").strip()

            full_en = f"{first_en} {last_en}".strip()
            full_kh = f"{last_kh} {first_kh}".strip()

            label = full_en
            if full_kh:
                label = f"{full_en} / {full_kh}".strip(" /")

            items.append({"value": str(sid), "label": label})

        items.sort(key=lambda x: (x["label"] or "").lower())
        return items
    def admin_list_enrollment_student_select(self, class_id: str | ObjectId) -> List[dict]:
        filter_ = {
            "status": "Active",
            "$or": [
                {"current_class_id": {"$exists": False}},
                {"current_class_id": None},
            ],
        }


        docs = self._student_read_model.list_student_name_options(filter=filter_, projection={"_id": 1, "current_class_id": 1})
        student_ids = [d["_id"] for d in docs if d.get("_id")]
        return self._display_name_service.student_select_options_for_ids(student_ids)
    
    def admin_list_students_in_class_select(self, class_id: str | ObjectId) -> List[dict]:
        coid = mongo_converter.convert_to_object_id(class_id)

        filter_ = {
            "status": "Active",
            "current_class_id": coid,
        }

        docs = self._student_read_model.list_student_name_options(filter=filter_, projection={"_id": 1})
        student_ids = [d["_id"] for d in docs if d.get("_id")]
        return self._display_name_service.student_select_options_for_ids(student_ids)


    def admin_list_class_select(self) -> List[dict]:

        """
        For class dropdowns: returns [{_id, name}, ...] for classes.
        """
        return self._class_read_model.list_class_names()

    def admin_get_schedule_by_id(self, slot_id: Union[str, ObjectId]) -> Optional[dict]:
        """
        For schedule dropdowns: returns raw schedule docs with {_id, name, ...}
        Frontend RemoteSelect will map to label/value.
        """
        return self._schedule_read_model.get_by_id(slot_id)




    # ------------- helpers -------------
    """
    check relationship before delete
    """
    def admin_count_schedules_for_teacher(self, teacher_id: Union[str, ObjectId]) -> int:
        """
        if teacher has schedules, return number of schedules
        else return 0
        """
        return self._schedule_read_model.count_schedules_for_teacher(teacher_id)

    def admin_count_classes_for_teacher(self, teacher_id: Union[str, ObjectId]) -> int:
        """
        if teacher has classes, return number of classes
        else return 0
        """
        return self._class_read_model.count_classes_for_teacher(teacher_id)