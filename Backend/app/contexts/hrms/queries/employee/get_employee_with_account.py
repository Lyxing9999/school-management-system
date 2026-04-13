
from __future__ import annotations

from app.contexts.hrms.errors.employee_exceptions import EmployeeNotFoundException


class GetEmployeeWithAccountQuery:
    def __init__(self, *, employee_read_model, iam_gateway) -> None:
        self.employee_read_model = employee_read_model
        self.iam_gateway = iam_gateway

    def execute(self, *, employee_id: str):
        employee = self.employee_read_model.get_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundException(employee_id)

        user_id = employee.get("user_id")
        account = None

        if user_id:
            account = self.iam_gateway.get_account_summary_by_user_id(user_id)

        return {
            "employee": employee,
            "account": account,
        }