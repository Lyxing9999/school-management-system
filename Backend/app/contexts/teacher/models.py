from datetime import datetime
from typing import List, Optional
from app.contexts.enum.roles import Role







class TeacherAggregate:
    def __init__(
        self, 
        username: str, 
        email: str, 
        password: str, 
        subjects: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.username = username
        self.email = email
        self.password = password
        self.role = Role.TEACHER
        self.subjects = subjects or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # -------------------------
    # Password & Security
    # -------------------------
    def hash_password(self, auth_service=None):
        """Hash the teacher's password using AuthService"""
        if not auth_service:
            from app.contexts.auth.services import AuthService
            auth_service = AuthService()
        self.password = auth_service.hash_password(self.password)

    # -------------------------
    # Teacher Operations
    # -------------------------
    def assign_subject(self, subject: str):
        """Assign a new subject to the teacher"""
        if subject not in self.subjects:
            self.subjects.append(subject)
            self.updated_at = datetime.utcnow()

    def input_attendance(self, student_id: str, date: Optional[str] = None):
        """Record student attendance for a specific date"""
        # Placeholder: integrate with AttendanceRepository
        date = date or datetime.utcnow().isoformat()
        # e.g., return {"student_id": student_id, "date": date, "status": "present"}
        pass

    def input_score(self, student_id: str, course_id: str, score: float):
        """Record student score for a course"""
        # Placeholder: integrate with GradesRepository
        # e.g., return {"student_id": student_id, "course_id": course_id, "score": score}
        pass

    



    # -------------------------
    # Utilities
    # -------------------------
    def to_dict(self) -> dict:
        """Return a dictionary representation of the teacher aggregate"""
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "role": self.role.value,
            "subjects": self.subjects,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }