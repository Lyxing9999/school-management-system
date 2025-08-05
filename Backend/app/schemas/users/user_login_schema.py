from pydantic import BaseModel , Field , constr

class UserLoginSchema(BaseModel):
    username: constr(min_length=3, max_length=20) = Field(..., description="The username of the user")
    password: constr(min_length=6) = Field(..., description="The password of the user")

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
    }