from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from bson import ObjectId


def now_utc() -> datetime:
    return datetime.utcnow()


@dataclass
class Lifecycle:
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)
    deleted_at: datetime | None = None
    deleted_by: ObjectId | None = None

    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def touch(self, now: datetime | None = None) -> None:
        self.updated_at = now or now_utc()

    def soft_delete(self, actor_id: ObjectId, now: datetime | None = None) -> bool:
        if self.is_deleted():
            return False
        n = now or now_utc()
        self.deleted_at = n
        self.deleted_by = actor_id
        self.updated_at = n
        return True

    def restore(self, now: datetime | None = None) -> None:
        n = now or now_utc()
        self.deleted_at = None
        self.deleted_by = None
        self.updated_at = n