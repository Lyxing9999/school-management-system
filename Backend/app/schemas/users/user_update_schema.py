from pydantic import BaseModel, constr

class UserUpdateSchema(BaseModel):
    username: constr(strip_whitespace=True, min_length=3) | None = None
    email: str | None = None  # Soft type, no strict Email validation yet
    password: constr(strip_whitespace=True, min_length=6) | None = None

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
    }