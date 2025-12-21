from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.types import not_deleted
from app.contexts.student.policies.student_policy import StudentPolicy
from app.contexts.staff.policies.staff_policy import StaffPolicy


class IAMPolicy:
    def __init__(self, db: Database):
        self.iam = db.iam

        # Role policies
        self._student_policy = StudentPolicy(db)
        self._staff_policy = StaffPolicy(db)

        # Router map: easy to add more later
        self._soft_delete_router = {
            "student": self._student_policy.can_soft_delete_user,
            "teacher": self._staff_policy.can_soft_delete_user,
        }
        self._hard_delete_router = {
            "student": self._student_policy.can_hard_delete_user,
            "teacher": self._staff_policy.can_hard_delete_user,
        }
        self._restore_router = {
            "student": self._student_policy.can_restore_user,
            "teacher": self._staff_policy.can_restore_user,
        }

    def _get_role(self, user_id: ObjectId) -> str | None:
        user = self.iam.find_one(not_deleted({"_id": user_id}), {"role": 1})
        if not user:
            return None
        return user.get("role")

    def can_soft_delete_user(self, user_id: ObjectId) -> PolicyResult:
        role = self._get_role(user_id)
        if not role:
            return PolicyResult.deny("soft", {"user": "not_found_or_deleted"})

        handler = self._soft_delete_router.get(role)
        if handler:
            return handler(user_id)

        return PolicyResult.ok("soft")

    def can_hard_delete_user(self, user_id: ObjectId) -> PolicyResult:
        role = self._get_role(user_id)
        if not role:
            return PolicyResult.deny("hard", {"user": "not_found_or_deleted"})

        handler = self._hard_delete_router.get(role)
        if handler:
            return handler(user_id)

        return PolicyResult.ok("hard")

    def can_restore_user(self, user_id: ObjectId) -> PolicyResult:

        user = self.iam.find_one({"_id": user_id}, {"role": 1})
        if not user:
            return PolicyResult.deny("restore", {"user": "not_found"})

        role = user.get("role")
        handler = self._restore_router.get(role)
        if handler:
            return handler(user_id)

        return PolicyResult.ok("restore")