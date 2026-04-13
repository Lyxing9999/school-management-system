from enum import Enum


class AttendanceDayType(str, Enum):
    WORKING_DAY = "working_day"
    WEEKEND = "weekend"
    PUBLIC_HOLIDAY = "public_holiday"
    MISSING_CHECK_OUT = "missing_check_out"