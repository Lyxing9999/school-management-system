from __future__ import annotations


class SoftDeleteEmployeeUseCase:
    def __init__(self, *, employee_repository) -> None:
        self.employee_repository = employee_repository

    def execute(self, *, employee_id: str, actor_id):
        return self.employee_repository.soft_delete(
            employee_id,
            deleted_by=actor_id,
        )