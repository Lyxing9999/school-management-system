from typing import Optional
from pydantic import BaseModel, Field
from datetime import time
from app.utils.pyobjectid import PyObjectId



class ScheduleItemModel(BaseModel):
    _collection_name = "schedule"
    
        
    id: Optional[PyObjectId] = Field(None, alias="_id")
    location: Optional[str] = None
    shift: Optional[str] = None  # keep optional
    start_time: time = Field(..., description="Format: HH:MM")
    end_time: time = Field(..., description="Format: HH:MM")
    room: Optional[str] = None   # make room optional

    model_config = {
        "extra": "allow",
        "from_attributes": True,
        "use_enum_values": True,
    }