# app/models/user_model.py
from typing import ClassVar, Optional
from pydantic import BaseModel, Field  # type: ignore
from datetime import datetime, timezone
from app.utils.pyobjectid import PyObjectId 
from app.enums.roles import Role
from app.utils.objectid import ObjectId  # type: ignore


class UserModel(BaseModel):
    _collection_name: ClassVar[str] = "users"
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    role: Role = Role.STUDENT
    username: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "use_enum_values": True,
        "from_attributes": True,
        "extra": "allow",

        
        "json_encoders": {
            ObjectId: str,
            PyObjectId: str,
            datetime: lambda dt: dt.isoformat(),  
        },
     
    }

    def to_dict(self, include_password: bool = False) -> dict:
        data = self.model_dump(exclude_none=True)
        if not include_password:
            data.pop("password", None)
        return data