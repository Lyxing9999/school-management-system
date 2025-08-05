
from typing import List
from app.schemas.classes.class_create_schema import ScheduleItem
from pydantic import Field
from pydantic import BaseModel
from app.utils.pyobjectid import PyObjectId
from app.utils.objectid import ObjectId


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


    