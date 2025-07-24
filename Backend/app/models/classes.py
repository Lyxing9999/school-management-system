from datetime import datetime, timezone
from typing import  List, ClassVar
from pydantic import BaseModel, Field, HttpUrl  # type: ignore
from app.models.schedule import ScheduleItemModel  # type: ignore
from app.utils.objectid import ObjectId # type: ignore
from app.utils.pyobjectid import PyObjectId

class ClassInfoModel(BaseModel):
    course_code: str
    course_title: str
    lecturer: str
    email: str | None = None
    phone_number: str
    hybrid: bool = False
    schedule: List[ScheduleItemModel] | None = None
    credits: int | None = 0
    link_telegram: HttpUrl |  None = None 
    department: str | None = ""
    description: str | None = None
    year: int | None = Field(default_factory=lambda: datetime.now().year)


class ClassesModel(BaseModel):
    _collection_name: ClassVar[str] = "classes"
    
    id: PyObjectId | None = Field(default=None, alias="_id")
    class_info: ClassInfoModel | None = None 
    created_by: str | ObjectId | None = None
    students_enrolled: List[str] = Field(default_factory=list) 
    max_students: int | None = 30 
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            PyObjectId: str,
            datetime: lambda dt: dt.isoformat(),   
            HttpUrl: str                        
        }
    }