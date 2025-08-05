from pydantic import BaseModel, Field, constr

class UserRegisterSchema(BaseModel):

    username: constr(min_length=3, max_length=20) = Field(..., description="The username of the user")
    email: str | None = Field(None, description="The email of the user")
    password: constr(min_length=6) = Field(..., description="The user's password")
    
    model_config = {
        "from_attributes": True,
        "extra": "forbid",
    }