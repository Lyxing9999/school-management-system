from __future__ import annotations

from typing import Any, Dict, Optional
from app.contexts.student.domain.student import StudentStatus

def not_deleted(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Default: treat deleted as soft-deleted flag.
    Includes docs where deleted is False OR missing.
    """
    q: Dict[str, Any] = {"deleted": {"$ne": True}}
    if extra:
        q.update(extra)
    return q

def active(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Active student profiles:
    status == "Active" AND deleted != true
    """
    q: Dict[str, Any] = {
        "status": StudentStatus.ACTIVE.value,   
        "deleted": {"$ne": True},
    }
    if extra:
        q.update(extra)
    return q