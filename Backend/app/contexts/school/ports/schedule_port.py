from typing import Protocol, Optional, Any

class SchedulePort(Protocol):
    def class_has_active_schedule(self, class_id: Any, *, session: Optional[Any] = None) -> bool:
        ...