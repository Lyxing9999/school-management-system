from __future__ import annotations

from bson import ObjectId
from app.contexts.shared.model_converter import mongo_converter

class OidMixin:
    def _oid(self, value: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(value)