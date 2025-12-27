from app.contexts.school.ports.student_membership_port import StudentMembershipPort
from app.contexts.school.domain.value_objects.class_roster_update import ClassRosterUpdate


class ClassRelationsService:
    def __init__(self, *, class_repo, student_membership: StudentMembershipPort):
        self.class_repo = class_repo
        self.student_membership = student_membership

    def apply(self, update: ClassRosterUpdate, *, use_transaction: bool = True) -> dict:
        def run(session=None) -> dict:
            cls = self.class_repo.find_by_id(update.class_id, session=session)
            if cls is None or cls.lifecycle.deleted_at is not None:
                raise Exception("CLASS_NOT_FOUND_OR_DELETED")

            # Teacher update (tracked)
            old_teacher = cls.teacher_id
            teacher_changed = (old_teacher != update.desired_teacher_id)
            if teacher_changed:
                ok = self.class_repo.set_teacher(update.class_id, update.desired_teacher_id, session=session)
                if not ok:
                    raise Exception("CLASS_NOT_FOUND_OR_DELETED")

            current_ids = self.student_membership.list_student_ids_in_class(update.class_id, session=session)
            to_add, to_remove = update.diff(current_ids)

            added: list[str] = []
            removed: list[str] = []
            conflicts: list[dict] = []
            capacity_rejected: list[str] = []

            # 1) Removals
            for sid in to_remove:
                left = self.student_membership.try_leave_class(sid, update.class_id, session=session)
                if left:
                    self.class_repo.try_decrement_enrollment(update.class_id, session=session)
                    removed.append(str(sid))

            # 2) Additions
            for sid in to_add:
                if not self.student_membership.exists(sid, session=session):
                    conflicts.append({"student_id": str(sid), "reason": "NOT_FOUND", "current_class_id": None})
                    continue

                reserved = self.student_membership.try_join_class(sid, update.class_id, session=session)
                if not reserved:
                    cur_cls = self.student_membership.get_current_class_id(sid, session=session)
                    conflicts.append({
                        "student_id": str(sid),
                        "reason": "ALREADY_ENROLLED",
                        "current_class_id": str(cur_cls) if cur_cls else None,
                    })
                    continue

                updated_class = self.class_repo.try_increment_enrollment(update.class_id, session=session)
                if updated_class is None:
                    self.student_membership.revert_join(sid, update.class_id, session=session)
                    capacity_rejected.append(str(sid))
                    continue

                added.append(str(sid))

            final_cls = self.class_repo.find_by_id(update.class_id, session=session)
            enrolled_count = int(final_cls.enrolled_count) if final_cls else 0

            return {
                "class_id": str(update.class_id),
                "teacher_changed": teacher_changed,
                "teacher_id": str(update.desired_teacher_id) if update.desired_teacher_id else None,
                "enrolled_count": enrolled_count,
                "added": added,
                "removed": removed,
                "conflicts": conflicts,
                "capacity_rejected": capacity_rejected,
            }

        if not use_transaction:
            return run(session=None)

        with self.class_repo.start_session() as session:
            with session.start_transaction():
                return run(session=session)