# app/contexts/school/services/reporting_service.py

from datetime import date
from bson import ObjectId


class ReportingService:
    def __init__(
        self,
        enrollment_read_model,
        attendance_read_model,
        grade_read_model,
    ):
        self.enrollment_read_model = enrollment_read_model
        self.attendance_read_model = attendance_read_model
        self.grade_read_model = grade_read_model

    # 1) Attendance summary for a student in a month
    def get_student_monthly_attendance(
        self,
        student_id: str | ObjectId,
        year: int,
        month: int,
    ) -> dict:
        """
        Returns something like:
        {
          "present": 18,
          "absent": 2,
          "excused": 1,
          "total": 21
        }
        """
        records = self.attendance_read_model.get_for_student_in_month(
            student_id=student_id,
            year=year,
            month=month,
        )

        stats = {"present": 0, "absent": 0, "excused": 0, "total": 0}
        for rec in records:
            stats["total"] += 1
            status = rec["status"]
            if status in stats:
                stats[status] += 1

        return stats

    # 2) Grades + GPA for a student in a term
    def get_student_term_grades(
        self,
        student_id: str | ObjectId,
        term: str,
    ) -> dict:
        """
        Returns:
        {
          "term": "2025-S1",
          "grades": [...list of grade docs...],
          "gpa": 3.5
        }
        """
        grades = self.grade_read_model.get_for_student_in_term(
            student_id=student_id,
            term=term,
        )

        # very simple GPA example (you can replace with your real formula)
        if not grades:
            gpa = 0.0
        else:
            avg_score = sum(g["score"] for g in grades) / len(grades)
            gpa = round((avg_score / 20), 2)  # e.g. 0–100 → 0–5 GPA

        return {
            "term": term,
            "grades": grades,
            "gpa": gpa,
        }