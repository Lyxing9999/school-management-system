from enum import Enum

class Day(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class Shift(Enum):
    M = "M"  # Morning
    A = "A"  # Afternoon
    E = "E"  # Evening
