from __future__ import annotations


class ListAuditLogsQuery:
    def __init__(self, *, audit_log_repository) -> None:
        self.audit_log_repository = audit_log_repository

    def execute(
        self,
        *,
        entity_type: str | None = None,
        entity_id=None,
        actor_id=None,
        action: str | None = None,
        start_at=None,
        end_at=None,
        include_deleted: bool = False,
        page: int = 1,
        page_size: int = 20,
    ):
        return self.audit_log_repository.list_logs(
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            action=action,
            start_at=start_at,
            end_at=end_at,
            include_deleted=include_deleted,
            page=page,
            limit=page_size,
        )
