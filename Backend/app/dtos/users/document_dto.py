from bson import ObjectId
from pydantic import BaseModel, Field 
from app.utils.pyobjectid import PyObjectId
from app.enum.enums import Role

class UserDBDTO(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str | None = Field(default=None)
    role: Role
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


