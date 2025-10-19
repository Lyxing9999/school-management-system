from __future__ import annotations
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.contexts.schools.data_transfer.responses.subject_responses import SubjectBaseDataDTO
from app.contexts.schools.data_transfer.requests.subject_requests import SubjectCreateSchema


class SchoolSubject:
    """
    Represents a Subject in the school.
    A subject can exist independently of a class.
    Admin can assign teachers later.
    """

    def __init__(
        self,
        name: str,
        teacher_ids: Optional[List[ObjectId]] = None,
        id: Optional[ObjectId] = None,
        created_by: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted: bool = False
    ):
        self.id = id or ObjectId()
        self.name = name
        self.teacher_ids: List[ObjectId] = teacher_ids or []
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted

    # -------------------------
    # Factory Methods
    # -------------------------
    @classmethod
    def from_create_schema(cls, payload: SubjectCreateSchema, created_by: ObjectId) -> SchoolSubject:
        teacher_ids = getattr(payload, "teacher_ids", []) or []
        return cls(
            name=payload.name,
            teacher_ids=teacher_ids,
            created_by=created_by
        )

    @classmethod
    def to_domain(cls, data: dict) -> SchoolSubject:
        return cls(
            id=ObjectId(data["_id"]) if "_id" in data else None,
            name=data["name"],
            teacher_ids=[ObjectId(tid) for tid in data.get("teacher_ids", [])],
            created_by=ObjectId(data.get("created_by")) if data.get("created_by") else None,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted=data.get("deleted", False)
        )

    # -------------------------
    # Persistence
    # -------------------------
    def to_persistence_dict(self) -> dict:
        return {
            "_id": self.id,
            "name": self.name,
            "teacher_ids": self.teacher_ids,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted": self.deleted
        }

    @classmethod
    def from_persistence_dict(cls, data: dict) -> SchoolSubject:
        return cls.to_domain(data)

    # -------------------------
    # Business Methods
    # -------------------------
    def add_teacher(self, teacher_id: ObjectId):
        if teacher_id not in self.teacher_ids:
            self.teacher_ids.append(teacher_id)
            self.updated_at = datetime.utcnow()

    def remove_teacher(self, teacher_id: ObjectId):
        if teacher_id in self.teacher_ids:
            self.teacher_ids.remove(teacher_id)
            self.updated_at = datetime.utcnow()

    def set_teachers(self, teacher_ids: List[ObjectId]):
        self.teacher_ids = teacher_ids
        self.updated_at = datetime.utcnow()

    def mark_deleted(self):
        self.deleted = True
        self.updated_at = datetime.utcnow()

    # -------------------------
    # DTO
    # -------------------------
    def to_dto(self, teacher_names: Optional[List[str]] = None) -> SubjectBaseDataDTO:
        return SubjectBaseDataDTO(
            id=str(self.id),
            name=self.name,
            teacher_ids=[str(tid) for tid in self.teacher_ids],
            teacher_names=teacher_names or [],
            created_by=str(self.created_by) if self.created_by else None,
            deleted=self.deleted,
            created_at=self.created_at,
            updated_at=self.updated_at
        )