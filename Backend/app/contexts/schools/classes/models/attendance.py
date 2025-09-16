class AttendanceAggregate:
    def __init__(self, student_id=None, teacher_id=None, class_id=None, course_id=None, date=None, present=True):
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.course_id = course_id
        self.date = date or datetime.utcnow()
        self.present = present