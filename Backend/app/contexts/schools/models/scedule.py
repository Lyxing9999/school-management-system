from datetime import datetime
from typing import Optional

class ScheduleAggregate:
    def __init__(
        self,
        class_id: str,
        course_id: str,
        teacher_id: str,
        day_of_week: str,
        start_time: str,
        end_time: str,
        room: Optional[str] = None,
        created_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted: bool = False,
        deleted_at: Optional[datetime] = None
    ):
        self.class_id = class_id
        self.course_id = course_id
        self.teacher_id = teacher_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted
        self.deleted_at = deleted_at

    # -------------------------
    # Business Logic Methods
    # -------------------------
    def change_teacher(self, teacher_id: str):
        if self.teacher_id != teacher_id:
            self.teacher_id = teacher_id
            self.updated_at = datetime.utcnow()

    def change_time(self, day_of_week: str, start_time: str, end_time: str):
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.updated_at = datetime.utcnow()

    def change_room(self, room: str):
        if self.room != room:
            self.room = room
            self.updated_at = datetime.utcnow()

    def mark_deleted(self):
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
