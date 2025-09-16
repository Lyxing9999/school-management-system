from pydantic import BaseModel , Field

from app.place_holder import PlaceholderModel
class PlaceholderModel(BaseModel):
    model_config = {
        "extra": "allow"  # allow extra fields
    }

    def __getattr__(self, item):
        # If attribute exists in extra fields, return it
        return self.model_dump().get(item, None)
class AdminCreateUserSchema(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)




class AdminUpdateUserSchema(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8)
    model_config = {
        "extra": "allow"
    }



class AdminCreateClassSchema(PlaceholderModel):
    pass

