from pymongo.database import Database

from app.contexts.school.services.composition import build_school_facade


class SchoolService:
    """
    Backward-compatible adapter.

    Existing code can keep doing: SchoolService(db).create_class(...)
    Internally we delegate to the new SchoolFacade + use cases.

    Once you migrate all imports to use SchoolFacade directly,
    you can delete this file.
    """

    def __init__(self, db: Database):
        self._facade = build_school_facade(db)

    # -------- Class --------
    def create_class(self, *args, **kwargs):
        return self._facade.class_service.create_class(*args, **kwargs)

    def assign_teacher_to_class(self, *args, **kwargs):
        return self._facade.class_service.assign_teacher_to_class(*args, **kwargs)

    def soft_delete_class(self, *args, **kwargs):
        return self._facade.class_service.soft_delete_class(*args, **kwargs)

    def restore_class(self, *args, **kwargs):
        return self._facade.class_service.restore_class(*args, **kwargs)

    def hard_delete_class(self, *args, **kwargs):
        return self._facade.class_service.hard_delete_class(*args, **kwargs)

    # -------- Teacher assignment --------
    def assign_teacher_to_subject_in_class(self, *args, **kwargs):
        return self._facade.teacher_assignment_service.assign_teacher_to_subject_in_class(*args, **kwargs)

    # -------- Enrollment --------
    def enroll_student_to_class(self, *args, **kwargs):
        return self._facade.enrollment_service.enroll_student_to_class(*args, **kwargs)

    def unenroll_student_from_class(self, *args, **kwargs):
        return self._facade.enrollment_service.unenroll_student_from_class(*args, **kwargs)

    def update_class_relations(self, *args, **kwargs):
        return self._facade.class_relations_service.apply(*args, **kwargs)
    # -------- Attendance --------
    def mark_attendance(self, *args, **kwargs):
        return self._facade.attendance_service.mark_attendance(*args, **kwargs)

    def change_attendance_status(self, *args, **kwargs):
        return self._facade.attendance_service.change_attendance_status(*args, **kwargs)

    def get_attendance_by_id(self, *args, **kwargs):
        return self._facade.attendance_service.get_attendance_by_id(*args, **kwargs)
    
    def soft_delete_attendance(self, *args, **kwargs):
        return self._facade.attendance_service.soft_delete_attendance(*args, **kwargs)
    
    def restore_attendance(self, *args, **kwargs):
        return self._facade.attendance_service.restore_attendance(*args, **kwargs)
    
    def hard_delete_attendance(self, *args, **kwargs):
        return self._facade.attendance_service.hard_delete_attendance(*args, **kwargs)

    # -------- Grades --------
    def add_grade(self, *args, **kwargs):
        return self._facade.grade_service.add_grade(*args, **kwargs)

    def update_grade_score(self, *args, **kwargs):
        return self._facade.grade_service.update_grade_score(*args, **kwargs)

    def change_grade_type(self, *args, **kwargs):
        return self._facade.grade_service.change_grade_type(*args, **kwargs)

    def get_grade_by_id(self, *args, **kwargs):
        return self._facade.grade_service.get_grade_by_id(*args, **kwargs)

    def soft_delete_grade(self, *args, **kwargs):
        return self._facade.grade_service.soft_delete_grade(*args, **kwargs)

    def restore_grade(self, *args, **kwargs):
        return self._facade.grade_service.restore_grade(*args, **kwargs)

    def hard_delete_grade(self, *args, **kwargs):
        return self._facade.grade_service.hard_delete_grade(*args, **kwargs)
    # -------- Subjects --------
    def create_subject(self, *args, **kwargs):
        return self._facade.subject_service.create_subject(*args, **kwargs)

    def get_subject_by_id(self, *args, **kwargs):
        return self._facade.subject_service.get_subject_by_id(*args, **kwargs)

    def get_subject_by_code(self, *args, **kwargs):
        return self._facade.subject_service.get_subject_by_code(*args, **kwargs)

    def activate_subject(self, *args, **kwargs):
        return self._facade.subject_service.activate_subject(*args, **kwargs)

    def update_subject_patch(self, *args, **kwargs):
        return self._facade.subject_service.update_subject_patch(*args, **kwargs)

    def deactivate_subject(self, *args, **kwargs):
        return self._facade.subject_service.deactivate_subject(*args, **kwargs)

    def soft_delete_subject(self, *args, **kwargs):
        return self._facade.subject_service.soft_delete_subject(*args, **kwargs)

    def restore_subject(self, *args, **kwargs):
        return self._facade.subject_service.restore_subject(*args, **kwargs)

    def hard_delete_subject(self, *args, **kwargs):
        return self._facade.subject_service.hard_delete_subject(*args, **kwargs)

    # -------- Schedule --------
    def create_schedule_slot_for_class(self, *args, **kwargs):
        return self._facade.schedule_service.create_schedule_slot_for_class(*args, **kwargs)

    def move_schedule_slot(self, *args, **kwargs):
        return self._facade.schedule_service.move_schedule_slot(*args, **kwargs)

    def assign_subject_to_schedule_slot(self, *args, **kwargs):
        return self._facade.schedule_service.assign_subject_to_schedule_slot(*args, **kwargs)

    def delete_schedule_slot(self, *args, **kwargs):
        return self._facade.schedule_service.delete_schedule_slot(*args, **kwargs)

    def soft_delete_schedule_slot(self, *args, **kwargs):
        return self._facade.schedule_service.soft_delete_schedule_slot(*args, **kwargs)

    def restore_schedule_slot(self, *args, **kwargs):
        return self._facade.schedule_service.restore_schedule_slot(*args, **kwargs)

    def hard_delete_schedule_slot(self, *args, **kwargs):
        return self._facade.schedule_service.hard_delete_schedule_slot(*args, **kwargs)