from pydantic import Field
from app.schemas.classes.class_create_schema import ClassCreateSchema
from app.schemas.classes.class_update_schema import ClassUpdateSchema
from app.utils.pyobjectid import PyObjectId 

class AdminClassCreateSchema(ClassCreateSchema):
    created_by: PyObjectId = Field(..., description="The admin who created the class", alias="created_by_admin_id")

    model_config = {
        **ClassCreateSchema.model_config,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str},
        "populate_by_name": True,
    }


class AdminClassUpdateSchema(ClassUpdateSchema):
    updated_by: PyObjectId = Field(..., description="The admin who updated the class", alias="updated_by_admin_id")

    model_config = {
        **ClassUpdateSchema.model_config,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str},
        "populate_by_name": True,
    }