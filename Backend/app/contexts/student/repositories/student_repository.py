from typing import Optional
from bson import ObjectId
from pymongo.collection import Collection
from ..domain.student import Student
from ..mapper.student_mapper import StudentMapper  # 👈 Import Mapper

class MongoStudentRepository:
    def __init__(self, collection: Collection):
        self.collection = collection
        self._mapper = StudentMapper()

    
    def insert(self, student: Student) -> Student:
        payload = self._mapper.to_persistence(student)
        self.collection.insert_one(payload)
        return student

    def find_by_id(self, id: ObjectId) -> Optional[Student]:
        doc = self.collection.find_one({"_id": id})
        return self._mapper.to_domain(doc) if doc else None

    def find_by_user_id(self, user_id: ObjectId) -> Optional[Student]:
        doc = self.collection.find_one({"user_id": user_id})
        return self._mapper.to_domain(doc) if doc else None