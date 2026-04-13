from __future__ import annotations


class GetMyAttendanceQuery:
    def __init__(self, *, attendance_read_model) -> None:
        self.attendance_read_model = attendance_read_model

    def execute(
        self,
        *,
        employee_id,
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
        start_date=None,
        end_date=None,
    ):
        return self.attendance_read_model.list_attendances(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            page=page,
            limit=page_size,
        )