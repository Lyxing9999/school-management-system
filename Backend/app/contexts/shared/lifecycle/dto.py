from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class LifecycleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None