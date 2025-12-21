from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common_validators import strip, strip_or_none, oid_to_str, oids_to_str_list


class AdminCreateClassSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    name: str = Field(..., min_length=1)
    teacher_id: Optional[str] = None
    subject_ids: List[str] = Field(default_factory=list)
    max_students: Optional[int] = Field(default=None, ge=1)

    @field_validator("name", mode="before")
    @classmethod
    def _name(cls, v):
        return strip(v)

    @field_validator("teacher_id", mode="before")
    @classmethod
    def _teacher_id(cls, v):
        return oid_to_str(v)

    @field_validator("subject_ids", mode="before")
    @classmethod
    def _subject_ids(cls, v):
        return oids_to_str_list(v)


class AdminUpdateClassSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    name: Optional[str] = None
    teacher_id: Optional[str] = None
    subject_ids: Optional[List[str]] = None
    max_students: Optional[int] = Field(default=None, ge=1)

    @field_validator("name", mode="before")
    @classmethod
    def _name(cls, v):
        return strip_or_none(v)

    @field_validator("teacher_id", mode="before")
    @classmethod
    def _teacher_id(cls, v):
        return oid_to_str(v)

    @field_validator("subject_ids", mode="before")
    @classmethod
    def _subject_ids(cls, v):
        # allow None for patch updates
        return None if v is None else oids_to_str_list(v)


class AdminAssignTeacherToClassSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)
    teacher_id: str = Field(..., min_length=1)

    @field_validator("teacher_id", mode="before")
    @classmethod
    def _teacher_id(cls, v):
        v = oid_to_str(v)
        if not v:
            raise ValueError("teacher_id is required")
        return v


class AdminUnAssignTeacherToClassSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)
    teacher_id: str = Field(..., min_length=1)

    @field_validator("teacher_id", mode="before")
    @classmethod
    def _teacher_id(cls, v):
        v = oid_to_str(v)
        if not v:
            raise ValueError("teacher_id is required")
        return v


class AdminEnrollStudentToClassSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)
    student_id: str = Field(..., min_length=1)

    @field_validator("student_id", mode="before")
    @classmethod
    def _student_id(cls, v):
        v = oid_to_str(v)
        if not v:
            raise ValueError("student_id is required")
        return v