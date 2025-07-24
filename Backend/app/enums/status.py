from enum import Enum


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