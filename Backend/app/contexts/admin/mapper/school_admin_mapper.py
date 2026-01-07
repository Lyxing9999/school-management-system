from __future__ import annotations
from typing import List

from app.contexts.school.domain.schedule import ScheduleSlot
from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.domain.subject import Subject

from app.contexts.admin.data_transfer.responses import (
    AdminSubjectDataDTO,
    AdminScheduleSlotDataDTO,
    AdminSubjectListDTO,
    AdminScheduleListDTO,
    AdminClassDataDTO,
)

class SchoolAdminMapper:
    # ========== CLASS ==========

    @staticmethod
    def class_to_dto(section: ClassSection) -> AdminClassDataDTO:
        """Domain ClassSection -> AdminClassDataDTO"""
        return AdminClassDataDTO(
            id=str(section.id),
            name=section.name,
            homeroom_teacher_id=str(section.homeroom_teacher_id) if section.homeroom_teacher_id else None,
            enrolled_count=int(section.enrolled_count or 0),
            max_students=section.max_students,
            status=section.status.value if hasattr(section.status, "value") else section.status,
            subject_ids=[str(sid) for sid in section.subject_ids],
            subject_count=len(section.subject_ids),
            homeroom_teacher_name=None,
            subject_labels=[],
            lifecycle=section.lifecycle,
        )

    @staticmethod
    def class_doc_to_dto(doc: dict) -> AdminClassDataDTO:
        """Raw Mongo dict -> AdminClassDataDTO (read-model output)"""
        subject_ids = doc.get("subject_ids") or []
        return AdminClassDataDTO(
            id=str(doc["_id"]),
            name=doc.get("name", ""),
            homeroom_teacher_id=str(doc["homeroom_teacher_id"]) if doc.get("homeroom_teacher_id") else None,
            enrolled_count=int(doc.get("enrolled_count") or 0),
            max_students=doc.get("max_students"),
            status=doc.get("status"),
            subject_ids=[str(sid) for sid in subject_ids],
            subject_count=len(subject_ids),
            homeroom_teacher_name=None,
            subject_labels=[],
            lifecycle=doc.get("lifecycle"),
        )

    @staticmethod
    def class_list_to_dto(docs: List[dict]) -> List[AdminClassDataDTO]:
        """List[dict] -> List[AdminClassDataDTO]"""
        return [SchoolAdminMapper.class_doc_to_dto(doc) for doc in docs]

    # ========== SUBJECT ==========

    @staticmethod
    def subject_to_dto(subject: Subject) -> AdminSubjectDataDTO:
        return AdminSubjectDataDTO(
            id=str(subject.id),
            name=subject.name,
            code=subject.code,
            description=subject.description,
            allowed_grade_levels=list(subject.allowed_grade_levels),
            is_active=subject.is_active,
            lifecycle=subject.lifecycle,
        )

    @staticmethod
    def subject_doc_to_dto(doc: dict) -> AdminSubjectDataDTO:
        return AdminSubjectDataDTO(
            id=str(doc["_id"]),
            name=doc["name"],
            code=doc["code"],
            description=doc.get("description"),
            allowed_grade_levels=list(doc.get("allowed_grade_levels", [])),
            is_active=doc.get("is_active", True),
            lifecycle=doc.get("lifecycle"),
        )

    @staticmethod
    def subject_list_to_dto(docs: List[dict]) -> AdminSubjectListDTO:
        return AdminSubjectListDTO(items=[SchoolAdminMapper.subject_doc_to_dto(doc) for doc in docs])

    # ========== SCHEDULE ==========

    @staticmethod
    def schedule_slot_to_dto(slot: ScheduleSlot) -> AdminScheduleSlotDataDTO:
        return AdminScheduleSlotDataDTO(
            id=str(slot.id),
            class_id=str(slot.class_id),
            teacher_id=str(slot.teacher_id),
            day_of_week=int(slot.day_of_week),
            start_time=slot.start_time,
            end_time=slot.end_time,
            room=slot.room,
            lifecycle=slot.lifecycle,
        )

    @staticmethod
    def schedule_slot_doc_to_dto(doc: dict) -> AdminScheduleSlotDataDTO:
        return AdminScheduleSlotDataDTO(
            id=str(doc["_id"]),
            class_id=str(doc["class_id"]),
            teacher_id=str(doc["teacher_id"]),
            day_of_week=doc["day_of_week"],
            start_time=doc["start_time"],
            end_time=doc["end_time"],
            room=doc.get("room"),
            lifecycle=doc.get("lifecycle"),
        )

    @staticmethod
    def schedule_list_to_dto(slots: List[ScheduleSlot]) -> AdminScheduleListDTO:
        return AdminScheduleListDTO(items=[SchoolAdminMapper.schedule_slot_to_dto(s) for s in slots])