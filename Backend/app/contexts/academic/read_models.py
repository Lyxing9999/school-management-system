
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from pymongo.database import Database
from bson import ObjectId

from app.contexts.staff.read_models import StaffReadModel
class academic_read_model(MongoErrorMixin):
    def __init__(self, db: Database, collection_users: str = "users", collection_classes:  str = "classes"):
        self._db = db
        self._user = self._db[collection_users]
        self._class = self._db[collection_classes]
        self._staff_read_model = StaffReadModel(self._db)


    def get_all_classes(self) -> dict:
        try:
            return self._class.find({})
        except Exception as e:
            self._handle_mongo_error(e)
 

    def get_staff_name_select(self, search_text: str = "") -> list[dict]:
        return self._staff_read_model.get_staff_name_select(search_text)

    def list_teacher_names(self) -> list[dict]:
        return self._staff_read_model.list_teacher_names()