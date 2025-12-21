from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

from app.contexts.shared.enum.roles import SystemRole
from app.contexts.iam.domain.iam import IAMStatus
from .common_validators import strip_or_none, strip, oid_to_str


class AdminCreateUserSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    role: SystemRole
    created_by: Optional[str] = None

    @field_validator("username", mode="before")
    @classmethod
    def _username(cls, v):
        return strip_or_none(v)

    @field_validator("email", mode="before")
    @classmethod
    def _email(cls, v):
        return strip(v)

    @field_validator("created_by", mode="before")
    @classmethod
    def _created_by(cls, v):
        return oid_to_str(v)


class AdminSetUserStatusSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    status: IAMStatus


class AdminUpdateUserSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)

    role: Optional[SystemRole] = None

    @field_validator("username", mode="before")
    @classmethod
    def _username(cls, v):
        return strip_or_none(v)

    @field_validator("email", mode="before")
    @classmethod
    def _email(cls, v):
        return strip(v) if v else None

