from __future__ import annotations

from datetime import datetime, date, time
from typing import Any, Iterable, List, Optional
from bson import ObjectId


def strip(v: Any) -> Any:
    return v.strip() if isinstance(v, str) else v


def strip_or_none(v: Any) -> Any:
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def oid_to_str(v: Any) -> Optional[str]:
    """
    Accept ObjectId | str | None. Return clean str | None.
    - trims strings
    - converts "" -> None
    """
    if v is None:
        return None
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return str(v)


def oids_to_str_list(values: Any) -> List[str]:
    """
    Accept list/iterable of ObjectId/str, returns list[str] (filters empty).
    """
    if values is None:
        return []
    if not isinstance(values, (list, tuple, set)):
        raise ValueError("Expected a list of ids.")
    out: List[str] = []
    for v in values:
        s = oid_to_str(v)
        if s:
            out.append(s)
    return out


def parse_date_yyyy_mm_dd(v: Any) -> Optional[date]:
    if v is None:
        return None
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return None
        return datetime.strptime(v, "%Y-%m-%d").date()
    raise ValueError("Invalid date. Expected YYYY-MM-DD.")


def ensure_day_of_week_1_7(v: Any) -> int:
    """
    Normalizes day_of_week into int 1..7.
    Supports: int, "1", enum with .value, etc.
    """
    if v is None:
        raise ValueError("day_of_week is required")

    # Enum -> value
    if hasattr(v, "value"):
        v = v.value

    if isinstance(v, str):
        v = v.strip()
        if not v:
            raise ValueError("day_of_week is required")
        v = int(v)

    if not isinstance(v, int):
        raise ValueError("day_of_week must be an integer (1..7)")

    if v < 1 or v > 7:
        raise ValueError("day_of_week must be between 1 and 7")

    return v


def validate_time_range(start: time, end: time) -> None:
    if start >= end:
        raise ValueError("end_time must be after start_time")