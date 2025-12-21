from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.contexts.shared.enum.roles import SystemRole
from app.contexts.staff.data_transfer.requests import StaffUpdateSchema 
from .common_validators import strip, strip_or_none, oid_to_str
from .iam_schemas import AdminCreateUserSchema

class AdminCreateStaffSchema(AdminCreateUserSchema):
    """
    Staff profile fields only (staff collection).
    If you also want to create IAM user, use AdminCreateStaffWithUserSchema below.
    """
    model_config = ConfigDict(extra="ignore")

    staff_id: str = Field(..., min_length=1)
    staff_name: str = Field(..., min_length=1)
    phone_number: Optional[str] = None
    user_id: Optional[str] = None
    address: Optional[str] = None
    created_by: Optional[str] = None



    @field_validator("staff_id", "staff_name", mode="before")
    @classmethod
    def _strip_required(cls, v):
        return strip(v)

    @field_validator("phone_number", "address", mode="before")
    @classmethod
    def _strip_optional(cls, v):
        return strip_or_none(v)

    @field_validator("user_id", "created_by", mode="before")
    @classmethod
    def _oids(cls, v):
        return oid_to_str(v)




class AdminUpdateStaffSchema(StaffUpdateSchema):
    model_config = ConfigDict(extra="ignore")