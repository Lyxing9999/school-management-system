
from __future__ import annotations

from bson import ObjectId

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.errors.class_exceptions import ClassNotFoundException
from app.contexts.school.errors.subject_exceptions import SubjectNotFoundException
from app.contexts.school.errors.grade_exceptions import InvalidTermException


class GradeFactory:
    """
    Factory for creating GradeRecord with domain-level business checks.

    Responsibilities:
    - Ensure teacher is allowed to grade this subject/class
    - Ensure student is enrolled in the class/subject
    - Delegate score/type/term validation to domain (GradeRecord)
    """

    def __init__(
        self,
        class_read_model,
        subject_read_model,
        teacher_assignment_read_model,
    ):
        self.class_read_model = class_read_model
        self.subject_read_model = subject_read_model
        self.teacher_assignment_read_model = teacher_assignment_read_model

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def _require_term(self, term: str) -> str:
        """
        Strong requirement at factory layer for clearer errors.
        Domain will still validate the format strictly.
        """
        if term is None:
            raise InvalidTermException(received_value=None, expected="YYYY-S1 or YYYY-S2")

        t = str(term).strip()
        if not t:
            raise InvalidTermException(received_value=term, expected="YYYY-S1 or YYYY-S2")

        return t

    def create_grade(
        self,
        student_id: str | ObjectId,
        subject_id: str | ObjectId,
        score: float,
        type: GradeType | str,
        teacher_id: str | ObjectId,
        *,
        term: str,  # REQUIRED now
        class_id: str | ObjectId | None = None,
    ) -> GradeRecord:
        # Normalize IDs
        student_obj_id = self._normalize_id(student_id)
        subject_obj_id = self._normalize_id(subject_id)
        teacher_obj_id = self._normalize_id(teacher_id)

        class_obj_id: ObjectId | None = None
        if class_id is not None:
            class_obj_id = self._normalize_id(class_id)

        # Require non-empty term early
        term = self._require_term(term)

        # 1) Verify subject/class exist
        subject_doc = self.subject_read_model.get_by_id(subject_obj_id)
        if not subject_doc:
            raise SubjectNotFoundException(subject_obj_id)

        if class_obj_id is not None:
            class_doc = self.class_read_model.get_by_id(class_obj_id)
            if not class_doc:
                raise ClassNotFoundException(class_obj_id)


        return GradeRecord(
            student_id=student_obj_id,
            subject_id=subject_obj_id,
            score=score,
            type=type,
            class_id=class_obj_id,
            teacher_id=teacher_obj_id,
            term=term,
        )