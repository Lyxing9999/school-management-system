from bson import ObjectId
from pydantic import BaseModel, Field , RootModel, ConfigDict
from typing import List
from app.utils.pyobjectid import PyObjectId


class UserDBDTO(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str | None = Field(default=None)
    role: str
    email: str | None = Field(default=None)
    password: str
    created_by: PyObjectId | None = Field(alias="created_by_admin_id", default=None)
    updated_by: PyObjectId | None = Field(alias="updated_by_admin_id", default=None)
    deleted_by: PyObjectId | None = Field(alias="deleted_by_admin_id", default=None)

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "extra": "forbid",
        "populate_by_name": True, 
    }


# Response DTO for API Output
class UserResponseDataDTO(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    username: str | None
    role: str
    email: str | None
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "extra": "ignore",
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
    }

class UserResponseDataDTOList(RootModel[List[UserResponseDataDTO]]):
    model_config = ConfigDict(from_attributes=True)