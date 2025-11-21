# app/contexts/school/factory/class_factory.py

from __future__ import annotations
from typing import Iterable
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.errors.class_exceptions import (
    ClassNameAlreadyExistsException,
    TeacherOverClassLoadException,
)


class ClassFactory:
    """
    Factory for creating ClassSection aggregates with validation.

    Responsibilities:
    - Validate class name uniqueness (optional, but common)
    - Validate teacher max class load (if teacher is assigned)
    - Initialize ClassSection domain model
    """

    def __init__(self, class_read_model, teacher_read_model):
        """
        :param class_read_model: provides read-side methods like:
            - get_by_name(name) -> dict | None
        :param teacher_read_model: provides:
            - count_classes_for_teacher(teacher_id) -> int
            - get_max_class_load(teacher_id) -> int | None
        """
        self.class_read_model = class_read_model
        self.teacher_read_model = teacher_read_model

    def create_class(
        self,
        name: str,
        teacher_id: str | ObjectId | None = None,
        subject_ids: Iterable[str | ObjectId] | None = None,
        max_students: int | None = None,
    ) -> ClassSection:
        # 1. Validate name uniqueness
        if self.class_read_model.get_by_name(name):
            raise ClassNameAlreadyExistsException(name)

        # 2. Normalize IDs
        teacher_obj_id: ObjectId | None = None
        if teacher_id is not None:
            teacher_obj_id = teacher_id if isinstance(teacher_id, ObjectId) else ObjectId(teacher_id)

        normalized_subject_ids: list[ObjectId] = []
        for sid in subject_ids or []:
            normalized_subject_ids.append(sid if isinstance(sid, ObjectId) else ObjectId(sid))

        # 3. Optional: check teacher load
        if teacher_obj_id is not None:
            max_load = self.teacher_read_model.get_max_class_load(teacher_obj_id)
            if max_load is not None:
                current_load = self.teacher_read_model.count_classes_for_teacher(teacher_obj_id)
                if current_load >= max_load:
                    raise TeacherOverClassLoadException(teacher_obj_id, max_load)

        # 4. Create domain object
        return ClassSection(
            name=name,
            teacher_id=teacher_obj_id,
            student_ids=[],
            subject_ids=normalized_subject_ids,
            max_students=max_students,
        )