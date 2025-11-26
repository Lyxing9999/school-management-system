
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from pymongo.database import Database
from bson import ObjectId
from typing import List , Tuple , Union , Optional
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_model import StaffReadModel

class AdminReadModel(MongoErrorMixin):
    def __init__(self, db: Database , collection_classes: str = "classes", collection_subjects: str = "subjects" ):
        self.db = db

        self.collection_classes = db[collection_classes]
        self.collection_subjects = db[collection_subjects]
        self.mongo_converter = mongo_converter
        self._iam_read_model: Optional[IAMReadModel] = None
        self._staff_read_model: Optional[StaffReadModel] = None

    @property
    def iam_read_model(self) -> IAMReadModel:
        if self._iam_read_model is None:
            self._iam_read_model = IAMReadModel(self.db)
        return self._iam_read_model

    @property
    def staff_read_model(self) -> StaffReadModel:
        if self._staff_read_model is None:
            self._staff_read_model = StaffReadModel(self.db)
        return self._staff_read_model



    def get_staff_by_id(self, staff_id: ObjectId) -> Optional[dict]:
        return self.staff_read_model.get_by_id(staff_id)

    def get_user_by_id(self, user_id: ObjectId) -> Optional[dict]:
        return self.iam_read_model.get_by_id(user_id)


    def get_staff_name_select(self) -> List[dict]:
        return self.staff_read_model.get_staff_name_select()
    

    def get_student_name_select(self) -> List[dict]:
        return self.iam_read_model.get_student_name_select()

    
    def get_page_by_role(self, roles: Union[str, list[str]], page: int = 1, page_size: int = 5) -> Tuple[List[dict], int]:
        return self.iam_read_model.get_page_by_role(roles, page, page_size)
        