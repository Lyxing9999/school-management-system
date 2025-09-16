from pydantic import BaseModel
from datetime import datetime

class Timestamps(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None