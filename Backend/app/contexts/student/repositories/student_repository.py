from typing import Optional
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import UpdateResult

from ..domain.student import Student
from ..mapper.student_mapper import StudentMapper
from ..errors.student_exceptions import StudentUpdateFailedException

class MongoStudentRepository:
    def __init__(self, collection: Collection):
        self.collection = collection
        self._mapper = StudentMapper()

    def insert(self, student: Student) -> Student:
        payload = self._mapper.to_persistence(student)
        result = self.collection.insert_one(payload)
        student.id = result.inserted_id 
        return student

    def find_by_id(self, id: ObjectId) -> Optional[Student]:
        doc = self.collection.find_one({"_id": id})
        return self._mapper.to_domain(doc) if doc else None

    def find_by_user_id(self, user_id: ObjectId) -> Optional[Student]:
        doc = self.collection.find_one({"user_id": user_id})
        return self._mapper.to_domain(doc) if doc else None

    def update(self, student: Student) -> Student:
        payload = self._mapper.to_persistence(student)   
        _id = payload.pop("_id") 
        result: UpdateResult = self.collection.update_one(
            {"_id": _id},
            {"$set": payload}
        )
        if result.matched_count == 0:
            raise StudentUpdateFailedException(user_id=student.user_id, student_id=student.id, reason="Student ID not found in DB")
        return student