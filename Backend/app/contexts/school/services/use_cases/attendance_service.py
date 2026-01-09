
from typing import Optional
from datetime import date as date_type
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus, today_kh
from app.contexts.school.errors.attendance_exceptions import AttendanceNotFoundException
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException
from app.contexts.shared.lifecycle.filters import not_deleted

from ._base import OidMixin


class AttendanceService(OidMixin):
    def __init__(
        self,
        *,
        attendance_repo,
        attendance_factory,
        attendance_policy,
        attendance_lifecycle,
    ):
        self.attendance_repo = attendance_repo
        self.attendance_factory = attendance_factory
        self.attendance_policy = attendance_policy
        self.attendance_lifecycle = attendance_lifecycle

    def mark_attendance_session(
        self,
        *,
        student_id: str | ObjectId,
        class_id: str | ObjectId,
        subject_id: str | ObjectId,
        schedule_slot_id: str | ObjectId,
        status: AttendanceStatus | str,
        teacher_id: str | ObjectId,
        record_date: date_type | None = None,
        prevent_duplicate: bool = True,
        enforce_slot_class_match: bool = True,  # MVP: True (recommended)
    ) -> AttendanceRecord:
        # 1) Always give policy a real date
        effective_date: date_type = record_date or today_kh()

        student_oid = self._oid(student_id)
        class_oid = self._oid(class_id)
        subject_oid = self._oid(subject_id)
        slot_oid = self._oid(schedule_slot_id)
        teacher_oid = self._oid(teacher_id)

        # 2) Load slot once and make it authoritative for subject (prevents UI mismatch)
        slot = self.attendance_policy.schedule.find_one(
            not_deleted({"_id": slot_oid}),
            {"_id": 1, "class_id": 1, "subject_id": 1},
        )
        if not slot:
            raise LifecyclePolicyDeniedException(
                entity="attendance",
                entity_id="(new)",
                mode="create",
                reasons={"schedule": "slot_not_found_or_deleted"},
                recommended=None,
            )

        # 2a) Enforce slot must belong to the selected class (security + correctness)
        slot_class_id = slot.get("class_id")
        if enforce_slot_class_match and str(slot_class_id or "") != str(class_oid):
            raise LifecyclePolicyDeniedException(
                entity="attendance",
                entity_id="(new)",
                mode="create",
                reasons={"schedule": "slot_class_mismatch"},
                recommended=None,
            )

        # 2b) If slot has subject_id, override request subject_id with slot subject_id
        slot_subject_id = slot.get("subject_id")
        if slot_subject_id:
            subject_oid = slot_subject_id  # authoritative

        # 3) Policy check (now subject_id is consistent with slot)
        can = self.attendance_policy.can_create(
            student_id=student_oid,
            class_id=class_oid,
            subject_id=subject_oid,
            schedule_slot_id=slot_oid,
            teacher_id=teacher_oid,
            record_date=effective_date,
            prevent_duplicate=prevent_duplicate,
        )
        if not can.allowed:
            raise LifecyclePolicyDeniedException(
                entity="attendance",
                entity_id="(new)",
                mode=can.mode,
                reasons=can.reasons,
                recommended=can.recommended,
            )

        # 4) Create record using the same normalized ids
        record = self.attendance_factory.create_record(
            student_id=student_oid,
            class_id=class_oid,
            subject_id=subject_oid,
            schedule_slot_id=slot_oid,
            status=status,
            teacher_id=teacher_oid,
            record_date=effective_date,
        )
        return self.attendance_repo.insert(record)

    def change_attendance_status(
        self,
        attendance_id: str | ObjectId,
        new_status: AttendanceStatus | str,
        *,
        actor_teacher_id: str | ObjectId,
    ) -> Optional[AttendanceRecord]:
        oid = self._oid(attendance_id)
        actor = self._oid(actor_teacher_id)

        can = self.attendance_policy.can_update(attendance_id=oid, actor_teacher_id=actor)
        if not can.allowed:
            raise LifecyclePolicyDeniedException(
                entity="attendance",
                entity_id=str(oid),
                mode=can.mode,
                reasons=can.reasons,
                recommended=can.recommended,
            )

        existing = self.attendance_repo.find_by_id(oid)
        if existing is None:
            raise AttendanceNotFoundException(str(attendance_id))

        existing.change_status(new_status, actor_id=actor)
        return self.attendance_repo.update(existing)

    def soft_delete_attendance(self, *, attendance_id: str | ObjectId, actor_teacher_id: str | ObjectId) -> int:
        oid = self._oid(attendance_id)
        actor = self._oid(actor_teacher_id)

        can = self.attendance_policy.can_soft_delete(attendance_id=oid, actor_teacher_id=actor)
        if not can.allowed:
            raise LifecyclePolicyDeniedException(
                entity="attendance",
                entity_id=str(oid),
                mode=can.mode,
                reasons=can.reasons,
                recommended=can.recommended,
            )

        res = self.attendance_lifecycle.soft_delete_attendance(attendance_id=oid, actor_teacher_id=actor_teacher_id)
        return int(res.modified_count)

    def restore_attendance(self, attendance_id: str | ObjectId, actor_id: str | ObjectId | None = None) -> int:
        oid = self._oid(attendance_id)
        res = self.attendance_lifecycle.restore_attendance(
            attendance_id=oid,
            actor_id=self._oid(actor_id) if actor_id else None,
        )
        return int(res.modified_count)

    def hard_delete_attendance(self, attendance_id: str | ObjectId, actor_id: str | ObjectId) -> int:
        oid = self._oid(attendance_id)
        res = self.attendance_lifecycle.hard_delete_attendance(attendance_id=oid, actor_id=self._oid(actor_id))
        return int(res.deleted_count)

    def get_attendance_by_id(self, attendance_id: str | ObjectId) -> Optional[AttendanceRecord]:
        return self.attendance_repo.find_by_id(self._oid(attendance_id))