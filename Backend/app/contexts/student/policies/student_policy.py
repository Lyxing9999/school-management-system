from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.filters import not_deleted


class StudentPolicy:
    def __init__(self, db: Database):
        self.students = db.students
        self.attendance = db.attendance
        self.grades = db.grades

    def _get_student_by_user_id(self, user_id: ObjectId) -> dict | None:
        return self.students.find_one(not_deleted({"user_id": user_id}), {"_id": 1, "current_class_id": 1})

    # Called when deleting IAM user with role=student
    def can_soft_delete_user(self, user_id: ObjectId) -> PolicyResult:
        student = self._get_student_by_user_id(user_id)
        if not student:
            return PolicyResult.ok("soft")

        if student.get("current_class_id") is not None:
            return PolicyResult.deny("soft", {"enrolled_in_class": str(student["current_class_id"])})

        return PolicyResult.ok("soft")

    def can_hard_delete_user(self, user_id: ObjectId) -> PolicyResult:
        student = self._get_student_by_user_id(user_id)
        if not student:
            return PolicyResult.ok("hard")

        student_id = student["_id"]

        a = self.attendance.count_documents(not_deleted({"student_id": student_id}))
        g = self.grades.count_documents(not_deleted({"student_id": student_id}))

        if a > 0 or g > 0:
            return PolicyResult.deny("hard", {"attendance": a, "grades": g}, recommended="soft")
        return PolicyResult.ok("hard")

    def can_restore_user(self, user_id: ObjectId) -> PolicyResult:

        exists = self.students.count_documents({"user_id": user_id})
        if exists == 0:
            return PolicyResult.deny("restore", {"student": "not_found"})
        return PolicyResult.ok("restore")