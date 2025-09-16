from enum import Enum

# -----------------
# Class status
# -----------------
class ClassStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

# -----------------
# Class attendance
# -----------------
class ClassAttendance(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

# -----------------
# Days of the week
# -----------------
class Day(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

# -----------------
# Class type
# -----------------
class ClassType(str, Enum):
    PRIMARY = "primary"



# -----------------
# Class level
# -----------------
class ClassLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# -----------------
# Class schedule
# -----------------
class ClassSchedule(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"