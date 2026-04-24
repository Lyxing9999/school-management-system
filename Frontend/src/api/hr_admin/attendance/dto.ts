import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export type AttendanceStatus =
  | "checked_in"
  | "checked_out"
  | "late"
  | "early_leave"
  | "absent"
  | "wrong_location_pending"
  | "wrong_location_approved"
  | "wrong_location_rejected";

export type AttendanceDayType = "working_day" | "weekend" | "public_holiday";

export interface AttendanceDTO {
  id: string;
  employee_id: string;
  employee_name?: string | null;
  attendance_date: string; // YYYY-MM-DD

  check_in_time: string | null;
  check_out_time: string | null;

  schedule_id: string | null;
  schedule_name?: string | null;
  location_id: string | null;
  location_name?: string | null;

  check_in_latitude: number | null;
  check_in_longitude: number | null;
  check_out_latitude: number | null;
  check_out_longitude: number | null;

  day_type: AttendanceDayType;
  is_ot_eligible: boolean;
  status: string;

  notes?: string | null;
  late_minutes: number;
  early_leave_minutes: number;

  wrong_location_reason?: string | null;
  location_review_status?: string | null;
  wrong_location_status?: string | null;
  late_reason?: string | null;
  early_leave_reason?: string | null;
  early_leave_review_status?: string | null;
  admin_comment?: string | null;

  location_reviewed_by?: string | null;
  location_reviewed_by_name?: string | null;
  early_leave_reviewed_by?: string | null;
  early_leave_reviewed_by_name?: string | null;
  created_by?: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;

  created_at: string | null;
  updated_at: string | null;
}

export interface PaginationDTO {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AttendancePaginatedDTO {
  items: AttendanceDTO[];
  pagination: PaginationDTO;
}

export interface AttendanceTodayDTO {
  item: AttendanceDTO | null;
}

export interface AttendanceCheckInDTO {
  latitude: number;
  longitude: number;
  wrong_location_reason?: string | null;
  late_reason?: string | null;
}

export interface AttendanceCheckOutDTO {
  latitude: number;
  longitude: number;
  early_leave_reason?: string | null;
}

export interface AttendanceApproveWrongLocationDTO {
  approved: boolean;
  comment?: string | null;
  location_id?: string | null;
}

export interface AttendanceApproveEarlyLeaveDTO {
  approved: boolean;
  comment?: string | null;
}

export interface AttendanceListParams {
  employee_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  limit?: number;
  include_deleted?: boolean;
  deleted_only?: boolean;
}

export interface AttendanceTeamListParams {
  status?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  limit?: number;
}

export interface WrongLocationReportParams {
  start_date?: string;
  end_date?: string;
  status?: string;
  review_status?: string;
  page?: number;
  limit?: number;
}

export interface EarlyLeaveReportParams {
  start_date?: string;
  end_date?: string;
  status?: string;
  review_status?: string;
  page?: number;
  limit?: number;
}
