from __future__ import annotations

from app.contexts.hrms.errors.employee_exceptions import (
    EmployeeLinkedAccountRequiredException,
)


class SoftDeleteEmployeeAccountUseCase:
    def __init__(self, *, employee_repository, iam_gateway) -> None:
        self.employee_repository = employee_repository
        self.iam_gateway = iam_gateway

    def execute(self, *, employee_id: str, actor_id: str) -> None:
        employee = self.employee_repository.find_by_id(employee_id)

        user_id = employee.get("user_id")
        if not user_id:
            raise EmployeeLinkedAccountRequiredException(str(employee["_id"]))

        self.iam_gateway.soft_delete_user(
            user_id=user_id,
            actor_id=actor_id,
        )