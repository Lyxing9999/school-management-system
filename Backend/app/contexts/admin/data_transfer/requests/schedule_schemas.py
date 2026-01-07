from datetime import time
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.contexts.school.domain.schedule import DayOfWeek  
from .common_validators import oid_to_str, ensure_day_of_week_1_7, validate_time_range, strip_or_none


class AdminCreateScheduleSlotSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    class_id: str = Field(..., description="Class ObjectId as string")
    teacher_id: str = Field(..., description="Teacher ObjectId as string")
    day_of_week: DayOfWeek | int = Field(..., description="1=Mon .. 7=Sun")
    start_time: time
    end_time: time
    room: Optional[str] = None
    subject_id: Optional[str] = None

    @field_validator("class_id", "teacher_id", mode="before")
    @classmethod
    def _ids(cls, v):
        v = oid_to_str(v)
        if not v:
            raise ValueError("id is required")
        return v

    @field_validator("day_of_week", mode="before")
    @classmethod
    def _dow(cls, v: Any):
        return ensure_day_of_week_1_7(v)

    @field_validator("room", mode="before")
    @classmethod
    def _room(cls, v):
        return strip_or_none(v)

    @model_validator(mode="after")
    def _time_range(self):
        validate_time_range(self.start_time, self.end_time)
        return self


class AdminUpdateScheduleSlotSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    day_of_week: DayOfWeek | int
    start_time: time
    end_time: time
    room: Optional[str] = None
    subject_id: Optional[str] = None

    @field_validator("day_of_week", mode="before")
    @classmethod
    def _dow(cls, v: Any):
        return ensure_day_of_week_1_7(v)

    @field_validator("room", mode="before")
    @classmethod
    def _room(cls, v):
        return strip_or_none(v)

    @model_validator(mode="after")
    def _time_range(self):
        validate_time_range(self.start_time, self.end_time)
        return self


class AdminAssignScheduleSlotSubjectSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)
    
    subject_id: Optional[str] = None