import type { NotifType } from "~/api/notifications/notification.dto";

export const NOTIF_TYPE_OPTIONS: { label: string; value: NotifType }[] = [
  { label: "Class Assigned", value: "CLASS_ASSIGNMENT" },
  { label: "Class Unassigned", value: "CLASS_UNASSIGNED" },
  { label: "Class Enrolled", value: "CLASS_ENROLLED" },
  { label: "Class Removed", value: "CLASS_REMOVED" },
  { label: "Schedule Assigned", value: "SCHEDULE_ASSIGNED" },
  { label: "Schedule Updated", value: "SCHEDULE_UPDATED" },
  { label: "Grade Published", value: "GRADE_PUBLISHED" },
  { label: "Announcement", value: "ANNOUNCEMENT" },
  { label: "HRMS Leave Submitted", value: "HRMS_LEAVE_SUBMITTED" },
  { label: "HRMS Leave Approved", value: "HRMS_LEAVE_APPROVED" },
  { label: "HRMS Leave Rejected", value: "HRMS_LEAVE_REJECTED" },
  { label: "HRMS Leave Cancelled", value: "HRMS_LEAVE_CANCELLED" },
  { label: "HRMS OT Submitted", value: "HRMS_OVERTIME_SUBMITTED" },
  { label: "HRMS OT Approved", value: "HRMS_OVERTIME_APPROVED" },
  { label: "HRMS OT Rejected", value: "HRMS_OVERTIME_REJECTED" },
  { label: "HRMS OT Cancelled", value: "HRMS_OVERTIME_CANCELLED" },
  { label: "HRMS Payroll Generated", value: "HRMS_PAYROLL_GENERATED" },
  { label: "HRMS Payroll Finalized", value: "HRMS_PAYROLL_FINALIZED" },
  { label: "HRMS Payroll Marked Paid", value: "HRMS_PAYROLL_MARKED_PAID" },
  { label: "HRMS Payslip Ready", value: "HRMS_PAYSLIP_READY" },
  {
    label: "HRMS Wrong Location Approved",
    value: "HRMS_ATTENDANCE_WRONG_LOCATION_APPROVED",
  },
  {
    label: "HRMS Wrong Location Rejected",
    value: "HRMS_ATTENDANCE_WRONG_LOCATION_REJECTED",
  },
  {
    label: "HRMS Early Leave Approved",
    value: "HRMS_ATTENDANCE_EARLY_LEAVE_APPROVED",
  },
  {
    label: "HRMS Early Leave Rejected",
    value: "HRMS_ATTENDANCE_EARLY_LEAVE_REJECTED",
  },
];
