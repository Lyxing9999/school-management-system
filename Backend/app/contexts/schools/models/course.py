from datetime import datetime 
from typing import List , Optional 




class CourseAggregate:
    def __init__(
        self,
        name: str,
        teacher_id: str,
        class_ids: Optional[List[str]] = None, 
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted: bool = False,
        deleted_at: Optional[datetime] = None
    ):
        self.name = name
        self.teacher_id = teacher_id
        self.class_ids = class_ids or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted
        self.deleted_at = deleted_at



    # -------------------------
    # Business Logic Methods
    # -------------------------
    def assign_class(self, class_id: str):
        if class_id not in self.class_ids:
            self.class_ids.append(class_id)
            self.updated_at = datetime.utcnow()

    def remove_class(self, class_id: str):
        if class_id in self.class_ids:
            self.class_ids.remove(class_id)
            self.updated_at = datetime.utcnow()

    def change_teacher(self, teacher_id: str):
        if self.teacher_id != teacher_id:
            self.teacher_id = teacher_id
            self.updated_at = datetime.utcnow()

    def mark_deleted(self):
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()




    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "teacher_id": self.teacher_id,
            "class_ids": self.class_ids,
            "timestamps": self.timestamp(),
            "deleted": self.deleted,
        }