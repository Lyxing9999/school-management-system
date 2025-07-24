from pydantic import BaseModel, Field # type: ignore
from app.utils.objectid import ObjectId #type: ignore
from typing import Optional
from datetime import datetime, timezone, date
from app.enums.roles import Role


class TeacherCreateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str
    role: Role