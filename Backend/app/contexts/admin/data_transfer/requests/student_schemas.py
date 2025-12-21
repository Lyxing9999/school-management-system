from datetime import date
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

from app.contexts.student.domain.student import Gender
from .common_validators import strip, strip_or_none, oid_to_str, parse_date_yyyy_mm_dd


class AdminCreateStudentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

    student_id_code: str = Field(..., min_length=1)
    first_name_kh: str
    last_name_kh: str
    first_name_en: str
    last_name_en: str

    gender: Gender
    dob: date
    current_grade_level: int = Field(..., ge=1, le=12)
    current_class_id: Optional[str] = None

    phone_number: Optional[str] = None
    address: Optional[dict] = None
    photo_url: Optional[str] = None
    guardians: List[Dict] = Field(default_factory=list)

    @field_validator(
        "username",
        "student_id_code",
        "first_name_kh", "last_name_kh",
        "first_name_en", "last_name_en",
        mode="before",
    )
    @classmethod
    def _strip_required(cls, v):
        return strip(v)

    @field_validator("dob", mode="before")
    @classmethod
    def _dob(cls, v):
        parsed = parse_date_yyyy_mm_dd(v)
        if parsed is None:
            raise ValueError("dob is required")
        return parsed

    @field_validator("current_class_id", mode="before")
    @classmethod
    def _class_id(cls, v):
        return oid_to_str(v)

    @field_validator("phone_number", "photo_url", mode="before")
    @classmethod
    def _strip_optional(cls, v):
        return strip_or_none(v)


class AdminUpdateStudentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    first_name_kh: Optional[str] = None
    last_name_kh: Optional[str] = None
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None

    gender: Optional[Gender] = None
    dob: Optional[date] = None

    current_grade_level: Optional[int] = Field(None, ge=1, le=12)
    current_class_id: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[dict] = None
    photo_url: Optional[str] = None
    guardians: Optional[list] = None

    @field_validator(
        "first_name_kh", "last_name_kh",
        "first_name_en", "last_name_en",
        mode="before",
    )
    @classmethod
    def _strip_names(cls, v):
        return strip_or_none(v)

    @field_validator("dob", mode="before")
    @classmethod
    def _dob(cls, v):
        return parse_date_yyyy_mm_dd(v)

    @field_validator("current_class_id", mode="before")
    @classmethod
    def _class_id(cls, v):
        return oid_to_str(v)

    @field_validator("phone_number", "photo_url", mode="before")
    @classmethod
    def _strip_optional(cls, v):
        return strip_or_none(v)