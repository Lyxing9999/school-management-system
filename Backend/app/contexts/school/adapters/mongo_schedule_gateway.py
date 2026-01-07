from typing import Optional, Any
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.lifecycle.filters import not_deleted
from app.contexts.school.ports.schedule_port import SchedulePort


class MongoScheduleGateway(SchedulePort):
    def __init__(self, db: Database):
        self.collection: Collection = db["schedules"]

    def class_has_active_schedule(
        self,
        class_id: Any,
        *,
        session: Optional[Any] = None
    ) -> bool:
        oid = mongo_converter.convert_to_object_id(class_id)

        base = {"$or": [{"class_id": oid}, {"class_id": str(oid)}]}
        query = not_deleted(base)

        doc = self.collection.find_one(query, session=session)
        return doc is not None