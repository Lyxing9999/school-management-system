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
    