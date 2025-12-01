from datetime import datetime, date as date_type, time
from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from typing import List
from app.contexts.shared.model_converter import mongo_converter

class AttendanceReadModel:
    """
    Read model to check existing attendance records
    (e.g., to prevent duplicates).
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["attendance"]

    def get_by_student_class_date(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        record_date: date_type | None,
    ) -> dict | None:
        """
        Find an attendance record for (student, class, date).

        If record_date is None, treat it as "today" (UTC),
        mirroring the factory's 'default to today' behavior.
        """
        if record_date is None:
            record_date = datetime.utcnow().date()

        if isinstance(record_date, date_type) and not isinstance(record_date, datetime):
            record_dt = datetime.combine(record_date, time.min)
        else:
            record_dt = record_date  # already datetime

        return self.collection.find_one(
            {
                "student_id": student_id,
                "class_id": class_id,
                "date": record_dt,
            }
        )

    def list_by_student(self, student_id: ObjectId) -> List[dict]:
        return list(self.collection.find({"student_id": student_id}))
    
    def list_teacher_attendance(self, teacher_id: ObjectId) -> List[dict]:
        return list(self.collection.find({"teacher_id": teacher_id}))

    def list_class_attendance(self, class_id: ObjectId) -> List[dict]:
        oid = mongo_converter.convert_to_object_id(class_id)
        return list(self.collection.find({"class_id": oid}))

    def list_student_attendances(
        self,
        student_id: ObjectId,
        class_id: Optional[ObjectId] = None,
    ) -> List[dict]:
        query: dict = {
            "student_id": student_id,
        }
        if class_id is not None:
            query["class_id"] = class_id

        return list(self.collection.find(query))    