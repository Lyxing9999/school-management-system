
from pydantic import BaseModel, Field  # type: ignore
from app.enum.enums import Role
from app.utils.objectid import ObjectId  # type: ignore


class UserCreateSchema(BaseModel):
    username: str = Field(min_length=1, max_length=50, description="The username of the user")
    email: str | None = None
    password: str = Field(min_length=6)
    role: Role = Role.STUDENT
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "use_enum_values": True,
        "from_attributes": True,
        "extra": "allow",
        "json_encoders": {
            ObjectId: str,
        },
    }

