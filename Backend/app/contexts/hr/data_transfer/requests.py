# from pydantic import BaseModel
# from app.contexts.shared.enum.roles import StaffRole
# from bson import ObjectId



# class HRCreateStaffRequestSchema(BaseModel):
#     staff_id: str
#     staff_name: str
#     role: StaffRole
#     phone_number: str
#     email: str
#     password: str
#     address: str | None = None

#     model_config = {
#          "enum_values_as_str": True,
#     }
# class HRUpdateStaffRequestSchema(BaseModel):
#     staff_id: str | ObjectId | None = None
#     staff_name: str | None = None
#     role: StaffRole | None = None
#     phone_number: str | None = None
#     email: str | None = None
#     password: str | None = None
#     address: str | None = None
#     model_config = {
#         "arbitrary_types_allowed": True,
#         "enum_values_as_str": True,
#     }