from pydantic import BaseModel, Field   # type: ignore
from datetime import datetime, timezone
from app.utils.pyobjectid import PyObjectId # type: ignore
from typing import ClassVar 

class CourseModel(BaseModel):
    _collection_name: ClassVar[str] = "courses"

    id: PyObjectId | None = Field(default_factory=lambda: PyObjectId(), alias="_id")
    course_code: str
    course_title: str
    credits: int | None = Field(default=0, ge=0)
    department: str | None = Field(default=None)
    description: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "extra": "allow",
        "populate_by_name": True,
        "from_attributes": True,
        "arbitrary_types_allowed": True, 
    }
