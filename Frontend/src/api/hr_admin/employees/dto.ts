import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { Role } from "~/api/types/enums/role.enum";

export type HrEmploymentType = "permanent" | "contract";
export type HrEmployeeStatus = "active" | "inactive";

export type HrSalaryType = "monthly" | "daily" | "hourly";

export type HrEmployeeContractDTO = {
  start_date: string;
  end_date: string;
  salary_type: HrSalaryType;
  rate: number;
  pay_on_holiday?: boolean;
  pay_on_weekend?: boolean;
  leave_policy_id?: string | null;
};

export type HrEmployeeDTO = {
  id: string;
  employee_name?: string | null;
  user_id?: string | null;
  account_name?: string | null;
  account_email?: string | null;
  employee_code: string;
  full_name: string;
  department?: string | null;
  position?: string | null;
  employment_type: HrEmploymentType;
  basic_salary: number;
  contract?: HrEmployeeContractDTO | null;
  schedule_id?: string | null;
  schedule_name?: string | null;
  work_location_id?: string | null;
  work_location_name?: string | null;
  manager_user_id?: string | null;
  manager_name?: string | null;
  status: HrEmployeeStatus;
  created_by?: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  photo_url?: string | null;
  lifecycle?: {
    created_at?: string;
    updated_at?: string;
    deleted_at?: string | null;
    deleted_by?: string | null;
  } | null;
};

export type HrCreateEmployeeDTO = {
  employee_code: string;
  full_name: string;
  department?: string | null;
  position?: string | null;
  employment_type?: HrEmploymentType;
  basic_salary: number;
  contract?: HrEmployeeContractDTO | null;
  manager_user_id?: string | null;
  schedule_id?: string | null;
  work_location_id?: string | null;
  status?: HrEmployeeStatus;
  photo_url?: string | null;
};

export type HrUpdateEmployeeDTO = Partial<HrCreateEmployeeDTO> & {
  contract?: HrEmployeeContractDTO | null;
};

export type ListEmployeesParams = {
  q?: string;
  page?: number;
  limit?: number;
  include_deleted?: boolean;
  deleted_only?: boolean;
  with_accounts?: boolean;
};

export interface HrEmployeeAccountDTO {
  id: string;
  user_id?: string | null;
  email?: string | null;
  account_email?: string | null;
  username?: string | null;
  role?: string | null;
  status?: string | null;
  account_name?: string | null;
  deleted_at?: string | null;
  lifecycle?: {
    created_at?: string;
    updated_at?: string;
    deleted_at?: string | null;
    deleted_by?: string | null;
  } | null;
  full_name?: string | null;
  display_name?: string | null;
  name?: string | null;
}

export interface HrCreateEmployeeAccountDTO {
  username?: string;
  email: string;
  password: string;
  role: Role;
}

export interface HrEmployeeOnboardDTO {
  employee: HrCreateEmployeeDTO;
  email: string;
  password: string;
  username?: string;
  role?: string;
}

export interface HrEmployeeWithAccountDTO {
  employee: HrEmployeeDTO;
  user: HrEmployeeAccountDTO | null;
}

export interface HrEmployeeWithAccountSummaryDTO {
  employee: HrEmployeeDTO;
  account?: HrEmployeeAccountDTO | null;
  user?: HrEmployeeAccountDTO | null;
}

export interface HrEmployeeWithAccountSummaryPaginatedDTO {
  items: HrEmployeeWithAccountSummaryDTO[];
  total: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
}

export type HrGetEmployeesWithAccountsResponse =
  ApiResponse<HrEmployeeWithAccountSummaryPaginatedDTO>;
export type HrGetEmployeeResponse = ApiResponse<HrEmployeeDTO>;
export type HrGetMyEmployeeResponse = ApiResponse<HrEmployeeDTO>;
export type HrCreateEmployeeResponse = ApiResponse<HrEmployeeDTO>;
export type HrUpdateEmployeeResponse = ApiResponse<HrEmployeeDTO>;
export type HrGetEmployeeAccountResponse =
  ApiResponse<HrEmployeeAccountDTO | null>;
export type HrCreateEmployeeAccountResponse =
  ApiResponse<HrEmployeeWithAccountDTO>;
export type HrEmployeeOnboardResponse = ApiResponse<HrEmployeeWithAccountDTO>;
export type HrSoftDeleteEmployeeAccountResponse =
  ApiResponse<HrEmployeeAccountDTO>;
export type HrRestoreEmployeeAccountResponse =
  ApiResponse<HrEmployeeAccountDTO>;

export type ListEmployeeAccountsParams = {
  q?: string;
  page?: number;
  limit?: number;
  include_deleted?: boolean;
  deleted_only?: boolean;
  status?: string;
};

export interface HrEmployeeAccountListItemDTO {
  id: string;
  user_id?: string | null;
  email?: string | null;
  account_email?: string | null;
  username?: string | null;
  account_name?: string | null;
  role?: string | null;
  status?: string | null;
  deleted_at?: string | null;
  lifecycle?: {
    deleted_at?: string | null;
  } | null;
}

export interface HrEmployeeAccountPaginatedDTO {
  items: HrEmployeeAccountListItemDTO[];
  total: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
}

export interface HrLinkEmployeeAccountDTO {
  user_id: string;
}

export type HrGetEmployeeAccountsResponse =
  ApiResponse<HrEmployeeAccountPaginatedDTO>;

export type HrLinkEmployeeAccountResponse = ApiResponse<HrEmployeeDTO>;

export interface HrUpdateEmployeeAccountDTO {
  email?: string;
  username?: string;
  password?: string;
}

export interface HrPasswordResetResponse {
  message: string;
  reset_link?: string;
}
