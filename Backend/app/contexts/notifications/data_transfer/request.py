from typing import Optional
from pydantic import BaseModel


class MarkReadSchema(BaseModel):
    notification_id: str


class ListNotificationsQuery(BaseModel):
    limit: int = 30
    cursor: Optional[str] = None