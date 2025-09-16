from pydantic import BaseModel
from app.contexts.shared.enum.roles import SystemRole
from pydantic import BaseModel
from bson import ObjectId
# -------------------------
# Login
# -------------------------
class UserLoginSchema(BaseModel):
    email: str
    password: str 




# -------------------------
# Register
# -------------------------
class UserRegisterSchema(BaseModel):
    email: str
    password: str
    username: str | None = None
    role: SystemRole = SystemRole.STUDENT
    created_by: str | ObjectId | None = None

    model_config = {
         "enum_values_as_str": True,
         "arbitrary_types_allowed": True
    }

 
# -------------------------
# Update
# -------------------------
class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None

    model_config = {
         "enum_values_as_str": True,
    }

# -------------------------
# Form schemas (UI placeholders)
# -------------------------
def get_user_form_schema() -> dict:
    return {
        "title": "UserForm",
        "type": "object",
        "properties": {
            "email": {"type": "string", "placeholder": "Enter email"},
            "password": {"type": "string", "placeholder": "Enter password"},
            "role": {"type": "select", "enum": ["STUDENT", "PARENT", "TEACHER"]},
        }
    }

def get_user_update_form_schema() -> dict:
    return {
        "title": "UserUpdateForm",
        "type": "object",
        "properties": {
            "email": {"type": "string", "placeholder": "Enter email"},
            "password": {"type": "string", "placeholder": "Enter password"},
            "role": {"type": "select", "enum": ["STUDENT", "PARENT"]},
        }
    }