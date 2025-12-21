from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common_validators import strip, strip_or_none


class AdminCreateSubjectSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    description: Optional[str] = None
    allowed_grade_levels: List[int] = Field(default_factory=list)

    @field_validator("name", "code", mode="before")
    @classmethod
    def _strip_required(cls, v):
        return strip(v)

    @field_validator("description", mode="before")
    @classmethod
    def _desc(cls, v):
        return strip_or_none(v)


class AdminUpdateSubjectSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    allowed_grade_levels: Optional[List[int]] = None

    @field_validator("name", "code", "description", mode="before")
    @classmethod
    def _strip_optional(cls, v):
        return strip_or_none(v)