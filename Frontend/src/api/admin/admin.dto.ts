import { Role, StaffRole, UserRole } from "~/api/types/enums/role.enum";
import type { ApiResponse } from "~/api/types/common/api-response.type";
export type AdminApiResponse<T> = ApiResponse<T>;
export type AdminGetUserData = {
  id: string;
  username?: string;
  email: string;
  role: Role;
  created_at: string;
  updated_at: string;
  deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
};
export type AdminGetPageUserData = {
  users: AdminGetUserData[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

export type AdminCreateUser = {
  username: string;
  email: string;
  password: string;
  role: UserRole;
};

export type AdminUpdateUser = {
  username?: string;
  email?: string;
  password?: string;
  role?: UserRole;
};

export type AdminUserSchema = {};
export type AdminGetPageUserResponse = AdminApiResponse<AdminGetPageUserData>;
export type AdminGetUserResponse = AdminApiResponse<AdminGetUserData>;

export type AdminCreateClass = {
  name: string;
  owner_id: string;
  max_students: number;
  grade: number;
  status: boolean;
};

export type AdminFindTeacherSelect = {
  id: string;
  staff_name: string;
};
export type AdminGetTeacherSelectResponse = AdminApiResponse<
  AdminFindTeacherSelect[]
>;
export type AdminGetClass = {
  id: string;
  name: string;
  owner_id: string;
  max_students: number;
  grade: number;
  status: boolean;
};

export type AdminGetClassResponse = AdminApiResponse<AdminGetClass>;

export type AdminCreateStaff = AdminCreateUser & {
  staff_id: string;
  staff_name: string;
  role: StaffRole;
  phone_number: string;
  address: string;
};

export type AdminUpdateStaff = AdminUpdateUser & {
  staff_id?: string;
  staff_name?: string;
  role?: StaffRole;
  phone_number?: string;
  address?: string;
};

export type adminGetstaffData = AdminGetUserData & {
  staff_id: string;
  staff_name: string;
  role: StaffRole;
  phone_number: string;
  address: string;
};
export type AdminGetStaffResponse = AdminApiResponse<adminGetstaffData>;
