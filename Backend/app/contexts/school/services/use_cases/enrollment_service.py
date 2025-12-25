from __future__ import annotations

from typing import Optional
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.errors.class_exceptions import ClassNotFoundException, StudentAlreadyEnrolledException
from app.contexts.student.errors.student_exceptions import StudentNotFoundException

from ._base import OidMixin


class EnrollmentService(OidMixin):
    def __init__(self, *, class_repo, student_service_getter):
        self.class_repo = class_repo
        self._get_student_service = student_service_getter

    def enroll_student_to_class(self, class_id: str | ObjectId, student_id: str | ObjectId) -> ClassSection:
        class_oid = self._oid(class_id)
        student_oid = self._oid(student_id)

        section = self.class_repo.find_by_id(class_oid)
        if section is None:
            raise ClassNotFoundException(class_id)

        student_service = self._get_student_service()
        student = student_service.get_student_by_id(student_oid)
        if student is None:
            raise StudentNotFoundException(student_id)

        if student.current_class_id is not None:
            raise StudentAlreadyEnrolledException(
                student_id=student_oid,
                current_class_id=student.current_class_id,
                target_class_id=class_oid,
            )

        section.increment_enrollment()

        ok = self.class_repo.update(section)
        if not ok:
            raise ClassNotFoundException(class_id)

        try:
            student_service.join_class(class_id=class_oid, student_id=student_oid)
        except Exception:
            section.decrement_enrollment()
            self.class_repo.update(section)
            raise

        return section

    def unenroll_student_from_class(
        self,
        class_id: str | ObjectId,
        student_id: str | ObjectId,
    ) -> Optional[ClassSection]:
        class_oid = self._oid(class_id)
        student_oid = self._oid(student_id)

        section = self.class_repo.find_by_id(class_oid)
        if section is None:
            raise ClassNotFoundException(class_id)

        section.decrement_enrollment()
        self.class_repo.update(section)

        self._get_student_service().leave_class(student_id=student_oid)
        return section