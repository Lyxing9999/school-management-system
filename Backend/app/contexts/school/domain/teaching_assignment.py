from __future__ import annotations
from bson import ObjectId
from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc

class TeachingAssignmentRecord:
    def __init__(
        self,
        *,
        class_id: ObjectId | str,
        subject_id: ObjectId | str,
        teacher_id: ObjectId | str,
        assigned_by: ObjectId | str | None = None,
        id: ObjectId | None = None,
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()
        self.class_id = class_id if isinstance(class_id, ObjectId) else ObjectId(class_id)
        self.subject_id = subject_id if isinstance(subject_id, ObjectId) else ObjectId(subject_id)
        self.teacher_id = teacher_id if isinstance(teacher_id, ObjectId) else ObjectId(teacher_id)

        self.assigned_by = (
            assigned_by
            if (assigned_by is None or isinstance(assigned_by, ObjectId))
            else ObjectId(assigned_by)
        )

        self.lifecycle = lifecycle or Lifecycle()

    def change_teacher(self, teacher_id: ObjectId | str, *, actor_id: ObjectId | None = None) -> None:
        self.teacher_id = teacher_id if isinstance(teacher_id, ObjectId) else ObjectId(teacher_id)
        if actor_id is not None:
            self.assigned_by = actor_id
        self.lifecycle.touch(now_utc())

    def soft_delete(self, actor_id: ObjectId) -> None:
        self.lifecycle.soft_delete(actor_id)

    def restore(self) -> None:
        self.lifecycle.restore()