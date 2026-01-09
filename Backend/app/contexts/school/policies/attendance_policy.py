

from datetime import date as date_type, datetime, time
from typing import Any, Dict

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import (
    not_deleted,
    by_show_deleted,
    ShowDeleted,
)
from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.model_converter import mongo_converter


class AttendancePolicy:
    """
    Session attendance policy:
      attendance: { student_id, class_id, subject_id, schedule_slot_id, record_date, marked_by_teacher_id, lifecycle... }

    MVP recommended rules (relaxed):
      - Create: teacher must be assigned to (class, subject)
      - AND schedule_slot must belong to the class (+ subject match if slot has subject_id)
      - Do NOT require schedule_slot.teacher_id == actor teacher_id (optional strict mode later)

    Strict rules (optional):
      - Same as above, but also require schedule_slot.teacher_id == actor teacher_id
    """

    def __init__(self, db: Database):
        self.students = db["students"]
        self.classes = db["classes"]
        self.attendance = db["attendance"]
        self.assignments = db["teacher_subject_assignments"]
        self.schedule = db["schedules"]  # your schedules collection name

    # -------------------------
    # Helpers
    # -------------------------
    def _oid(self, v: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    @staticmethod
    def _match_oid_or_str(field: str, oid: ObjectId) -> Dict[str, Any]:
        """Mongo filter that matches either ObjectId or its string form (legacy storage safe)."""
        return {field: {"$in": [oid, str(oid)]}}

    @staticmethod
    def _record_date_match(d: date_type) -> Dict[str, Any]:
        """
        Match canonical record_date stored as:
          - "YYYY-MM-DD" (string) OR
          - datetime at 00:00:00 OR
          - legacy 'date' datetime
        """
        record_str = d.isoformat()
        record_dt = datetime.combine(d, time.min)
        return {
            "$or": [
                {"record_date": record_str},
                {"record_date": record_dt},
                {"date": record_dt},
            ]
        }

    def _is_homeroom(self, *, teacher_id: ObjectId, class_id: ObjectId) -> bool:
        cls = self.classes.find_one(
            not_deleted({"_id": class_id}),
            {"_id": 1, "homeroom_teacher_id": 1, "teacher_id": 1},
        )
        if not cls:
            return False

        homeroom_id = cls.get("homeroom_teacher_id") or cls.get("teacher_id")
        return str(homeroom_id or "") == str(teacher_id)

    def _teacher_assigned(
        self, *, teacher_id: ObjectId, class_id: ObjectId, subject_id: ObjectId
    ) -> bool:
        """
        Robust assignment check: supports ObjectId or string storage in teacher_subject_assignments.
        """
        q = not_deleted(
            {
                "$and": [
                    self._match_oid_or_str("teacher_id", teacher_id),
                    self._match_oid_or_str("class_id", class_id),
                    self._match_oid_or_str("subject_id", subject_id),
                ]
            }
        )
        return self.assignments.count_documents(q, limit=1) > 0

    def _slot_allowed(
        self,
        *,
        schedule_slot_id: ObjectId,
        class_id: ObjectId,
        subject_id: ObjectId,
        actor_teacher_id: ObjectId,
        enforce_owner: bool = False,
    ) -> bool:
        """
        MVP (enforce_owner=False):
          - slot exists
          - slot.class_id matches class_id
          - if slot.subject_id exists => must match subject_id
          - does NOT require slot.teacher_id == actor_teacher_id

        Strict (enforce_owner=True):
          - all above
          - AND slot.teacher_id must equal actor_teacher_id
        """
        slot = self.schedule.find_one(
            not_deleted({"_id": schedule_slot_id}),
            {"_id": 1, "teacher_id": 1, "class_id": 1, "subject_id": 1},
        )
        slot = self.schedule.find_one(
            not_deleted({"_id": schedule_slot_id}),
            {"_id": 1, "teacher_id": 1, "class_id": 1, "subject_id": 1, "lifecycle": 1},
        )

        if not slot:
            return False

        slot_class = slot.get("class_id")
        if str(slot_class or "") != str(class_id):
            return False

        # Strongly recommended to store subject_id on schedule slot.
        slot_subject = slot.get("subject_id")
        if slot_subject is not None and str(slot_subject) != str(subject_id):
            return False

        if enforce_owner:
            slot_teacher = slot.get("teacher_id")
            if str(slot_teacher or "") != str(actor_teacher_id):
                return False

        return True

    # -------------------------
    # Policy: Create
    # -------------------------
    def can_create(
        self,
        *,
        student_id: ObjectId,
        class_id: ObjectId,
        subject_id: ObjectId,
        schedule_slot_id: ObjectId,
        record_date: date_type,
        teacher_id: ObjectId,
        require_student_in_class: bool = True,
        prevent_duplicate: bool = True,
        enforce_slot_owner: bool = False,  # MVP: False, Strict: True
    ) -> PolicyResult:
        # --- class exists + active ---
        cls = self.classes.find_one(
            not_deleted({"_id": class_id}),
            {"_id": 1, "status": 1, "homeroom_teacher_id": 1, "teacher_id": 1},
        )
        if not cls:
            return PolicyResult.deny("create", {"class": "not_found_or_deleted"})

        if cls.get("status") in ("inactive", "archived"):
            return PolicyResult.deny("create", {"class_status": cls.get("status")})

        # --- student exists + enrolled ---
        stu = self.students.find_one(
            not_deleted({"_id": student_id}),
            {"_id": 1, "current_class_id": 1},
        )
        if not stu:
            return PolicyResult.deny("create", {"student": "not_found_or_deleted"})

        if require_student_in_class and str(stu.get("current_class_id") or "") != str(class_id):
            return PolicyResult.deny(
                "create",
                {
                    "enrollment": "student_not_in_class",
                    "student_current_class_id": str(stu.get("current_class_id"))
                    if stu.get("current_class_id")
                    else None,
                },
            )

        # --- assignment required (your core rule) ---
        if not self._teacher_assigned(
            teacher_id=teacher_id, class_id=class_id, subject_id=subject_id
        ):
            return PolicyResult.deny("create", {"permission": "not_assigned_for_subject"})

        # --- schedule slot allowed (MVP relaxed by default) ---
        if not self._slot_allowed(
            schedule_slot_id=schedule_slot_id,
            class_id=class_id,
            subject_id=subject_id,
            actor_teacher_id=teacher_id,
            enforce_owner=enforce_slot_owner,
        ):
            return PolicyResult.deny("create", {"schedule": "slot_not_allowed"})

        # --- prevent duplicates ---
        if prevent_duplicate:
            q = not_deleted(
                {
                    "student_id": student_id,
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "schedule_slot_id": schedule_slot_id,
                    **self._record_date_match(record_date),
                }
            )
            existing = self.attendance.find_one(q, {"_id": 1})
            if existing:
                return PolicyResult.deny(
                    "create",
                    {
                        "duplicate": "attendance_already_exists",
                        "existing_attendance_id": str(existing["_id"]),
                    },
                )

        return PolicyResult.ok("create")

    # -------------------------
    # Policy: Update/Delete
    # -------------------------
    def can_update(
        self,
        *,
        attendance_id: ObjectId,
        actor_teacher_id: ObjectId,
        allow_homeroom_override: bool = False,
    ) -> PolicyResult:
        doc = self.attendance.find_one(
            not_deleted({"_id": attendance_id}),
            {"_id": 1, "class_id": 1, "subject_id": 1},
        )
        if not doc:
            return PolicyResult.deny("update", {"attendance": "not_found_or_deleted"})

        class_id = doc["class_id"]
        subject_id = doc["subject_id"]

        if allow_homeroom_override and self._is_homeroom(
            teacher_id=actor_teacher_id, class_id=class_id
        ):
            return PolicyResult.ok("update")

        if self._teacher_assigned(
            teacher_id=actor_teacher_id, class_id=class_id, subject_id=subject_id
        ):
            return PolicyResult.ok("update")

        return PolicyResult.deny("update", {"permission": "forbidden"})

    def can_soft_delete(
        self, *, attendance_id: ObjectId, actor_teacher_id: ObjectId
    ) -> PolicyResult:
        return self.can_update(
            attendance_id=attendance_id,
            actor_teacher_id=actor_teacher_id,
            allow_homeroom_override=False,
        )

    def can_hard_delete(self, attendance_id: ObjectId) -> PolicyResult:
        exists = self.attendance.count_documents(
            by_show_deleted("all", {"_id": attendance_id}),
            limit=1,
        )
        if exists == 0:
            return PolicyResult.deny("hard", {"attendance": "not_found"})
        return PolicyResult.ok("hard")

    def can_restore(self, attendance_id: ObjectId) -> PolicyResult:
        exists = self.attendance.count_documents(
            by_show_deleted("all", {"_id": attendance_id}),
            limit=1,
        )
        if exists == 0:
            return PolicyResult.deny("restore", {"attendance": "not_found"})
        return PolicyResult.ok("restore")