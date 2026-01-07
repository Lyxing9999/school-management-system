
from typing import Optional
from datetime import date as date_type
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.errors.attendance_exceptions import AttendanceNotFoundException
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException

from ._base import OidMixin


class AttendanceService(OidMixin):
    def __init__(self, *, attendance_repo, attendance_factory, attendance_policy, attendance_lifecycle):
        self.attendance_repo = attendance_repo
        self.attendance_factory = attendance_factory
        self.attendance_policy = attendance_policy
        self.attendance_lifecycle = attendance_lifecycle

    def mark_attendance(
        self,
        student_id: str | ObjectId,
        class_id: str | ObjectId,
        status: AttendanceStatus | str,
        teacher_id: str | ObjectId,
        record_date: date_type | None = None,
        *,
        prevent_duplicate: bool = True,
    ) -> AttendanceRecord:
        can = self.attendance_policy.can_create(
            student_id=self._oid(student_id),
            class_id=self._oid(class_id),
            teacher_id=self._oid(teacher_id),
            record_date=record_date,
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

        record = self.attendance_factory.create_record(
            student_id=student_id,
            class_id=class_id,
            status=status,
            teacher_id=teacher_id,
            record_date=record_date,
        )
        return self.attendance_repo.insert(record)

    def change_attendance_status(
        self,
        attendance_id: str | ObjectId,
        new_status: AttendanceStatus | str,
    ) -> Optional[AttendanceRecord]:
        oid = self._oid(attendance_id)

        can = self.attendance_policy.can_update(oid)
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

        existing.change_status(new_status)
        return self.attendance_repo.update(existing)

    def soft_delete_attendance(
        self,
        attendance_id: str | ObjectId,
        actor_id: str | ObjectId,
    ) -> int:
        """
        Soft delete attendance record (recommended default).
        """
        oid = self._oid(attendance_id)
        res = self.attendance_lifecycle.soft_delete_attendance(
            attendance_id=oid,
            actor_id=self._oid(actor_id),
        )
        return int(res.modified_count)

    def restore_attendance(
        self,
        attendance_id: str | ObjectId,
        actor_id: str | ObjectId | None = None,
    ) -> int:
        """
        Restore a soft-deleted attendance record.
        """
        oid = self._oid(attendance_id)
        res = self.attendance_lifecycle.restore_attendance(
            attendance_id=oid,
            actor_id=self._oid(actor_id) if actor_id else None,
        )
        return int(res.modified_count)

    def hard_delete_attendance(
        self,
        attendance_id: str | ObjectId,
        actor_id: str | ObjectId,
    ) -> int:
        """
        Hard delete (admin-only in most systems).
        """
        oid = self._oid(attendance_id)
        res = self.attendance_lifecycle.hard_delete_attendance(
            attendance_id=oid,
            actor_id=self._oid(actor_id),
        )
        return int(res.deleted_count)

    def get_attendance_by_id(self, attendance_id: str | ObjectId) -> Optional[AttendanceRecord]:
        return self.attendance_repo.find_by_id(self._oid(attendance_id))