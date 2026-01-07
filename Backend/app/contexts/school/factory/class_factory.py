from __future__ import annotations
from typing import Iterable
from bson import ObjectId
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.school.domain.class_section import ClassSection, ClassSectionStatus
from app.contexts.school.errors.class_exceptions import (
    ClassNameAlreadyExistsException,
    TeacherOverClassLoadException,
)


class ClassFactory:
    def __init__(self, class_read_model, teacher_read_model):
        self.class_read_model = class_read_model
        self.teacher_read_model = teacher_read_model

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def create_class(
        self,
        name: str,
        homeroom_teacher_id: str | ObjectId | None = None,
        subject_ids: Iterable[str | ObjectId] | None = None,
        max_students: int | None = None,
        status: ClassSectionStatus | str = ClassSectionStatus.ACTIVE,
    ) -> ClassSection:
        clean_name = name.strip()
        if self.class_read_model.get_by_name(clean_name):
            raise ClassNameAlreadyExistsException(clean_name)

        homeroom_teacher_oid = self._normalize_id(homeroom_teacher_id) if homeroom_teacher_id is not None else None

        subject_oids = list({self._normalize_id(sid) for sid in (subject_ids or [])})

        if homeroom_teacher_oid is not None:
            max_load = self.teacher_read_model.get_max_class_load(homeroom_teacher_oid)
            if max_load is not None:
                current_load = self.teacher_read_model.count_classes_for_teacher(homeroom_teacher_oid)
                if current_load >= max_load:
                    raise TeacherOverClassLoadException(homeroom_teacher_oid, max_load)

        return ClassSection(
            name=clean_name,
            homeroom_teacher_id=homeroom_teacher_oid,
            subject_ids=subject_oids,
            max_students=max_students,
            status=status,
        )