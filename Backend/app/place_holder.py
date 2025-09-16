from pydantic import BaseModel

class PlaceholderModel(BaseModel):
    model_config = {
        "extra": "allow"  # allow extra fields
    }

    def __getattr__(self, item):
        # If attribute exists in extra fields, return it
        return self.model_dump().get(item, None)