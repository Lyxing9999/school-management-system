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
    M = "M" 
    A = "A"  
    E = "E" 


class Category(str, Enum):
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    APPRECIATION = "appreciation"
    OTHER = "other"
    SYSTEM = "system" 


class ReportStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    
class FeedbackStatus(str, Enum):
    UNREAD = "unread"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    



class AttendanceStatus(str, Enum):
    PRESENT =  "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused" 



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


from enum import Enum

class Role(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class FeedbackRole(str, Enum):
    STUDENT = Role.STUDENT.value
    TEACHER = Role.TEACHER.value

from enum import Enum
class TargetType(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    CLASS = "class"
    SYSTEM = "system"
    CONTENT = "content"
class ReportReason(str, Enum):
    BUG = "bug"
    ABUSE = "abuse"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    UNFAIR_TREATMENT = "unfair_treatment"
    ERROR = "error"
    OTHER = "other"
class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    