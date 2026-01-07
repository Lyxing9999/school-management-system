from pydantic import BaseModel, ConfigDict, Field
from typing import Generic, List, Optional, TypeVar, Dict, Any
import datetime as dt

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


class NotificationDTO(BaseDTO):
    id: Optional[str] = None
    user_id: str
    role: str
    type: str
    title: str
    message: Optional[str] = None

    entity_type: Optional[str] = None
    entity_id: Optional[str] = None

    data: Dict[str, Any] = Field(default_factory=dict)

    read_at: Optional[str] = None
    created_at: Optional[str] = None
    
class NotificationListDTO(ItemListDTO[NotificationDTO]):
    pass


class UnreadCountDTO(BaseDTO):
    unread: int = 0