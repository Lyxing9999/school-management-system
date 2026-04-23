export interface PayrollRunGenerateDTO {
  month: string;
}

export interface PayrollRunGenerateResponseDTO {
  id?: string;
  run_id?: string;
  month?: string;
  status?: string;
  total_employees?: number;
  total_amount?: number;
  generated_at?: string;
  [key: string]: any;
}

import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export type PayrollRunStatus = "draft" | "finalized" | "paid";

export interface PayrollRunDTO {
  id: string;
  month: string;
  payroll_month?: string | null;
  payroll_run_label?: string | null;
  generated_by: string;
  generated_by_name?: string | null;
  created_by?: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  status: PayrollRunStatus | string;
  lifecycle: LifecycleDTO;
}

export interface PayrollRunListParams {
  page?: number;
  limit?: number;
}

export interface PayrollRunPaginatedDTO {
  items: PayrollRunDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PayslipDTO {
  id: string;
  payroll_run_id: string;
  payroll_month?: string | null;
  payroll_run_label?: string | null;
  employee_id: string;
  employee_name?: string | null;
  month: string;
  base_salary: number;
  payable_working_days: number;
  paid_holiday_days: number;
  unpaid_leave_days: number;
  total_ot_hours: number;
  ot_payment: number;
  total_deductions: number;
  net_salary: number;
  status: string;
  created_by?: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  lifecycle: LifecycleDTO;
}

export interface PayslipListParams {
  payroll_run_id?: string;
  employee_id?: string;
  month?: string;
  page?: number;
  limit?: number;
}

export interface PayslipPaginatedDTO {
  items: PayslipDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
