from __future__ import annotations
from datetime import datetime, date as date_type
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from typing import List


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

        return self.collection.find_one(
            {
                "student_id": student_id,
                "class_id": class_id,
                "date": record_date,
            }
        )

    def list_by_student(self, student_id: ObjectId) -> List[dict]:
        return list(self.collection.find({"student_id": student_id}))
    
    def list_teacher_attendance(self, teacher_id: ObjectId) -> List[dict]:
        return list(self.collection.find({"teacher_id": teacher_id}))

    def list_class_attendance(self, class_id: ObjectId) -> List[dict]:
        return list(self.collection.find({"class_id": class_id}))

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
