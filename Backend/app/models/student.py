from datetime import datetime, timezone
from pydantic import BaseModel, Field  # type: ignore
from typing import Optional, List, Dict, ClassVar
from app.enums.status import AttendanceStatus
from app.utils.objectid import ObjectId # type: ignore
from app.utils.pyobjectid import PyObjectId
class StudentInfoModel(BaseModel):
    student_id: str
    grade: Optional[int] = 0
    class_ids: List[str] = Field(default_factory=list)
    major: Optional[str] = None
    birth_date: Optional[datetime] = None
    batch: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    attendance_record: Dict[str, AttendanceStatus] = Field(default_factory=dict)
    courses_enrolled: List[str] = Field(default_factory=list)
    scholarships: List[str] = Field(default_factory=list)
    current_gpa: float = 0.0
    remaining_credits: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create_minimal(cls, **overrides):
        data = {
            "student_id": "",
            "grade": None,
            "class_ids": [],
            "major": None,
            "birth_date": None,
            "batch": None,
            "address": None,
            "phone_number": None,
            "email": None,
            "attendance_record": {},
            "courses_enrolled": [],
            "scholarships": [],
            "current_gpa": 0.0,
            "remaining_credits": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
        }
        data.update(overrides)
        return cls(**data)
        


    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
    }

class StudentModel(BaseModel):
    _collection_name: ClassVar[str] = "student" 
    
    id: Optional[PyObjectId] = Field(None, alias="_id")
    student_info: StudentInfoModel
    
    @classmethod
    def create_minimal(cls, _id: PyObjectId, **overrides):
        student_info = StudentInfoModel.create_minimal()
        data = {
            "_id": _id,
            "student_info": student_info,
        }
        data.update(overrides)
        return cls(**data)
    
    model_config = {
        "extra": "allow",
        "from_attributes": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }