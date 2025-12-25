from pydantic import BaseModel

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
