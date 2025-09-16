
class StudentService:
    def __init__(self, db: Database):
        self.db = db

    def update_profile(self, student_id: str, data: dict):
        pass

    def request_leave(self, student_id: str, leave_data: dict):
        pass

    def get_attendance(self, student_id: str):
        pass

    def get_scores(self, student_id: str):
        pass
