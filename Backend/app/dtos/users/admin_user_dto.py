
from app.utils.objectid import ObjectId
from pydantic import Field, RootModel
from app.dtos.users.user_response_dto import UserResponseDataDTO
from app.utils.pyobjectid import PyObjectId



class AdminCreateUserDataDTO(UserResponseDataDTO):
    created_by: PyObjectId | None = Field(alias="created_by_admin_id", default=None)

class AdminUpdateUserDataDTO(UserResponseDataDTO):
    updated_by: PyObjectId | None = Field(alias="updated_by_admin_id", default=None)

class AdminDeleteUserDataDTO(UserResponseDataDTO):
    deleted_by: PyObjectId | None = Field(alias="deleted_by_admin_id", default=None)

class AdminFindUserDataDTO(UserResponseDataDTO):
    created_by: PyObjectId | None = Field(alias="created_by_admin_id", default=None)
    updated_by: PyObjectId | None = Field(alias="updated_by_admin_id", default=None)
    deleted_by: PyObjectId | None = Field(alias="deleted_by_admin_id", default=None)

    model_config = {
        "from_attributes": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "arbitrary_types_allowed": True,
        "extra": "ignore",
        "populate_by_name": True, 
    }

class AdminFindUserDataListDTO(RootModel[list[AdminFindUserDataDTO]]):
    model_config = {"from_attributes": True}




