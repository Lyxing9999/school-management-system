from __future__ import annotations


class FindEmployeeByUserIdQuery:
    def __init__(self, *, employee_read_model) -> None:
        self.employee_read_model = employee_read_model

    def execute(self, *, user_id):
        return self.employee_read_model.find_by_user_id(user_id)