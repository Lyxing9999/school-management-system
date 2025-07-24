from pydantic import BaseModel, Field, computed_field  # type: ignore
from app.utils.pyobjectid import PyObjectId

class GradeModel(BaseModel):
    
    id: PyObjectId | None = Field(None, alias="_id")
    student_name: str
    course_id: str
    attendance: float | None = 0.0
    assignment: float | None = 0.0
    quiz: float | None = 0.0
    project: float | None = 0.0
    midterm: float | None = 0.0
    final_exam: float | None = 0.0 
    extra_exam: float | None = 0.0
    term: str = "Term 1"
    
    @computed_field
    def total(self) -> float:
        return (
            (self.attendance or 0) +
            (self.assignment or 0) +
            (self.quiz or 0) +
            (self.project or 0) +
            (self.midterm or 0) +
            (self.final_exam or 0) + 
            (self.extra_exam or 0)
        )
    @computed_field
    def letter_grade(self) -> str:
        total = self.total
        if total >= 97:
            return "A+"
        elif total >= 93:
            return "A"
        elif total >= 90:
            return "A-"
        elif total >= 87:
            return "B+"
        elif total >= 83:
            return "B"
        elif total >= 80:
            return "B-"
        elif total >= 77:
            return "C+"
        elif total >= 73:
            return "C"
        elif total >= 70:
            return "C-"
        elif total >= 67:
            return "D+"
        elif total >= 63:
            return "D"
        elif total >= 60:
            return "D-"
        else:
            return "F"

    def is_passing(self, passing_grade: float | None = None) -> bool:
        if passing_grade is None:
            passing_grade = 60.0
        return self.total >= passing_grade
    
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "arbitrary_types_allowed": True,
    }
