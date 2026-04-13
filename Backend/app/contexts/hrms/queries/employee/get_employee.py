from __future__ import annotations

from app.contexts.hrms.errors.employee_exceptions import EmployeeNotFoundException


class GetEmployeeQuery:
    def __init__(self, *, employee_read_model) -> None:
        self.employee_read_model = employee_read_model

    def execute(self, *, employee_id: str):
        employee = self.employee_read_model.get_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundException(employee_id)
        return employee