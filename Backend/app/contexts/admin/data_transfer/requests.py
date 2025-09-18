from pydantic import BaseModel , Field
from app.contexts.shared.enum.roles import SystemRole
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
    email: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8)
    role: SystemRole | None = Field(None)
    created_by: str | None = Field(None)
    model_config = {
        "enum_values_as_str": True,
        'extra': 'forbid'
    }




class AdminUpdateUserSchema(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8)
    role: SystemRole | None = Field(None)
    model_config = {
        "extra": "allow"
    }



class AdminCreateClassSchema(PlaceholderModel):
    pass



class AdminCreateStaffSchema(BaseModel):
    username: str | None = Field(None)
    email: str = Field(... , min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    staff_id: str = Field(... , min_length=3, max_length=50)
    staff_name: str = Field(... , min_length=3, max_length=50)
    role: SystemRole = Field(...)
    permissions: list[str] | None = Field(None)
    phone_number: str = Field(..., min_length=3, max_length=50)
    created_by: str | None = Field(None)
    address: str | None = Field(None)

    model_config = {
        "enum_values_as_str": True,
        'extra': 'forbid'
    }