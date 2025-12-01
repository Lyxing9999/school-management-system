# TODO: implement enrollment on Version 2 
# from __future__ import annotations
# from bson import ObjectId
# from pymongo.database import Database
# from pymongo.collection import Collection


# class EnrollmentReadModel:
#     """
#     Read model to answer questions like:
#     - Is student X enrolled in class Y?
#     """

#     def __init__(self, db: Database):
#         self.collection: Collection = db["enrollments"]

#     def is_student_enrolled(self, student_id: ObjectId, class_id: ObjectId) -> bool:
#         """
#         Returns True if student has an ACTIVE enrollment in this class.
#         """
#         doc = self.collection.find_one(
#             {
#                 "student_id": student_id,
#                 "class_id": class_id,
#                 "status": "active",
#             }
#         )
#         return doc is not None