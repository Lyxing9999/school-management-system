
from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import by_show_deleted, not_deleted
from app.contexts.shared.lifecycle.policy_result import PolicyResult


class SubjectPolicy:
    """
    Subject is reference data.
    Rule: cannot delete if still referenced by active entities.

    Lifecycle consistency:
    - soft delete checks operate on ACTIVE subject + count ACTIVE references (not deleted)
    - hard delete checks operate on ANY subject + count ALL references
    - restore checks operate on ANY subject
    """

    def __init__(self, db: Database):
        self.subjects = db["subjects"]
        self.classes = db["classes"]
        self.schedules = db["schedules"]
        self.grades = db["grades"]

    def can_soft_delete(self, subject_id: ObjectId) -> PolicyResult:
        sub = self.subjects.find_one(not_deleted({"_id": subject_id}), {"_id": 1})
        if not sub:
            return PolicyResult.deny("soft", {"subject": "not_found_or_deleted"})

        blockers: dict = {}

        class_count = self.classes.count_documents(not_deleted({"subject_ids": subject_id}))
        if class_count > 0:
            blockers["classes_using_subject"] = class_count

        sched_count = self.schedules.count_documents(not_deleted({"subject_id": subject_id}))
        if sched_count > 0:
            blockers["schedules_using_subject"] = sched_count

        grade_count = self.grades.count_documents(not_deleted({"subject_id": subject_id}))
        if grade_count > 0:
            blockers["grades_using_subject"] = grade_count

        if blockers:
            return PolicyResult.deny("soft", blockers, recommended="deactivate")

        return PolicyResult.ok("soft")

    def can_hard_delete(self, subject_id: ObjectId) -> PolicyResult:
        exists = self.subjects.count_documents(by_show_deleted("all", {"_id": subject_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("hard", {"subject": "not_found"})

        blockers: dict = {}

        class_count = self.classes.count_documents({"subject_ids": subject_id})
        if class_count > 0:
            blockers["classes_using_subject"] = class_count

        sched_count = self.schedules.count_documents({"subject_id": subject_id})
        if sched_count > 0:
            blockers["schedules_using_subject"] = sched_count

        grade_count = self.grades.count_documents({"subject_id": subject_id})
        if grade_count > 0:
            blockers["grades_using_subject"] = grade_count

        if blockers:
            return PolicyResult.deny("hard", blockers, recommended="soft")

        return PolicyResult.ok("hard")

    def can_restore(self, subject_id: ObjectId) -> PolicyResult:
        exists = self.subjects.count_documents(by_show_deleted("all", {"_id": subject_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("restore", {"subject": "not_found"})
        return PolicyResult.ok("restore")