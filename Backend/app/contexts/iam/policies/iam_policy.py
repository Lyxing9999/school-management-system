from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from app.contexts.shared.lifecycle.policy_result import PolicyResult


class IAMPolicy:
    def __init__(self, db: Database):
        self.users = db.users
        self.students = db.students
        self.staff = db.staff

    def can_hard_delete_user(self, user_id: ObjectId) -> PolicyResult:
        # user cannot be hard-deleted if referenced by student or staff
        s = self.students.count_documents({"user_id": user_id})
        t = self.staff.count_documents({"user_id": user_id})
        if s > 0 or t > 0:
            return PolicyResult.deny("hard", {"student_profiles": s, "staff_profiles": t}, recommended="soft")
        return PolicyResult.ok("hard")