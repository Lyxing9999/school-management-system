from enum import Enum


class AttendanceStatus(str, Enum):
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    LATE = "late"
    EARLY_LEAVE = "early_leave"
    ABSENT = "absent"
    HOLIDAY_OFF = "holiday_off"
    WEEKEND_OFF = "weekend_off"
    MISSING_CHECK_OUT = "missing_check_out"

    # legacy / backward compatibility only
    WRONG_LOCATION_PENDING = "wrong_location_pending"
    WRONG_LOCATION_APPROVED = "wrong_location_approved"
    WRONG_LOCATION_REJECTED = "wrong_location_rejected"