# # app/contexts/school/tests/mapper/test_enrollment_mapper.py

# from datetime import datetime
# from bson import ObjectId

# from app.contexts.school.domain.enrollment import Enrollment, EnrollmentStatus
# from app.contexts.school.mapper.enrollment_mapper import EnrollmentMapper


# def test_to_domain_from_full_dict():
#     enrollment_id = ObjectId()
#     student_id = ObjectId()
#     class_id = ObjectId()
#     enrolled_at = datetime(2025, 1, 1, 8, 0, 0)
#     dropped_at = datetime(2025, 2, 1, 8, 0, 0)
#     completed_at = None
#     created_at = datetime(2025, 1, 1, 7, 0, 0)
#     updated_at = datetime(2025, 2, 1, 9, 0, 0)

#     data = {
#         "_id": enrollment_id,
#         "student_id": student_id,
#         "class_id": class_id,
#         "status": "dropped",
#         "enrolled_at": enrolled_at,
#         "dropped_at": dropped_at,
#         "completed_at": completed_at,
#         "created_at": created_at,
#         "updated_at": updated_at,
#     }

#     enrollment = EnrollmentMapper.to_domain(data)

#     assert isinstance(enrollment, Enrollment)
#     assert enrollment.id == enrollment_id
#     assert enrollment.student_id == student_id
#     assert enrollment.class_id == class_id
#     assert enrollment.status == EnrollmentStatus.DROPPED
#     assert enrollment.enrolled_at == enrolled_at
#     assert enrollment.dropped_at == dropped_at
#     assert enrollment.completed_at is None
#     assert enrollment.created_at == created_at
#     assert enrollment.updated_at == updated_at


# def test_to_domain_uses_default_status_when_missing():
#     student_id = ObjectId()
#     class_id = ObjectId()

#     data = {
#         "_id": ObjectId(),
#         "student_id": student_id,
#         "class_id": class_id,
#         # no "status" field
#     }

#     enrollment = EnrollmentMapper.to_domain(data)

#     assert enrollment.student_id == student_id
#     assert enrollment.class_id == class_id
#     assert enrollment.status == EnrollmentStatus.ACTIVE


# def test_to_domain_when_input_is_already_domain_returns_same_instance():
#     student_id = ObjectId()
#     class_id = ObjectId()

#     original = Enrollment(
#         student_id=student_id,
#         class_id=class_id,
#         status=EnrollmentStatus.ACTIVE,
#     )

#     result = EnrollmentMapper.to_domain(original)

#     assert result is original


# def test_to_persistence_builds_correct_dict():
#     student_id = ObjectId()
#     class_id = ObjectId()
#     enrollment = Enrollment(
#         student_id=student_id,
#         class_id=class_id,
#         status=EnrollmentStatus.COMPLETED,
#     )

#     enrollment.completed_at = datetime(2025, 3, 1, 10, 0, 0)
#     enrollment.dropped_at = None

#     data = EnrollmentMapper.to_persistence(enrollment)

#     assert data["_id"] == enrollment.id
#     assert data["student_id"] == student_id
#     assert data["class_id"] == class_id
#     assert data["status"] == "completed"
#     assert data["enrolled_at"] == enrollment.enrolled_at
#     assert data["dropped_at"] is None
#     assert data["completed_at"] == enrollment.completed_at
#     assert data["created_at"] == enrollment.created_at
#     assert data["updated_at"] == enrollment.updated_at


# def test_round_trip_dict_to_domain_and_back():
#     enrollment_id = ObjectId()
#     student_id = ObjectId()
#     class_id = ObjectId()
#     enrolled_at = datetime(2025, 1, 1, 8, 0, 0)
#     created_at = datetime(2025, 1, 1, 7, 0, 0)
#     updated_at = datetime(2025, 1, 1, 9, 0, 0)

#     data = {
#         "_id": enrollment_id,
#         "student_id": student_id,
#         "class_id": class_id,
#         "status": "active",
#         "enrolled_at": enrolled_at,
#         "dropped_at": None,
#         "completed_at": None,
#         "created_at": created_at,
#         "updated_at": updated_at,
#     }

#     enrollment = EnrollmentMapper.to_domain(data)
#     persisted = EnrollmentMapper.to_persistence(enrollment)

#     assert persisted["_id"] == enrollment_id
#     assert persisted["student_id"] == student_id
#     assert persisted["class_id"] == class_id
#     assert persisted["status"] == "active"
#     assert persisted["enrolled_at"] == enrolled_at
#     assert persisted["dropped_at"] is None
#     assert persisted["completed_at"] is None
#     assert persisted["created_at"] == created_at
#     assert persisted["updated_at"] == updated_at