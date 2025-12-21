import type { ApiResponse } from "~/api/types/common/api-response.type";
import { StaffRole } from "~/api/types/enums/role.enum";
import type { StaffBaseDataDTO } from "~/api/types/staff.dto";

export interface AdminGetStaffData extends StaffBaseDataDTO {}

export interface AdminCreateStaff {
  email: string;
  password: string;
  role: StaffRole.TEACHER;
  staff_id: string;
  staff_name: string;
  phone_number: string;
  address: string;
}

export interface AdminUpdateStaff {
  staff_id?: string;
  staff_name?: string;
  role?: StaffRole;
  phone_number?: string;
  address?: string;
}

export interface AdminStaffNameSelectData {
  value: string;
  label: string;
}
export interface AdminTeacherNameSelectData {
  value: string;
  label: string;
}
export interface AdminTeacherSelectListData {
  items: AdminTeacherNameSelectData[];
}
export interface AdminGetTeacherData extends AdminTeacherNameSelectData {}

export type AdminGetStaffResponse = ApiResponse<StaffBaseDataDTO>;
export type AdminGetStaffSelectResponse = ApiResponse<AdminStaffNameSelectData>;
export type AdminTeacherSelectListResponse =
  ApiResponse<AdminTeacherSelectListData>;
