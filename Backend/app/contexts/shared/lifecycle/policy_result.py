from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Literal


DeleteMode = Literal["soft", "hard", "restore", "status_change"]


@dataclass
class PolicyResult:
    allowed: bool
    mode: DeleteMode
    reasons: Dict[str, Any] = field(default_factory=dict)
    recommended: Optional[DeleteMode] = None

    @staticmethod
    def ok(mode: DeleteMode) -> "PolicyResult":
        return PolicyResult(allowed=True, mode=mode)

    @staticmethod
    def deny(mode: DeleteMode, reasons: Dict[str, Any], recommended: Optional[DeleteMode] = None) -> "PolicyResult":
        return PolicyResult(allowed=False, mode=mode, reasons=reasons, recommended=recommended)