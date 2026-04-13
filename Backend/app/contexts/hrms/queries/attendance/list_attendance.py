from __future__ import annotations


class ListAttendanceQuery:
    def __init__(self, *, attendance_read_model) -> None:
        self.attendance_read_model = attendance_read_model

    def execute(
        self,
        *,
        employee_id=None,
        status: str | None = None,
        start_date=None,
        end_date=None,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
        deleted_only: bool = False,
    ):
        return self.attendance_read_model.list_attendances(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            include_deleted=include_deleted,
            deleted_only=deleted_only,
            page=page,
            limit=page_size,
        )