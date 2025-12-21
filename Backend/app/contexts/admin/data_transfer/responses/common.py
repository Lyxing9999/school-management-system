import datetime as dt
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        use_enum_values=True,
    )


class NameSelectDTO(BaseDTO):
    id: Optional[str] = None
    name: Optional[str] = None


class OptionDTO(BaseDTO):
    value: str
    label: str


T = TypeVar("T")


class ItemListDTO(BaseDTO, Generic[T]):
    items: List[T] = Field(default_factory=list)


class PaginatedDTO(BaseDTO, Generic[T]):
    items: List[T] = Field(default_factory=list)
    total: int
    page: int
    page_size: int
    total_pages: int


class LifecycleDTO(BaseDTO):
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None
    deleted_at: Optional[dt.datetime] = None
    deleted_by: Optional[str] = None