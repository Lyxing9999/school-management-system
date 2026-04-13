from __future__ import annotations

from app.contexts.hrms.errors.employee_exceptions import EmployeeNotFoundException


class GetMyEmployeeProfileQuery:
    def __init__(self, *, employee_read_model) -> None:
        self.employee_read_model = employee_read_model

    def execute(self, *, user_id):
        employee = self.employee_read_model.find_by_user_id(user_id)
        if not employee:
            raise EmployeeNotFoundException(str(user_id))
        return employee