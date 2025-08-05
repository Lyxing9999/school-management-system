

from pydantic import BaseModel , Field
from typing import List
from app.utils.pyobjectid import PyObjectId


class AdminClassCreateDataDTO(BaseModel):
    created_by_admin_id: PyObjectId = Field(..., description="ObjectId of the admin who created the class")
    teacher_id: PyObjectId = Field(..., description="ObjectId of the teacher assigned to the class")
    course_code: str = Field(..., description="Course code, e.g. MATH101")
    course_title: str = Field(..., description="Course title")
    schedule: List[ScheduleItem] = Field(..., description="List of scheduled days and times")
    telegram_link: str | None = Field(..., description="Telegram group link for the class")
    zoom_link: str | None = Field(..., description="Zoom meeting link (optional)")
    hybrid: bool  = Field(..., description="Is class hybrid (online + offline)")


    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str},
        "populate_by_name": True,
        "extra": "forbid",
    }

