import { Role, StaffRole, UserRole } from "~/api/types/enums/role.enum";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { UserBaseDataDTO } from "~/api/types/userBase";
export type AdminApiResponse<T> = ApiResponse<T>;

export interface AdminGetUserData extends UserBaseDataDTO {}
export interface AdminGetPageUserData {
  users: AdminGetUserData[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface AdminCreateUser {
  username?: string;
  email: string;
  password: string;
  role: UserRole;
}

export interface AdminUpdateUsers {
  username?: string;
  email?: string;
  password?: string;
  role?: UserRole;
}

export type AdminUserSchema = {};
export type AdminGetPageUserResponse = AdminApiResponse<AdminGetPageUserData>;
export type AdminGetUserResponse = AdminApiResponse<AdminGetUserData>;

export interface AdminCreateClass {
  name: string;
  owner_id: string;
  max_students: number;
  grade: number;
  status: boolean;
}

export interface AdminFindTeacherSelect {
  id: string;
  staff_name: string;
}
export type AdminGetTeacherSelectResponse = AdminApiResponse<
  AdminFindTeacherSelect[]
>;

export interface AdminGetClass {
  id: string;
  name: string;
  owner_id: string;
  max_students: number;
  grade: number;
  status: boolean;
}

export type AdminGetClassResponse = AdminApiResponse<AdminGetClass>;

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

export interface AdminGetStaffData {
  id: string;
  username?: string;
  email: string;
  staff_id: string;
  user_id: string;
  staff_name: string;
  role: StaffRole;
  phone_number: string;
  address: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
}
export type AdminGetStaffResponse = AdminApiResponse<AdminGetStaffData>;

export interface AdminUpdateStaffData {
  staff_id: string;
  staff_name: string;
  phone_number: string;
  address: string;
}
export type AdminUpdateStaffResponse = AdminApiResponse<AdminUpdateStaffData>;

export interface BaseStudentInfo {
  student_id: string;
  full_name: string;
  first_name?: string;
  last_name?: string;
  nickname?: string;
  birth_date?: string;
  gender?: string;
  grade_level?: number;
  classes?: string[];
  enrollment_date?: string;
  address?: string;
  photo_url?: string;
  guardian?: GuardianInfo;
  additional_info?: Record<string, any>;
}

export interface GuardianInfo {
  name: string;
  phone: string;
  relation: string;
}

export type AdminStudentInfoCreate = BaseStudentInfo;
export type AdminStudentInfoUpdate = Partial<BaseStudentInfo>;

export type AdminStudentInfoResponse = AdminApiResponse<BaseStudentInfo>;
