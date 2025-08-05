from bson import ObjectId
from pydantic import Field
from app.enum.enums import Role
from app.schemas.users.user_update_schema import UserUpdateSchema
from app.utils.pyobjectid import PyObjectId
from app.schemas.users.user_register_schema  import UserRegisterSchema

class AdminCreateUserSchema(UserRegisterSchema):
    role: Role = Field(Role.STUDENT, description="Role assigned to the new user")
    created_by: ObjectId = Field(..., description="The admin who created the user", alias="created_by_admin_id")
    model_config = {
        **UserRegisterSchema.model_config,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            PyObjectId: str,
            ObjectId: str
        },
    }


class AdminUpdateUserSchema(UserUpdateSchema):
    role: Role | None = Field(None, description="Role assigned to the user")
    password: str | None = Field(None, min_length=6, description="The password of the user")
    updated_by: ObjectId = Field(..., alias="updated_by_admin_id", description="The admin who updated the user")

    model_config = {
        **UserUpdateSchema.model_config,
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
    }

