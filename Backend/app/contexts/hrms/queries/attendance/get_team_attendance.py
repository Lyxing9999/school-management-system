from __future__ import annotations


class GetTeamAttendanceQuery:
    def __init__(self, *, employee_read_model, attendance_read_model) -> None:
        self.employee_read_model = employee_read_model
        self.attendance_read_model = attendance_read_model

    def execute(
        self,
        *,
        manager_user_id,
        status: str | None = None,
        start_date=None,
        end_date=None,
        page: int = 1,
        page_size: int = 10,
    ):
        employees, _ = self.employee_read_model.list_employees(
            manager_user_id=manager_user_id,
            page=1,
            limit=1000,
        )

        employee_ids = [item["_id"] for item in employees]
        if not employee_ids:
            return [], 0

        return self.attendance_read_model.list_attendances(
            employee_ids=employee_ids,
            start_date=start_date,
            end_date=end_date,
            status=status,
            page=page,
            limit=page_size,
        )