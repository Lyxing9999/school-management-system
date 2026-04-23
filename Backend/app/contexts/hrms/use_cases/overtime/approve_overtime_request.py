
from __future__ import annotations




class ApproveOvertimeRequestUseCase:
    def __init__(self, *, overtime_repository) -> None:
        self.overtime_repository = overtime_repository

    def execute(
        self,
        *,
        overtime_id,
        manager_id,
        approved_hours: float | None = None,
        comment: str | None = None,
    ):
        ot = self.overtime_repository.find_by_id(overtime_id)

        ot.approve(
            manager_id=manager_id,
            approved_hours=approved_hours,
            comment=comment,
        )

        return self.overtime_repository.save(ot)