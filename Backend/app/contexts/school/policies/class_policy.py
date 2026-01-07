from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import by_show_deleted, not_deleted
from app.contexts.shared.lifecycle.policy_result import PolicyResult


class ClassPolicy:
    """
    Rules for ClassSection lifecycle actions.

    Lifecycle consistency:
    - soft delete checks operate on ACTIVE class (not deleted)
    - restore checks operate on ANY class (including deleted)
    - related blockers for soft delete count only ACTIVE related docs (not deleted)
    - related blockers for hard delete count ALL related docs
    """

    def __init__(self, db: Database):
        self.classes = db["classes"]
        self.schedules = db["schedules"]
        self.attendance = db["attendance"]
        self.grades = db["grades"]
        self.students = db["students"]

    def can_soft_delete(self, class_id: ObjectId) -> PolicyResult:
        cls = self.classes.find_one(
            not_deleted({"_id": class_id}),
            {"enrolled_count": 1},
        )
        if not cls:
            return PolicyResult.deny("soft", {"class": "not_found_or_deleted"})

        blockers: dict = {}

        enrolled_count = int(cls.get("enrolled_count") or 0)
        if enrolled_count > 0:
            blockers["enrolled_students"] = enrolled_count

        sch = self.schedules.count_documents(not_deleted({"class_id": class_id}))
        if sch > 0:
            blockers["schedule_slots"] = sch

        att = self.attendance.count_documents(not_deleted({"class_id": class_id}))
        if att > 0:
            blockers["attendance_records"] = att

        grd = self.grades.count_documents(not_deleted({"class_id": class_id}))
        if grd > 0:
            blockers["grade_records"] = grd

        if blockers:
            return PolicyResult.deny("soft", blockers, recommended="archive")

        return PolicyResult.ok("soft")

    def can_hard_delete(self, class_id: ObjectId) -> PolicyResult:
        exists = self.classes.count_documents(by_show_deleted("all", {"_id": class_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("hard", {"class": "not_found"})

        blockers: dict = {}

        sch = self.schedules.count_documents({"class_id": class_id})
        if sch > 0:
            blockers["schedule_slots"] = sch

        att = self.attendance.count_documents({"class_id": class_id})
        if att > 0:
            blockers["attendance_records"] = att

        grd = self.grades.count_documents({"class_id": class_id})
        if grd > 0:
            blockers["grade_records"] = grd

        if blockers:
            return PolicyResult.deny("hard", blockers, recommended="soft")

        return PolicyResult.ok("hard")

    def can_restore(self, class_id: ObjectId) -> PolicyResult:
        exists = self.classes.count_documents(by_show_deleted("all", {"_id": class_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("restore", {"class": "not_found"})
        return PolicyResult.ok("restore")