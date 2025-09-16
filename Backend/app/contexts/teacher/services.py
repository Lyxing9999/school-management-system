from typing import Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
from app.contexts.users.aggregates import TeacherAggregate
from app.contexts.users.error.user_exceptions import NotFoundUserException
import logging

logger = logging.getLogger(__name__)

class TeacherService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db["teachers"]  # separate collection or use "users" with role filter

    # -------------------------
    # Teacher Operations
    # -------------------------
    def input_attendance(self, teacher_id: str, student_id: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Record attendance for a student"""
        teacher_id = ObjectId(teacher_id)
        teacher_raw = self.collection.find_one({"_id": teacher_id})
        if not teacher_raw:
            raise NotFoundUserException(teacher_id)

        teacher_agg = TeacherAggregate(
            username=teacher_raw["username"],
            email=teacher_raw["email"],
            password=teacher_raw["password"],
            subjects=teacher_raw.get("subjects", []),
            created_at=teacher_raw.get("created_at"),
            updated_at=teacher_raw.get("updated_at")
        )

        date = date or datetime.utcnow().isoformat()
        # TODO: integrate with AttendanceRepository or embed attendance in DB
        logger.info(f"Teacher {teacher_id} recorded attendance for student {student_id} on {date}")

        return {"teacher_id": str(teacher_id), "student_id": student_id, "date": date, "status": "present"}

    def input_score(self, teacher_id: str, student_id: str, course_id: str, score: float) -> Dict[str, Any]:
        """Record a score for a student in a course"""
        teacher_id = ObjectId(teacher_id)
        teacher_raw = self.collection.find_one({"_id": teacher_id})
        if not teacher_raw:
            raise NotFoundUserException(teacher_id)

        teacher_agg = TeacherAggregate(
            username=teacher_raw["username"],
            email=teacher_raw["email"],
            password=teacher_raw["password"],
            subjects=teacher_raw.get("subjects", []),
            created_at=teacher_raw.get("created_at"),
            updated_at=teacher_raw.get("updated_at")
        )

        # TODO: integrate with GradesRepository or embed scores in DB
        logger.info(f"Teacher {teacher_id} recorded score {score} for student {student_id} in course {course_id}")
        return {"teacher_id": str(teacher_id), "student_id": student_id, "course_id": course_id, "score": score}

    def get_schedule(self, teacher_id: str) -> Dict[str, Any]:
        """Return the teacher's schedule"""
        teacher_id = ObjectId(teacher_id)
        teacher_raw = self.collection.find_one({"_id": teacher_id})
        if not teacher_raw:
            raise NotFoundUserException(teacher_id)

        # TODO: integrate with ScheduleRepository or collection
        logger.info(f"Fetching schedule for teacher {teacher_id}")
        schedule = teacher_raw.get("schedule", [])
        return {"teacher_id": str(teacher_id), "schedule": schedule}