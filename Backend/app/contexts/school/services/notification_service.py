from datetime import datetime
from bson import ObjectId


class NotificationService:
    def __init__(self, notifications_collection, telegram_client=None, email_client=None):
        self.notifications = notifications_collection
        self.telegram_client = telegram_client
        self.email_client = email_client

    def notify_grade_updated(
        self,
        student_id: ObjectId,
        subject_id: ObjectId,
        score: float,
    ) -> None:
        # 1) persist notification
        self.notifications.insert_one({
            "user_id": student_id,
            "type": "grade",
            "title": "New grade posted",
            "message": f"You received a score of {score} in subject {subject_id}",
            "status": "sent",
            "created_at": datetime.utcnow(),
        })

        # 2) optionally send telegram/email
        # (can be no-op for now, implement later)
        if self.telegram_client:
            ...
        if self.email_client:
            ...