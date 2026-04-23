from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.contexts.admin.data_transfer.responses.common import PaginatedDTO
from app.contexts.shared.lifecycle.dto import LifecycleDTO


class DeductionRuleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    id: str
    type: str
    min_minutes: int
    max_minutes: int | None = None
    deduction_percentage: float
    is_active: bool
    created_by: str | None = None
    created_by_name: str | None = None
    deleted_by: str | None = None
    deleted_by_name: str | None = None
    lifecycle: LifecycleDTO


class DeductionRulePaginatedDTO(PaginatedDTO[DeductionRuleDTO]):
    pass
