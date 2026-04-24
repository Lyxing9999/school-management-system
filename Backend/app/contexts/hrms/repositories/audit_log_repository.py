from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.mapper.audit_log_mapper import AuditLogMapper


class MongoAuditLogRepository:
    def __init__(self, db: Database):
        self.collection = db["hr_audit_logs"]
        self.mapper = AuditLogMapper()

    def save(self, audit_log: AuditLog) -> AuditLog:
        doc = self.mapper.to_persistence(audit_log)
        self.collection.insert_one(doc)
        return audit_log

    def list_logs(
        self,
        *,
        entity_type: str | None = None,
        entity_id: ObjectId | None = None,
        actor_id: ObjectId | None = None,
        action: str | None = None,
        start_at=None,
        end_at=None,
        include_deleted: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[AuditLog], int]:
        query = {}

        if entity_type:
            query["entity_type"] = entity_type
        if entity_id:
            query["entity_id"] = entity_id
        if actor_id:
            query["actor_id"] = actor_id
        if action:
            query["action"] = str(action).strip().lower()
        if start_at or end_at:
            query["action_at"] = {}
            if start_at is not None:
                query["action_at"]["$gte"] = start_at
            if end_at is not None:
                query["action_at"]["$lte"] = end_at
        if not include_deleted:
            query["lifecycle.deleted_at"] = None

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit

        docs = (
            self.collection.find(query)
            .sort("action_at", -1)
            .skip(skip)
            .limit(limit)
        )

        return [self.mapper.to_domain(doc) for doc in docs], total
