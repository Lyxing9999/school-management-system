from typing import Any, Dict, Optional, Literal, List, Tuple

from app.contexts.core.errors.app_base_exception import AppBaseException, ErrorSeverity, ErrorCategory

DeleteMode = Literal["soft", "hard", "restore", "status_change"]


def _humanize_key(key: str) -> str:
    return key.replace("_", " ").strip().capitalize()


def _format_reasons(reasons: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Returns:
      - short readable text for user_message
      - structured list for frontend (chips/table)
    """
    if not reasons:
        return "Operation is blocked by a policy rule.", []

    items: List[Dict[str, Any]] = []
    parts: List[str] = []

    for k, v in reasons.items():
        label = _humanize_key(k)

        # v can be int, bool, list, dict...
        if isinstance(v, (int, float)) and v > 0:
            parts.append(f"{label}: {v}")
        elif isinstance(v, bool):
            parts.append(f"{label}: {'Yes' if v else 'No'}")
        elif isinstance(v, (list, tuple)) and v:
            parts.append(f"{label}: {len(v)} items")
        elif v is not None and v != "":
            parts.append(f"{label}: {v}")
        else:
            parts.append(label)

        items.append({"key": k, "label": label, "value": v})

    return "; ".join(parts), items


def _suggested_action(entity: str, recommended: Optional[DeleteMode]) -> Dict[str, Any]:
    """
    Frontend can use this to show a CTA button:
      - recommended == "soft" => show "Soft delete instead"
      - recommended == "status_change" => show "Deactivate/Archive"
    """
    if not recommended:
        return {"type": "none"}

    label_map = {
        "soft": f"Soft delete {entity}",
        "hard": f"Hard delete {entity}",
        "restore": f"Restore {entity}",
        "status_change": f"Change {entity} status",
    }

    return {
        "type": "suggested",
        "recommended": recommended,
        "label": label_map.get(recommended, f"Try {recommended}"),
    }


class LifecyclePolicyDeniedException(AppBaseException):
    """
    Raised when a lifecycle policy blocks an operation.
    Goal: return a frontend-friendly payload with actionable info.
    """

    def __init__(
        self,
        entity: str,
        entity_id: str,
        mode: DeleteMode,
        reasons: Dict[str, Any],
        recommended: Optional[DeleteMode] = None,
        hint: str | None = None,
    ):
        reason_text, reason_items = _format_reasons(reasons)

        # user-facing messages: short, direct, actionable
        mode_label = {
            "soft": "delete",
            "hard": "permanently delete",
            "restore": "restore",
            "status_change": "change status of",
        }.get(mode, mode)

        user_message = f"Cannot {mode_label} this {entity}. {reason_text}"
        if recommended:
            user_message += f" Suggested: {recommended}."

        details = {
            "entity": entity,
            "entity_id": entity_id,
            "mode": mode,
            "reasons": reasons,              
            "reason_items": reason_items,   
            "recommended": recommended,
            "action": _suggested_action(entity, recommended),
        }

        super().__init__(
            message=(
                f"Lifecycle policy denied: entity={entity} id={entity_id} "
                f"mode={mode} reasons={reasons} recommended={recommended}"
            ),
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=user_message,
            details=details,
            hint=hint or "Remove blockers (unassign/remove relationships) and try again.",
            recoverable=True,
        )