from __future__ import annotations

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from app.contexts.hrms.errors.employee_exceptions import EmployeeNotFoundException
from app.contexts.shared.model_converter import mongo_converter


class MongoEmployeeRepository:
    def __init__(self, db: Database):
        self.collection = db["hr_employees"]

    @staticmethod
    def _oid(value) -> ObjectId | None:
        return mongo_converter.convert_to_object_id(value)

    def create(self, doc: dict) -> dict:
        result = self.collection.insert_one(doc)
        return self.find_by_id(result.inserted_id)

    def save(self, doc: dict) -> dict:
        self.collection.replace_one(
            {"_id": self._oid(doc["_id"])},
            doc,
            upsert=True,
        )
        return self.find_by_id(doc["_id"])

    def find_by_id(self, employee_id) -> dict:
        oid = self._oid(employee_id)
        doc = self.collection.find_one({
            "_id": oid,
            "lifecycle.deleted_at": None,
        })
        if not doc:
            raise EmployeeNotFoundException(str(employee_id))
        return doc

    def find_by_id_including_deleted(self, employee_id) -> dict:
        oid = self._oid(employee_id)
        doc = self.collection.find_one({"_id": oid})
        if not doc:
            raise EmployeeNotFoundException(str(employee_id))
        return doc

    def find_by_user_id(self, user_id) -> dict | None:
        oid = self._oid(user_id)
        if not oid:
            return None

        return self.collection.find_one({
            "user_id": oid,
            "lifecycle.deleted_at": None,
        })

    def find_by_employee_code(self, employee_code: str) -> dict | None:
        code = (employee_code or "").strip()
        if not code:
            return None

        return self.collection.find_one({
            "employee_code": code,
            "lifecycle.deleted_at": None,
        })

    def update_fields(self, employee_id, fields: dict) -> dict:
        oid = self._oid(employee_id)
        self.collection.update_one({"_id": oid}, {"$set": fields})
        return self.find_by_id_including_deleted(oid)

    def create_with_session(self, doc: dict, session=None) -> dict:
        result = self.collection.insert_one(doc, session=session)
        return self.collection.find_one({"_id": result.inserted_id}, session=session)

    def link_user_if_empty_with_session(
        self,
        *,
        employee_id,
        user_id,
        session=None,
    ) -> dict | None:
        employee_oid = self._oid(employee_id)
        user_oid = self._oid(user_id)

        return self.collection.find_one_and_update(
            {
                "_id": employee_oid,
                "user_id": None,
                "lifecycle.deleted_at": None,
            },
            {
                "$set": {
                    "user_id": user_oid,
                }
            },
            session=session,
            return_document=ReturnDocument.AFTER,
        )