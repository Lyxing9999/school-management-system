from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from contexts.shared.lifecycle.policy_result import PolicyResult


class StudentPolicy:
    def __init__(self, db: Database):
        self.students = db.students
        self.attendance = db.attendance
        self.grades = db.grades

    def can_soft_delete(self, student_id: ObjectId) -> PolicyResult:
        # Usually always allowed (soft delete preserves history)
        exists = self.students.count_documents({"_id": student_id})
        if exists == 0:
            return PolicyResult.deny("soft", {"student": "not_found"})
        return PolicyResult.ok("soft")

    def can_hard_delete(self, student_id: ObjectId) -> PolicyResult:
        exists = self.students.count_documents({"_id": student_id})
        if exists == 0:
            return PolicyResult.deny("hard", {"student": "not_found"})

        a = self.attendance.count_documents({"student_id": student_id})
        g = self.grades.count_documents({"student_id": student_id})

        if a > 0 or g > 0:
            return PolicyResult.deny("hard", {"attendance": a, "grades": g}, recommended="soft")

        return PolicyResult.ok("hard")

    def can_restore(self, student_id: ObjectId) -> PolicyResult:
        exists = self.students.count_documents({"_id": student_id})
        if exists == 0:
            return PolicyResult.deny("restore", {"student": "not_found"})
        return PolicyResult.ok("restore")