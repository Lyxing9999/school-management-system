import type { ApiResponse } from "~/api/types/common/api-response.type";

export type NotificationDTO = {
  id: string;
  user_id: string;
  role: string;
  type: NotifType;
  title: string;
  message?: string | null;
  entity_type?: string | null;
  entity_id?: string | null;
  data?: Record<string, any>;
  read_at?: string | null;
  created_at?: string | null;
};

export type NotificationListDTO = { items: NotificationDTO[] };
export type UnreadCountDTO = { unread: number };

export type NotificationListResponse = ApiResponse<NotificationListDTO>;
export type UnreadCountResponse = ApiResponse<UnreadCountDTO>;
export type OkResponse = ApiResponse<{ ok: boolean }>;

export type NotifType =
  | "CLASS_ASSIGNMENT"
  | "CLASS_UNASSIGNED"
  | "CLASS_ENROLLED"
  | "CLASS_REMOVED"
  | "SCHEDULE_ASSIGNED"
  | "SCHEDULE_UPDATED"
  | "GRADE_PUBLISHED"
  | "ANNOUNCEMENT"
  | "HRMS_LEAVE_SUBMITTED"
  | "HRMS_LEAVE_APPROVED"
  | "HRMS_LEAVE_REJECTED"
  | "HRMS_LEAVE_CANCELLED"
  | "HRMS_OVERTIME_SUBMITTED"
  | "HRMS_OVERTIME_APPROVED"
  | "HRMS_OVERTIME_REJECTED"
  | "HRMS_OVERTIME_CANCELLED"
  | "HRMS_PAYROLL_GENERATED"
  | "HRMS_PAYROLL_FINALIZED"
  | "HRMS_PAYROLL_MARKED_PAID"
  | "HRMS_PAYSLIP_READY"
  | "HRMS_ATTENDANCE_WRONG_LOCATION_APPROVED"
  | "HRMS_ATTENDANCE_WRONG_LOCATION_REJECTED"
  | "HRMS_ATTENDANCE_EARLY_LEAVE_APPROVED"
  | "HRMS_ATTENDANCE_EARLY_LEAVE_REJECTED";
