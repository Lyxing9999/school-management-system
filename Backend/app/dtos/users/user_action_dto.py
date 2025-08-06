from pydantic import BaseModel, Field , RootModel , ConfigDict
from app.utils.pyobjectid import PyObjectId
from app.utils.objectid import ObjectId
from typing import List
from app.enum.enums import Role

class UserResponseDataDTO(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    username: str | None
    role: Role
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

class UserUpdateData(BaseModel):
    username: str | None = Field(None, description="The username of the user")
    email: str | None = Field(None, description="The email of the user")
    password: str | None = Field(None, description="The password of the user")




