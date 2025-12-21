from bson import ObjectId
from pymongo.database import Database
from contexts.student.services.student_lifecycle_service import StudentLifecycleService
from contexts.staff.services.staff_lifecycle_service import StaffLifecycleService


class AdminLifecycleFacade:
    def __init__(self, db: Database):
        self.student = StudentLifecycleService(db)
        self.staff = StaffLifecycleService(db)

    # Student operations (admin-facing)
    def soft_delete_student(self, student_id: ObjectId, actor_id: ObjectId) -> None:
        self.student.soft_delete(student_id, actor_id)

    def restore_student(self, student_id: ObjectId, actor_id: ObjectId) -> None:
        self.student.restore(student_id, actor_id)

    def hard_delete_student(self, student_id: ObjectId, actor_id: ObjectId) -> None:
        self.student.hard_delete(student_id, actor_id)