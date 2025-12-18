from __future__ import annotations
from typing import Iterable
from bson import ObjectId
from app.contexts.shared.model_converter import mongo_converter
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

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        """
        Convert incoming id to ObjectId using shared converter.
        """
        return mongo_converter.convert_to_object_id(id_)
    
    def create_class(
        self,
        name: str,
        teacher_id: str | ObjectId | None = None,
        subject_ids: Iterable[str | ObjectId] | None = None,
        max_students: int | None = None,
    ) -> ClassSection:

        if self.class_read_model.get_by_name(name):
            raise ClassNameAlreadyExistsException(name)
        
        teacher_obj_id: ObjectId | None = (
            self._normalize_id(teacher_id)
            if teacher_id is not None
            else None
        )

        normalized_subject_ids: list[ObjectId] = [
            self._normalize_id(sid)
            for sid in (subject_ids or [])
        ]
        
        if teacher_obj_id is not None:
            max_load = self.teacher_read_model.get_max_class_load(teacher_obj_id)
            if max_load is not None:
                current_load = self.teacher_read_model.count_classes_for_teacher(teacher_obj_id)
                if current_load >= max_load:
                    raise TeacherOverClassLoadException(teacher_obj_id, max_load)

        return ClassSection(
            name=name,
            teacher_id=teacher_obj_id,
            subject_ids=normalized_subject_ids,
            max_students=max_students,
        )