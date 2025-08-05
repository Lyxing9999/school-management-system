from pydantic import BaseModel, Field


class UserUpdateData(BaseModel):
    username: str | None = Field(None, description="The username of the user")
    email: str | None = Field(None, description="The email of the user")
    password: str | None = Field(None, description="The password of the user")




