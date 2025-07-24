from enum import Enum
class Category(str, Enum):
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    APPRECIATION = "appreciation"
    OTHER = "other"
    SYSTEM = "system"  # add if you want this value
