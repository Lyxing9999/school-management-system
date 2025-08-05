from typing import Optional
from pydantic import Field , BaseModel , model_validator
from app.error.exceptions import BadRequestError, ErrorSeverity, ErrorCategory
from app.utils.pyobjectid import PyObjectId
import re
from typing import List
from app.utils.objectid import ObjectId


class ScheduleItem(BaseModel):
    day_of_week: str = Field(..., description="Day of the week e.g., Monday")
    start_time: str = Field(..., description="Class start time, e.g., 08:00")
    end_time: str = Field(..., description="Class end time, e.g., 09:30")

    @model_validator(mode='before')
    def validate_schedule_item(cls, values):
        day = values.get("day_of_week")
        start = values.get("start_time")
        end = values.get("end_time")

        valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
        if day not in valid_days:
            raise BadRequestError(
                message="day_of_week must be a valid weekday name",
                status_code=400,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.VALIDATION,
                hint="Use full weekday names, e.g., Monday, Tuesday, ...",
                received_value=day,
                recoverable=True,
            )

        time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        if not re.match(time_pattern, start or ""):
            raise BadRequestError(
                message="start_time must be in HH:MM 24-hour format",
                status_code=400,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.VALIDATION,
                received_value=start,
            )
        if not re.match(time_pattern, end or ""):
            raise BadRequestError(
                message="end_time must be in HH:MM 24-hour format",
                status_code=400,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.VALIDATION,
                received_value=end,
            )
        return values


class ClassCreateSchema(BaseModel):
    teacher_id: PyObjectId = Field(..., description="ObjectId of assigned teacher")
    course_code: str = Field(..., max_length=20, description="Course code, e.g. MATH101")
    course_title: str = Field(..., max_length=100, description="Course title")
    schedule: List[ScheduleItem] = Field(..., description="List of scheduled days and times")
    telegram_link: Optional[str] = Field(None, description="Telegram group link for the class")
    zoom_link: Optional[str] = Field(None, description="Zoom meeting link (optional)")
    hybrid: bool = Field(default=False, description="Is class hybrid (online + offline)")

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
    }




class ClassUpdateSchema(BaseModel):
    course_code: str | None = Field(None, max_length=20, description="Course code, e.g. MATH101")
    course_title: str | None = Field(None, max_length=100, description="Course title")
    teacher_id: PyObjectId | None = Field(None, description="ObjectId of assigned teacher")
    schedule: List[ScheduleItem] | None = Field(None, description="List of scheduled days and times")
    telegram_link: str | None = Field(None, description="Telegram group link for the class")
    zoom_link: str | None = Field(None, description="Zoom meeting link (optional)")
    hybrid: bool | None = Field(None, description="Is class hybrid (online + offline)")

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
    }