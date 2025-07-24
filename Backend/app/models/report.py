from pydantic import BaseModel, Field # type: ignore
from typing import Optional
from datetime import datetime, timezone
from app.enums.report import TargetType, ReportReason, Severity
from app.enums.status import ReportStatus
from app.utils.pyobjectid import PyObjectId
class ReportModel(BaseModel):
    
    __collection_name__ = "report"
    
    
    id: PyObjectId | None = Field(None, alias="_id")
    reporter_id: str 
    target_id: str | None = None
    target_type: TargetType
    reason: ReportReason
    description: str | None = Field(..., min_length = 5, max_length = 1000)
    severity: Severity = Severity.MEDIUM
    status: ReportStatus = ReportStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "use_enum_values": True,
    }

    @classmethod
    def create_minimal(cls, autofilled_data: Optional[dict] = None, **overrides):
        data = {
            "reporter_id": "",
            "target_id": None,
            "target_type": TargetType.CONTENT,
            "reason": ReportReason.OTHER,
            "description": "",
            "severity": Severity.MEDIUM,
            "status": ReportStatus.PENDING,
            "created_at": datetime.now(timezone.utc),
        }
        if autofilled_data:
            data.update(autofilled_data)
        data.update(overrides)
        return cls(**data)