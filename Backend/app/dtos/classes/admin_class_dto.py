from pydantic import BaseModel, Field
from typing import List
from app.utils.pyobjectid import PyObjectId
from app.dtos.classes.document_dto import ScheduleItemDBDTO

class AdminClassCreateDataDTO(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    created_by: PyObjectId = Field(..., description="ObjectId of the admin who created the class", alias="created_by_admin_id")
    teacher_id: PyObjectId = Field(..., description="ObjectId of the teacher assigned to the class")
    course_code: str = Field(..., description="Course code, e.g. MATH101")
    course_title: str = Field(..., description="Course title")
    schedule: List[ScheduleItemDBDTO] = Field(..., description="List of scheduled days and times")
    telegram_link: str | None = Field(None, description="Telegram group link for the class")
    zoom_link: str | None = Field(None, description="Zoom meeting link (optional)")
    hybrid: bool = Field(default=False, description="Is class hybrid (online + offline)")

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str},
        "populate_by_name": True,
        "extra": "forbid",
    }

class AdminClassUpdateDataDTO(AdminClassCreateDataDTO):
    updated_by: PyObjectId = Field(..., description="ObjectId of the admin who updated the class", alias="updated_by_admin_id")



class AdminClassDeleteDataDTO(BaseModel):
    deleted_by: PyObjectId = Field(..., description="ObjectId of the admin who deleted the class", alias="deleted_by_admin_id")
    


