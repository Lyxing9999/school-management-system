from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection


class TeacherAssignmentReadModel:
    """
    Read model for checking if a teacher is allowed to grade
    a given (class, subject) combination.

    GradeFactory calls: can_teacher_grade(teacher_id, class_id, subject_id)
    """

    def __init__(self, db: Database):
        # Adjust collection name to what you actually have
        # e.g. "teacher_subject_assignments" / "class_subject_teachers"
        self.collection: Collection = db["teacher_subject_assignments"]

    def can_teacher_grade(
        self,
        teacher_id: ObjectId,
        class_id: ObjectId,
        subject_id: ObjectId,
    ) -> bool:
        """
        Returns True if there is an assignment row stating
        that this teacher can grade this subject in this class.
        """
        doc = self.collection.find_one(
            {
                "teacher_id": teacher_id,
                "class_id": class_id,
                "subject_id": subject_id,
                "is_active": True,
            }
        )
        return doc is not None