
from pymongo.database import Database
from app.contexts.student.repositories import StudentRepository
from app.contexts.student.models import StudentUpdatePayload , StudentFactory , StudentMapper
from app.contexts.student.data_transfer.requests import StudentInfoUpdateSchema
from app.contexts.student.data_transfer.responses import StudentInfoBaseDataDTO
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.student.models import Student
from app.contexts.student.error.student_exceptions import StudentNotFoundException
class StudentService:
    def __init__(self, db: Database):
        self.db = db
        self.student_repository = StudentRepository(db)



    def get_student_to_domain(self, user_id: str) -> Student:
        user_obj = mongo_converter.convert_to_object_id(user_id)
        student = self.student_repository.get_student_info(user_obj)
        if not student:
            return None
        student_model = StudentMapper.to_domain(student)
        return student_model


    def get_student_info(self, user_id: str) -> StudentInfoBaseDataDTO | None :
        user_obj = mongo_converter.convert_to_object_id(user_id)
        student = self.student_repository.get_student_info(user_obj)
        if not student:
            return None
        student_model = StudentMapper.to_domain(student)
        return StudentMapper.to_dto(student_model)



    def save_student_info(
        self, 
        user_id: str, 
        student_payload: StudentInfoUpdateSchema
    ) -> StudentInfoBaseDataDTO:
        try:
            user_obj = mongo_converter.convert_to_object_id(user_id)
            payload_obj = StudentUpdatePayload(**student_payload.model_dump())
            # Load or create domain object
            existing_student_dict = self.student_repository.get_student_info(user_obj)
            student = (
                StudentMapper.to_domain(existing_student_dict)
                if existing_student_dict
                else StudentFactory.create_from_payload(user_id=user_obj, payload=payload_obj)
            )
            student.update_info(payload_obj)
            # Persist
            saved_dict = self.student_repository.save_student_info(user_obj, StudentMapper.to_persistence_dict(student))
            
            saved_student = StudentMapper.to_domain(saved_dict)
            return StudentMapper.to_dto(saved_student)
        except Exception as e:
            raise RuntimeError(f"Failed to save student info: {str(e)}")


    def request_leave(self, student_id: str, leave_data: dict):
        pass

    def get_attendance(self, student_id: str):
        pass

    def get_scores(self, student_id: str):
        pass


    