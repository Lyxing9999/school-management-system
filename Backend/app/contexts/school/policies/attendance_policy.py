from datetime import date as date_type, datetime, time
from typing import Any, Dict

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import not_deleted, by_show_deleted
from app.contexts.shared.lifecycle.policy_result import PolicyResult


class AttendancePolicy:
    """
    Policy for AttendanceRecord operations (create/update/delete guards).

    Lifecycle consistency:
    - Existence checks for create/update/soft-delete operate on ACTIVE docs (not deleted)
    - Hard delete checks operate on ANY docs (including deleted)

    Notes:
    - Duplicate definition (optional): one attendance per (student_id, class_id, record_date)
    - Date compatibility: supports `record_date` and legacy `date` fields.
    """

    def __init__(self, db: Database):
        self.students = db["students"]
        self.classes = db["classes"]
        self.attendance = db["attendance"]

    def _midnight_dt(self, d: date_type) -> datetime:
        return datetime.combine(d, time.min)

    def _date_match(self, d: date_type) -> Dict[str, Any]:
        dt0 = self._midnight_dt(d)
        return {"$or": [{"record_date": dt0}, {"date": dt0}]}

    def can_create(
        self,
        *,
        student_id: ObjectId,
        class_id: ObjectId,
        record_date: date_type,
        teacher_id: ObjectId | None = None,
        require_student_in_class: bool = False,
        require_teacher_is_class_teacher: bool = False,
        prevent_duplicate: bool = True,
    ) -> PolicyResult:
        blockers: Dict[str, Any] = {}

        cls = self.classes.find_one(
            not_deleted({"_id": class_id}),
            {"_id": 1, "teacher_id": 1, "status": 1},
        )
        if not cls:
            blockers["class"] = "not_found_or_deleted"
            return PolicyResult.deny("create", blockers)

        status = cls.get("status")
        if status in ("inactive", "archived"):
            blockers["class_status"] = status
            return PolicyResult.deny("create", blockers)

        if require_teacher_is_class_teacher and teacher_id is not None:
            if cls.get("teacher_id") != teacher_id:
                blockers["teacher"] = "not_class_teacher"
                return PolicyResult.deny("create", blockers)

        stu = self.students.find_one(
            not_deleted({"_id": student_id}),
            {"_id": 1, "current_class_id": 1},
        )
        if not stu:
            blockers["student"] = "not_found_or_deleted"
            return PolicyResult.deny("create", blockers)

        if require_student_in_class:
            if stu.get("current_class_id") != class_id:
                blockers["enrollment"] = "student_not_in_class"
                blockers["student_current_class_id"] = (
                    str(stu.get("current_class_id")) if stu.get("current_class_id") else None
                )
                return PolicyResult.deny("create", blockers)

        if prevent_duplicate:
            q: Dict[str, Any] = not_deleted(
                {
                    "student_id": student_id,
                    "class_id": class_id,
                    **self._date_match(record_date),
                }
            )
            existing = self.attendance.find_one(q, {"_id": 1})
            if existing:
                blockers["duplicate"] = "attendance_already_exists"
                blockers["existing_attendance_id"] = str(existing["_id"])
                return PolicyResult.deny("create", blockers)

        return PolicyResult.ok("create")

    def can_update(self, attendance_id: ObjectId) -> PolicyResult:
        exists = self.attendance.count_documents(not_deleted({"_id": attendance_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("update", {"attendance": "not_found_or_deleted"})
        return PolicyResult.ok("update")

    def can_soft_delete(self, attendance_id: ObjectId) -> PolicyResult:
        exists = self.attendance.count_documents(not_deleted({"_id": attendance_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("soft", {"attendance": "not_found_or_deleted"})
        return PolicyResult.ok("soft")

    def can_hard_delete(self, attendance_id: ObjectId) -> PolicyResult:
        exists = self.attendance.count_documents(by_show_deleted("all", {"_id": attendance_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("hard", {"attendance": "not_found"})
        return PolicyResult.ok("hard")

    def can_restore(self, attendance_id: ObjectId) -> PolicyResult:
        exists = self.attendance.count_documents(by_show_deleted("all", {"_id": attendance_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("restore", {"attendance": "not_found"})
        return PolicyResult.ok("restore")