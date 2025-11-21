# app/contexts/school/factory/grade_factory.py

from __future__ import annotations
from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.errors.grade_exceptions import (
    NotSubjectTeacherException,
    StudentNotEnrolledForSubjectException,
)


class GradeFactory:
    """
    Factory for creating GradeRecord with domain-level business checks.

    Responsibilities:
    - Ensure teacher is allowed to grade this subject/class
    - Ensure student is enrolled in the class/subject
    - Delegate score validation to domain
    """

    def __init__(
        self,
        class_read_model,
        subject_read_model,
        enrollment_read_model,
        teacher_assignment_read_model,
    ):
        """
        :param class_read_model: e.g. get_by_id(class_id)
        :param subject_read_model: e.g. get_by_id(subject_id)
        :param enrollment_read_model: e.g. is_student_enrolled(student_id, class_id)
        :param teacher_assignment_read_model: e.g. can_teacher_grade(teacher_id, class_id, subject_id)
        """
        self.class_read_model = class_read_model
        self.subject_read_model = subject_read_model
        self.enrollment_read_model = enrollment_read_model
        self.teacher_assignment_read_model = teacher_assignment_read_model

    def create_grade(
        self,
        student_id: str | ObjectId,
        subject_id: str | ObjectId,
        score: float,
        type: GradeType | str,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId | None = None,
        term: str | None = None,
    ) -> GradeRecord:
        # Normalize IDs
        student_obj_id = student_id if isinstance(student_id, ObjectId) else ObjectId(student_id)
        subject_obj_id = subject_id if isinstance(subject_id, ObjectId) else ObjectId(subject_id)
        teacher_obj_id = teacher_id if isinstance(teacher_id, ObjectId) else ObjectId(teacher_id)
        class_obj_id: ObjectId | None = None
        if class_id is not None:
            class_obj_id = class_id if isinstance(class_id, ObjectId) else ObjectId(class_id)

        # 1. Optional: verify subject/class exist
        subject_doc = self.subject_read_model.get_by_id(subject_obj_id)
        if not subject_doc:
            raise ValueError(f"Subject {subject_obj_id} not found")

        if class_obj_id is not None:
            class_doc = self.class_read_model.get_by_id(class_obj_id)
            if not class_doc:
                raise ValueError(f"Class {class_obj_id} not found")

        # 2. Check teacher can grade this subject/class
        if class_obj_id is not None:
            if not self.teacher_assignment_read_model.can_teacher_grade(
                teacher_obj_id,
                class_obj_id,
                subject_obj_id,
            ):
                raise NotSubjectTeacherException(teacher_obj_id, subject_obj_id, class_obj_id)

        # 3. Check student enrollment (if class is specified)
        if class_obj_id is not None:
            if not self.enrollment_read_model.is_student_enrolled(student_obj_id, class_obj_id):
                raise StudentNotEnrolledForSubjectException(
                    student_obj_id, subject_obj_id, class_obj_id
                )

        # 4. Create domain model (GradeRecord will validate score and type)
        return GradeRecord(
            student_id=student_obj_id,
            subject_id=subject_obj_id,
            score=score,
            type=type,
            class_id=class_obj_id,
            teacher_id=teacher_obj_id,
            term=term,
        )