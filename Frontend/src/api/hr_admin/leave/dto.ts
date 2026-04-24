import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export type LeaveType = "annual" | "sick" | "unpaid" | "other";

export type LeaveRequestStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "cancelled";

/**
 * Leave request data transfer object
 */
export interface LeaveRequestDTO {
  id: string;
  employee_id: string;
  employee_name?: string | null;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  reason: string;
  contract_start: string;
  contract_end: string;
  is_paid: boolean;
  status: LeaveRequestStatus;
  manager_user_id: string | null;
  manager_name?: string | null;
  manager_comment: string | null;
  created_by?: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  total_days: number;
  lifecycle: LifecycleDTO;
}

/**
 * DTO for submitting a leave request
 * POST /api/hrms/leave-requests
 */
export interface LeaveSubmitDTO {
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  reason: string;
}

/**
 * DTO for approving a leave request
 * POST /api/hrms/leave-requests/<leave_id>/approve
 */
export interface LeaveApproveDTO {
  comment?: string | null;
}

/**
 * DTO for rejecting a leave request
 * POST /api/hrms/leave-requests/<leave_id>/reject
 */
export interface LeaveRejectDTO {
  comment?: string | null;
}

/**
 * List parameters for leave requests
 * GET /api/hrms/leave-requests
 * GET /api/hrms/leave-requests/my
 */
export interface LeaveRequestListParams {
  employee_id?: string;
  status?: LeaveRequestStatus;
  start_date?: string;
  end_date?: string;
  include_deleted?: boolean;
  deleted_only?: boolean;
  page?: number;
  limit?: number;
  signal?: AbortSignal;
}

/**
 * Paginated leave request list response
 */
export interface LeaveRequestListResponseDTO {
  items: LeaveRequestDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * My leave summary
 * GET /api/hrms/leave-requests/my-summary
 */
export interface LeaveSummaryDTO {
  total_requests: number;
  pending: number;
  approved: number;
  rejected: number;
  cancelled: number;
  total_approved_days: number;
}

/**
 * My leave balance
 * GET /api/hrms/leave-requests/my-balance
 */
export interface LeaveBalanceDTO {
  annual_entitlement: number;
  used_days: number;
  remaining_days: number;
}

export interface LeaveBalanceItemDTO {
  employee_id: string;
  employee_name?: string | null;
  employee_code?: string | null;
  department?: string | null;
  position?: string | null;
  employee_status?: string | null;
  manager_user_id?: string | null;
  manager_name?: string | null;
  annual_entitlement: number;
  used_days: number;
  remaining_days: number;
  pending_days: number;
  approved_days: number;
  approved_annual_days: number;
  approved_sick_days: number;
  approved_unpaid_days: number;
  approved_other_days: number;
  last_approved_end_date?: string | null;
}

export interface LeaveBalanceListParams {
  page?: number;
  limit?: number;
  q?: string;
  employee_id?: string;
  signal?: AbortSignal;
}

export interface LeaveBalanceListResponseDTO {
  items: LeaveBalanceItemDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
