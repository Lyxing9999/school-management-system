from dataclasses import dataclass
from typing import Optional, Set
from bson import ObjectId

@dataclass(frozen=True)
class ClassRosterUpdate:
    class_id: ObjectId
    desired_student_ids: Set[ObjectId]
    desired_teacher_id: Optional[ObjectId]

    @staticmethod
    def from_payload(*, class_id: ObjectId, student_ids: list[ObjectId], homeroom_teacher_id: Optional[ObjectId]) -> "ClassRosterUpdate":
        # normalize duplicates by set()
        return ClassRosterUpdate(
            class_id=class_id,
            desired_student_ids=set(student_ids),
            desired_teacher_id=homeroom_teacher_id,
        )

    def diff(self, current_student_ids: Set[ObjectId]) -> tuple[Set[ObjectId], Set[ObjectId]]:
        to_add = self.desired_student_ids - current_student_ids
        to_remove = current_student_ids - self.desired_student_ids
        return to_add, to_remove