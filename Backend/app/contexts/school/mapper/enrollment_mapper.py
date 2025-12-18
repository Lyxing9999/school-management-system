# app/contexts/school/mapper/enrollment_mapper.py

# from app.contexts.school.domain.enrollment import Enrollment, EnrollmentStatus


# class EnrollmentMapper:
#     """
#     Handles conversion between Enrollment domain model and MongoDB dict.
#     """

#     @staticmethod
#     def to_domain(data: dict | Enrollment) -> Enrollment:
#         if isinstance(data, Enrollment):
#             return data

#         return Enrollment(
#             id=data.get("_id"),
#             student_id=data["student_id"],
#             class_id=data["class_id"],
#             status=data.get("status", EnrollmentStatus.ACTIVE),
#             enrolled_at=data.get("enrolled_at"),
#             dropped_at=data.get("dropped_at"),
#             completed_at=data.get("completed_at"),
#             created_at=data.get("created_at"),
#             updated_at=data.get("updated_at"),
#         )

#     @staticmethod
#     def to_persistence(enrollment: Enrollment) -> dict:
#         return {
#             "_id": enrollment.id,
#             "student_id": enrollment.student_id,
#             "class_id": enrollment.class_id,
#             "status": enrollment.status.value,
#             "enrolled_at": enrollment.enrolled_at,
#             "dropped_at": enrollment.dropped_at,
#             "completed_at": enrollment.completed_at,
#             "created_at": enrollment.created_at,
#             "updated_at": enrollment.updated_at,
#         }