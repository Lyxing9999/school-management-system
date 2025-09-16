class GradeAggregate:
    def __init__(self, student_id, course_id, score, created_at=None):
        self.student_id = student_id
        self.course_id = course_id
        self.score = score
        self.created_at = created_at or datetime.utcnow()