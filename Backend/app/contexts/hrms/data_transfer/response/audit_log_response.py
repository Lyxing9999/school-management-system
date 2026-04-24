from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict

from app.contexts.shared.lifecycle.dto import LifecycleDTO
from app.contexts.admin.data_transfer.responses.common import PaginatedDTO


class AuditLogDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    id: str
    entity_type: str
    entity_id: str
    entity_name: Optional[str] = None
    action: str
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    actor_email: Optional[str] = None
    action_at: datetime
    details: Dict[str, Any] = {}
    lifecycle: LifecycleDTO


class AuditLogPaginatedDTO(PaginatedDTO[AuditLogDTO]):
    pass
