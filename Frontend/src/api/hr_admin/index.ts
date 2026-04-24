import { EmployeeApi } from "~/api/hr_admin/employees/api";
import { EmployeeService } from "~/api/hr_admin/employees/service";
import { WorkingScheduleApi } from "./schedule";
import { WorkingScheduleService } from "./schedule";
import { WorkLocationApi, WorkLocationService } from "./workLocations";
import { AttendanceApi, AttendanceService } from "./attendance";
import { PublicHolidayApi, PublicHolidayService } from "./publicHoliday";
import { OvertimeRequestApi } from "./overtime/api";
import { OvertimeRequestService } from "./overtime/service";
import { LeaveRequestApi } from "./leave/api";
import { LeaveRequestService } from "./leave/service";
import { AuditLogApi } from "./audit/api";
import { AuditLogService } from "./audit/service";
import { DeductionRuleApi } from "./deduction/api";
import { DeductionRuleService } from "./deduction/service";
import { PayrollRunApi } from "./payroll/api";
import { PayrollRunService } from "./payroll/service";
let _hrmsAdminService: ReturnType<typeof createHrmsAdminService> | null = null;

function createHrmsAdminService() {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is undefined.");

  const hrmsApi = {
    employee: new EmployeeApi($api),
    workingSchedule: new WorkingScheduleApi($api),
    workLocation: new WorkLocationApi($api),
    attendance: new AttendanceApi($api),
    publicHoliday: new PublicHolidayApi($api),
    overtimeRequest: new OvertimeRequestApi($api),
    leaveRequest: new LeaveRequestApi($api),
    auditLog: new AuditLogApi($api),
    deductionRule: new DeductionRuleApi($api),
    payrollRun: new PayrollRunApi($api),
  };

  return {
    employee: new EmployeeService(hrmsApi.employee),
    workingSchedule: new WorkingScheduleService(hrmsApi.workingSchedule),
    workLocation: new WorkLocationService(hrmsApi.workLocation),
    attendance: new AttendanceService(hrmsApi.attendance),
    publicHoliday: new PublicHolidayService(hrmsApi.publicHoliday),
    overtimeRequest: new OvertimeRequestService(hrmsApi.overtimeRequest),
    leaveRequest: new LeaveRequestService(hrmsApi.leaveRequest),
    auditLog: new AuditLogService(hrmsApi.auditLog),
    deductionRule: new DeductionRuleService(hrmsApi.deductionRule),
    payrollRun: new PayrollRunService(hrmsApi.payrollRun),
  };
}

export const hrmsAdminService = () =>
  (_hrmsAdminService ??= createHrmsAdminService());
