from __future__ import annotations
from app.contexts.core.config.setting import settings


from pymongo.database import Database

from app.contexts.hrms.repositories.employee_repository import MongoEmployeeRepository
from app.contexts.hrms.repositories.attendance_repository import MongoAttendanceRepository
from app.contexts.hrms.repositories.working_schedule_repository import MongoWorkingScheduleRepository
from app.contexts.hrms.repositories.work_location_repository import MongoWorkLocationRepository
from app.contexts.hrms.repositories.overtime_repository import MongoOvertimeRepository
from app.contexts.hrms.repositories.leave_repository import MongoLeaveRepository
from app.contexts.hrms.repositories.public_holiday_repository import MongoPublicHolidayRepository
from app.contexts.hrms.repositories.deduction_rule_repository import MongoDeductionRuleRepository
from app.contexts.hrms.repositories.payroll_repository import MongoPayrollRunRepository
from app.contexts.hrms.repositories.payslip_repository import MongoPayslipRepository
from app.contexts.hrms.repositories.audit_log_repository import MongoAuditLogRepository
from app.contexts.hrms.integrations.iam_gateway import HRMSIamGateway
from app.contexts.hrms.services.cambodia_public_holiday_provider import CambodiaPublicHolidayProvider
from app.contexts.hrms.read_models.overtime_read_model import OvertimeReadModel
from app.contexts.hrms.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.hrms.read_models.employee_read_model import EmployeeReadModel
from app.contexts.hrms.read_models.working_schedule_read_model import WorkingScheduleReadModel
from app.contexts.hrms.read_models.work_location_read_model import WorkLocationReadModel


class HrmsRepositories:
    def __init__(self, *, db: Database) -> None:
        self.db = db
        self.employee_repository = MongoEmployeeRepository(db)
        self.attendance_repository = MongoAttendanceRepository(db)
        self.working_schedule_repository = MongoWorkingScheduleRepository(db)
        self.work_location_repository = MongoWorkLocationRepository(db)
        self.overtime_repository = MongoOvertimeRepository(db)
        self.leave_repository = MongoLeaveRepository(db)
        self.public_holiday_repository = MongoPublicHolidayRepository(db)
        self.deduction_rule_repository = MongoDeductionRuleRepository(db)
        self.payroll_run_repository = MongoPayrollRunRepository(db)
        self.payslip_repository = MongoPayslipRepository(db)
        self.audit_log_repository = MongoAuditLogRepository(db)
        self.iam_gateway = HRMSIamGateway(db)
        self.overtime_read_model = OvertimeReadModel(db)
        self.attendance_read_model = AttendanceReadModel(db)
        self.employee_read_model = EmployeeReadModel(db)
        self.working_schedule_read_model = WorkingScheduleReadModel(db)
        self.work_location_read_model = WorkLocationReadModel(db)
        self.cambodia_public_holiday_provider = CambodiaPublicHolidayProvider(
        api_key=settings.CALENDARIFIC_API_KEY or "",
        )
