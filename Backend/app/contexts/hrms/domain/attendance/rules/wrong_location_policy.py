from __future__ import annotations

from ..value_objects.location_match import LocationMatch


class WrongLocationPolicy:
    @staticmethod
    def evaluate(*, is_valid_location: bool, distance_meters: float | None = None) -> LocationMatch:
        return LocationMatch(
            is_valid=is_valid_location,
            distance_meters=distance_meters,
            reason_required=not is_valid_location,
        )