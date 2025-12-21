from typing import Optional
from bson import ObjectId as BsonObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.contexts.shared.enum.roles import SystemRole

def _oid_to_str(v: BsonObjectId | str | None) -> str | None:
    if v is None:
        return None
    if isinstance(v, BsonObjectId):
        return str(v)
    return v


def _strip_or_none(v):
    """
    Normalize strings:
    - trim whitespace
    - convert "" -> None (useful for optional fields coming from UI)
    """
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


class StaffCreateSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    staff_id: str = Field(..., min_length=1)
    staff_name: str = Field(..., min_length=1)
    role: SystemRole = SystemRole.TEACHER

    user_id: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    created_by: Optional[str] = None

    @field_validator("user_id", "created_by", mode="before")
    @classmethod
    def normalize_object_ids(cls, v):
        return _strip_or_none(_oid_to_str(v))

    @field_validator("staff_id", "staff_name", "phone_number", "address", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class StaffUpdateSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    staff_id: Optional[str] = None
    staff_name: Optional[str] = None
    role: Optional[SystemRole] = None

    phone_number: Optional[str] = None
    address: Optional[str] = None

    @field_validator("staff_id", "staff_name", "phone_number", "address", mode="before")
    @classmethod
    def strip_optional_strings(cls, v):
        return _strip_or_none(v)