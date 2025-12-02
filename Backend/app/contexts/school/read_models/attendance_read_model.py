from datetime import datetime, date as date_type, time
from typing import Optional, List, Dict, Union

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter


class AttendanceReadModel:
    """
    Read model to check existing attendance records
    and list attendance by various filters.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["attendance"]

    def _normalize_id(self, id_: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def get_by_student_class_date(
        self,
        student_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        record_date: Optional[date_type] = None,
    ) -> Optional[Dict]:
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

        sid = self._normalize_id(student_id)
        cid = self._normalize_id(class_id)

        return self.collection.find_one(
            {
                "student_id": sid,
                "class_id": cid,
                "date": record_dt,
            }
        )

    def list_attendance_for_student(self, student_id: Union[str, ObjectId]) -> List[Dict]:
        sid = self._normalize_id(student_id)
        return list(self.collection.find({"student_id": sid}))

    def list_attendance_for_teacher(self, teacher_id: Union[str, ObjectId]) -> List[Dict]:
        tid = self._normalize_id(teacher_id)
        return list(self.collection.find({"teacher_id": tid}))

    def list_attendance_for_class(self, class_id: Union[str, ObjectId]) -> List[Dict]:
        cid = self._normalize_id(class_id)
        return list(self.collection.find({"class_id": cid}))

    def list_attendance_for_class_and_student(
        self,
        class_id: Union[str, ObjectId],
        student_id: Optional[Union[str, ObjectId]] = None,
    ) -> List[Dict]:
        cid = self._normalize_id(class_id)
        query: Dict = {"class_id": cid}

        if student_id is not None:
            sid = self._normalize_id(student_id)
            query["student_id"] = sid

        return list(self.collection.find(query))