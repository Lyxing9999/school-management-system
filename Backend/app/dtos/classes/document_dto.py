from typing import List
from pydantic import BaseModel, Field
from app.utils.pyobjectid import PyObjectId



class ScheduleItemDBDTO(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str


class ClassDBDTO(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    teacher_id: PyObjectId
    course_code: str
    course_title: str
    schedule: List[ScheduleItemDBDTO]
    telegram_link: str | None
    zoom_link: str | None
    hybrid: bool
    created_by: PyObjectId | None = Field(alias="created_by_admin_id", default=None)
    updated_by: PyObjectId | None = Field(alias="updated_by_admin_id", default=None)
    deleted_by: PyObjectId | None = Field(alias="deleted_by_admin_id", default=None)




