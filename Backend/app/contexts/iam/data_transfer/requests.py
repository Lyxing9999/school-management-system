from pydantic import BaseModel, Field
from app.contexts.shared.enum.roles import SystemRole
from pydantic import BaseModel
from bson import ObjectId
# -------------------------
# Login
# -------------------------
class IAMLoginSchema(BaseModel):
    email: str
    password: str 


# -------------------------
# Update
# -------------------------
class IAMUpdateSchema(BaseModel):
    username: str | None =  None
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
            "role": {"type": "select", "enum": ["STUDENT", "TEACHER"]},
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