# app/contexts/hrms/errors/deduction_exceptions.py
from app.contexts.core.errors import AppBaseException


class DeductionRuleNotFoundException(AppBaseException):
    def __init__(self, rule_id: str):
        super().__init__(
            message=f"Deduction rule with ID '{rule_id}' not found",
            error_code="DEDUCTION_RULE_NOT_FOUND",
            status_code=404,
            user_message="Deduction rule not found.",
        )


class InvalidDeductionRangeException(AppBaseException):
    def __init__(self, min_minutes: int, max_minutes: int):
        super().__init__(
            message=f"Invalid deduction range: min={min_minutes}, max={max_minutes}. Max must be >= min and both must be >= 0",
            error_code="INVALID_DEDUCTION_RANGE",
            status_code=400,
            user_message="Invalid deduction range provided.",
        )


class InvalidDeductionPercentageException(AppBaseException):
    def __init__(self, percentage: float):
        super().__init__(
            message=f"Invalid deduction percentage: {percentage}%. Must be between 0 and 100",
            error_code="INVALID_DEDUCTION_PERCENTAGE",
            status_code=400,
            user_message="Deduction percentage must be between 0 and 100.",
        )


class DeductionRuleDeletedException(AppBaseException):
    def __init__(self, rule_id: str):
        super().__init__(
            message=f"Deduction rule '{rule_id}' has been deleted",
            error_code="DEDUCTION_RULE_DELETED",
            status_code=410,
            user_message="Deduction rule has been deleted.",
        )


class DeductionMinMinutesNegativeException(AppBaseException):
    def __init__(self, min_minutes: int):
        super().__init__(
            message="min_minutes cannot be negative",
            error_code="DEDUCTION_MIN_MINUTES_NEGATIVE",
            status_code=400,
            user_message="Minimum minutes cannot be negative.",
            details={"min_minutes": min_minutes},
        )
