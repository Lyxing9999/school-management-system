from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.policy_result import PolicyResult


LIFECYCLE_NOT_DELETED = {"lifecycle.deleted_at": None}


class SubjectPolicy:
    """
    Subject is reference data.
    Rule: cannot delete if still referenced by active entities.
    """

    def __init__(self, db: Database):
        self.subjects = db.subjects
        self.classes = db.classes
        self.schedules = db.schedules  
        self.grades = db.grades

    def can_soft_delete(self, subject_id: ObjectId) -> PolicyResult:
        sub = self.subjects.find_one({"_id": subject_id, **LIFECYCLE_NOT_DELETED}, {"_id": 1})
        if not sub:
            return PolicyResult.deny("soft", {"subject": "not_found_or_deleted"})

        blockers: dict = {}

        # Your main requirement:
        class_count = self.classes.count_documents({"subject_ids": subject_id, **LIFECYCLE_NOT_DELETED})
        if class_count > 0:
            blockers["classes_using_subject"] = class_count

        # Optional: if schedules store subject_id
        sched_count = self.schedules.count_documents({"subject_id": subject_id, **LIFECYCLE_NOT_DELETED})
        if sched_count > 0:
            blockers["schedules_using_subject"] = sched_count

        # Optional: block if there are grades already (history)
        grade_count = self.grades.count_documents({"subject_id": subject_id, **LIFECYCLE_NOT_DELETED})
        if grade_count > 0:
            blockers["grades_using_subject"] = grade_count

        if blockers:
            return PolicyResult.deny("soft", blockers, recommended="deactivate")

        return PolicyResult.ok("soft")

    def can_hard_delete(self, subject_id: ObjectId) -> PolicyResult:
        exists = self.subjects.count_documents({"_id": subject_id})
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
        exists = self.subjects.count_documents({"_id": subject_id})
        if exists == 0:
            return PolicyResult.deny("restore", {"subject": "not_found"})
        return PolicyResult.ok("restore")