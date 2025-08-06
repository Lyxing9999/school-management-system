
from app.utils.objectid import ObjectId
from pydantic import Field, RootModel
from app.dtos.users.user_response_dto import UserResponseDataDTO
from app.utils.pyobjectid import PyObjectId



class AdminCreateUserDataDTO(UserResponseDataDTO):
    created_by: PyObjectId = Field(... ,alias="created_by_admin_id")

class AdminUpdateUserDataDTO(UserResponseDataDTO):
    updated_by: PyObjectId = Field(..., alias="updated_by_admin_id")

class AdminDeleteUserDataDTO(UserResponseDataDTO):
    deleted_by: PyObjectId = Field(..., alias="deleted_by_admin_id")

class AdminFindUserDataDTO(UserResponseDataDTO):
    created_by: PyObjectId = Field(..., alias="created_by_admin_id")
    updated_by: PyObjectId = Field(..., alias="updated_by_admin_id")
    deleted_by: PyObjectId = Field(..., alias="deleted_by_admin_id")

    model_config = {
        "from_attributes": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "arbitrary_types_allowed": True,
        "extra": "ignore",
        "populate_by_name": True, 
    }

class AdminFindUserDataListDTO(RootModel[list[AdminFindUserDataDTO]]):
    model_config = {"from_attributes": True}




