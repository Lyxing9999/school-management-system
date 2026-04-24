# app/contexts/hrms/errors/location_exceptions.py
from app.contexts.core.errors import AppBaseException


class WorkLocationNotFoundException(AppBaseException):
    def __init__(self, location_id: str):
        super().__init__(
            message=f"Work location with ID '{location_id}' not found",
            error_code="WORK_LOCATION_NOT_FOUND",
            status_code=404,
            user_message="Work location not found.",
        )


class InvalidLocationCoordinatesException(AppBaseException):
    def __init__(self, latitude: float, longitude: float):
        super().__init__(
            message=f"Invalid coordinates: lat={latitude}, lng={longitude}. Latitude must be -90 to 90, longitude must be -180 to 180",
            error_code="INVALID_LOCATION_COORDINATES",
            status_code=400,
            user_message="Invalid location coordinates provided.",
        )


class InvalidRadiusException(AppBaseException):
    def __init__(self, radius: int):
        super().__init__(
            message=f"Invalid radius: {radius}m. Must be between 10 and 1000 meters",
            error_code="INVALID_RADIUS",
            status_code=400,
            user_message="Invalid location radius provided.",
        )


class LocationOutOfRangeException(AppBaseException):
    def __init__(self, distance: float, allowed_radius: int):
        super().__init__(
            message=f"Check-in location is {distance:.0f}m away, exceeds allowed radius of {allowed_radius}m",
            error_code="LOCATION_OUT_OF_RANGE",
            status_code=400,
            user_message="You are outside the allowed check-in area.",
        )


class WorkLocationDeletedException(AppBaseException):
    def __init__(self, location_id: str):
        super().__init__(
            message=f"Work location '{location_id}' has been deleted",
            error_code="WORK_LOCATION_DELETED",
            status_code=410,
            user_message="Work location has been deleted.",
        )


class WorkLocationInactiveException(AppBaseException):
    def __init__(self, location_id: str):
        super().__init__(
            message=f"Work location '{location_id}' is inactive",
            error_code="WORK_LOCATION_INACTIVE",
            status_code=400,
            user_message="Assigned work location is inactive.",
            details={"location_id": location_id},
            hint="Activate the location or assign another active location.",
            recoverable=True,
        )


class WorkLocationCoordinatesPairRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Both latitude and longitude are required when updating coordinates",
            error_code="WORK_LOCATION_COORDINATES_PAIR_REQUIRED",
            status_code=400,
            user_message="Both latitude and longitude are required.",
            recoverable=True,
        )


class WorkLocationNameRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Location name is required",
            error_code="WORK_LOCATION_NAME_REQUIRED",
            status_code=400,
            user_message="Work location name is required.",
        )
