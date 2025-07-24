from app.models.grade import GradeModel
from app.utils.objectid import ObjectId # type: ignore
import pytest

@pytest.fixture
def grade_data():
    return {
        "teacher_id": str(ObjectId()),
        "student_id": str(ObjectId()),
        "class_id": str(ObjectId()),
        "course_id": str(ObjectId()),
        "attendance": 10,
        "assignment": 15,
        "quiz": 5,
        "project": 20,
        "midterm": 20,
        "final_exam": 25
    }   

def test_grade_model(grade_data):
    grade = GradeModel.create_minimal(**grade_data)
    assert grade.total == 95.0
    assert grade.letter_grade == "A"
    assert grade.is_passing() is True

def test_grade_model_with_autofilled_data(grade_data):
    # First test with fixture data
    grade = GradeModel.create_minimal(autofilled_data=grade_data)
    assert grade.total == 95.0
    assert grade.letter_grade == "A"
    assert grade.is_passing() is True

    # Second test with hardcoded input (change some values to get different total)
    grade = GradeModel.create_minimal(
        teacher_id=str(ObjectId()),
        student_id=str(ObjectId()),
        class_id=str(ObjectId()),
        course_id=str(ObjectId()),
        attendance=10,
        assignment=10,
        quiz=5,
        project=15,
        midterm=20,
        final_exam=18  # total = 78
    )
    assert grade.total == 78.0
    assert grade.letter_grade == "C+"
    assert grade.is_passing() is True