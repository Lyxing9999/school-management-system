from __future__ import annotations


class GetWrongLocationReportQuery:
    def __init__(self, *, attendance_read_model) -> None:
        self.attendance_read_model = attendance_read_model

    def execute(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        start_date=None,
        end_date=None,
        review_status: str | None = None,
    ):
        return self.attendance_read_model.list_wrong_location_cases(
            start_date=start_date,
            end_date=end_date,
            review_status=review_status,
            page=page,
            limit=page_size,
        )