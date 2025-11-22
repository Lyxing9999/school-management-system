from __future__ import annotations
from datetime import datetime, date as date_type
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection


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