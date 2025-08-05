from typing import Generic, TypeVar
from pydantic import BaseModel

R = TypeVar('R')

class BaseResponseDTO(BaseModel, Generic[R]):
    data: R | None = None
    message: str
    success: bool

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
    }