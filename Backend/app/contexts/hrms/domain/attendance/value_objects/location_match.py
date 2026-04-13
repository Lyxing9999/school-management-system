from dataclasses import dataclass


@dataclass(frozen=True)
class LocationMatch:
    is_valid: bool
    distance_meters: float | None = None
    reason_required: bool = False