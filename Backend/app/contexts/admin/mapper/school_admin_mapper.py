# app/contexts/admin/mapper/school_admin_mapper.py

from __future__ import annotations
from typing import List

from bson import ObjectId

from app.contexts.school.domain.schedule import ScheduleSlot
from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.domain.subject import Subject

from app.contexts.admin.data_transfer.response import (
    AdminClassDataDTO,
    AdminSubjectDataDTO,
    AdminScheduleSlotDataDTO,
    AdminSubjectListDTO,
    AdminScheduleListDTO,
    AdminClassListDTO,
)


class SchoolAdminMapper:
    # ========== CLASS ==========

    @staticmethod
    def class_to_dto(section: ClassSection) -> AdminClassDataDTO:
        """Domain ClassSection -> DTO"""
        return AdminClassDataDTO(
            id=str(section.id),
            name=section.name,
            teacher_id=str(section.teacher_id) if section.teacher_id else None,
            student_ids=[str(sid) for sid in section.student_ids],
            subject_ids=[str(sid) for sid in section.subject_ids],
            max_students=section.max_students,
            created_at=section.created_at,
            updated_at=section.updated_at,
            deleted=section.deleted,
        )

    @staticmethod
    def class_doc_to_dto(doc: dict) -> AdminClassDataDTO:
        """Raw Mongo dict -> DTO (used by read models)."""
        return AdminClassDataDTO(
            id=str(doc["_id"]),
            name=doc["name"],
            teacher_id=str(doc["teacher_id"]) if doc.get("teacher_id") else None,
            student_ids=[str(sid) for sid in doc.get("student_ids", [])],
            subject_ids=[str(sid) for sid in doc.get("subject_ids", [])],
            max_students=doc.get("max_students"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            deleted=doc.get("deleted", False),
        )

    @staticmethod
    def class_list_to_dto(docs: List[dict]) -> AdminClassListDTO:
        """
        NOTE: this takes *dicts* from ClassReadModel, not domain objects.
        """
        items = [
            SchoolAdminMapper.class_doc_to_dto(doc)
            for doc in docs
        ]
        return AdminClassListDTO(items=items)

    # ========== SUBJECT ==========

    @staticmethod
    def subject_to_dto(subject: Subject) -> AdminSubjectDataDTO:
        """Domain Subject -> DTO"""
        return AdminSubjectDataDTO(
            id=str(subject.id),
            name=subject.name,
            code=subject.code,
            description=subject.description,
            allowed_grade_levels=list(subject.allowed_grade_levels),
            is_active=subject.is_active,
            created_at=subject.created_at,
            updated_at=subject.updated_at,
        )

    @staticmethod
    def subject_doc_to_dto(doc: dict) -> AdminSubjectDataDTO:
        """Raw Mongo dict -> DTO (used by read models)."""
        return AdminSubjectDataDTO(
            id=str(doc["_id"]),
            name=doc["name"],
            code=doc["code"],
            description=doc.get("description"),
            allowed_grade_levels=list(doc.get("allowed_grade_levels", [])),
            is_active=doc.get("is_active", True),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    @staticmethod
    def subject_list_to_dto(docs: List[dict]) -> AdminSubjectListDTO:
        items = [
            SchoolAdminMapper.subject_doc_to_dto(doc)
            for doc in docs
        ]
        return AdminSubjectListDTO(items=items)

    # ========== SCHEDULE ==========

    @staticmethod
    def schedule_slot_to_dto(slot: ScheduleSlot) -> AdminScheduleSlotDataDTO:
        """Domain ScheduleSlot -> DTO"""
        return AdminScheduleSlotDataDTO(
            id=str(slot.id),
            class_id=str(slot.class_id),
            teacher_id=str(slot.teacher_id),
            day_of_week=int(slot.day_of_week),
            start_time=slot.start_time,
            end_time=slot.end_time,
            room=slot.room,
            created_at=slot.created_at,
            updated_at=slot.updated_at,
        )

    @staticmethod
    def schedule_slot_doc_to_dto(doc: dict) -> AdminScheduleSlotDataDTO:
        """Raw Mongo dict -> DTO (used by read models)."""
        return AdminScheduleSlotDataDTO(
            id=str(doc["_id"]),
            class_id=str(doc["class_id"]),
            teacher_id=str(doc["teacher_id"]),
            day_of_week=doc["day_of_week"],
            start_time=doc["start_time"],   
            end_time=doc["end_time"],
            room=doc.get("room"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    @staticmethod
    def schedule_list_to_dto(slots: List[ScheduleSlot]) -> AdminScheduleListDTO:
        """Domain list[ScheduleSlot] -> list DTO"""
        items = [
            SchoolAdminMapper.schedule_slot_to_dto(slot)
            for slot in slots
        ]
        return AdminScheduleListDTO(items=items)