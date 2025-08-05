from pydantic import Field, constr
from app.schemas.users.user_register_schema import UserRegisterSchema

class UserUpdateSchema(UserRegisterSchema):
    username: constr(min_length=3, max_length=20) | None = Field(None, description="The username of the user")
    email: str | None = Field(None, description="The email of the user")
    password: constr(min_length=6) | None = Field(None, description="The password of the user")

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "populate_by_name": True,
    }