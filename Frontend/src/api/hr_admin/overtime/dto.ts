import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export type OvertimeRequestStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "cancelled";

export type OvertimeDayType = "working_day" | "weekend" | "public_holiday";

/**
 * Overtime request data transfer object
 */
export interface OvertimeRequestDTO {
  id: string;
  employee_id: string;
  employee_name?: string | null;
  request_date: string;
  start_time: string;
  end_time: string;
  schedule_end_time: string;
  reason: string;
  day_type: OvertimeDayType;
  basic_salary: number;
  submitted_at: string;
  status: OvertimeRequestStatus;
  manager_id: string | null;
  manager_user_id?: string | null;
  manager_name?: string | null;
  manager_comment: string | null;
  approved_hours: number;
  calculated_payment: number;
  created_by?: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  lifecycle: LifecycleDTO;
}

/**
 * DTO for creating a new overtime request
 * POST /api/hrms/overtime-requests
 */
export interface OvertimeRequestCreateDTO {
  request_date: string;
  start_time: string;
  end_time: string;
  reason: string;
}

/**
 * DTO for approving an overtime request
 * POST /api/hrms/overtime-requests/<overtime_id>/approve
 */
export interface OvertimeApproveDTO {
  approved_hours: number;
  comment?: string | null;
}

/**
 * DTO for rejecting an overtime request
 * POST /api/hrms/overtime-requests/<overtime_id>/reject
 */
export interface OvertimeRejectDTO {
  comment: string;
}

/**
 * DTO for cancelling an overtime request
 * POST /api/hrms/overtime-requests/<overtime_id>/cancel
 */
export interface OvertimeCancelDTO {
  reason?: string | null;
}

/**
 * List parameters for overtime requests
 * GET /api/hrms/overtime-requests
 * GET /api/hrms/overtime-requests/my
 */
export interface OvertimeRequestListParams {
  employee_id?: string;
  status?: OvertimeRequestStatus;
  page?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
  signal?: AbortSignal;
}

/**
 * Paginated overtime request list response
 */
export interface OvertimeRequestListResponseDTO {
  items: OvertimeRequestDTO[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

/**
 * My overtime summary
 * GET /api/hrms/overtime-requests/my-summary
 */
export interface MyOvertimeSummaryDTO {
  total_requests: number;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
  cancelled_count: number;
  approved_hours: number;
  approved_payment: number;
}

/**
 * Payroll approved overtime summary
 * GET /api/hrms/overtime-requests/payroll-summary
 */
export interface OvertimePayrollSummaryDTO {
  total_approved_requests: number;
  total_approved_hours: number;
  total_approved_payment: number;
}
