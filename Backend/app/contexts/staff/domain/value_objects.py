from dataclasses import dataclass


@dataclass(frozen=True)
class StaffName:
    value: str
    def __post_init__(self):
        v = (self.value or "").strip()
        if not v:
            raise ValueError("staff_name is required")
        object.__setattr__(self, "value", v)

@dataclass(frozen=True)
class PhoneNumber:
    value: str
    def __post_init__(self):
        v = (self.value or "").strip()
        if v and len(v) < 6:
            raise ValueError("phone_number too short")
        object.__setattr__(self, "value", v)