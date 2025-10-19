import { Role, StaffRole, UserRole } from "~/api/types/enums/role.enum";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { UserBaseDataDTO } from "~/api/types/userBase";
import type { BaseStudentInfo } from "~/api/types/baseStudentInfo";
import type { BaseClassDataDTO } from "~/api/types/baseClass";
import type { BaseSubject } from "~/api/types/baseSubject";
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

export interface AdminUpdateUser {
  username?: string;
  email?: string;
  password?: string;
  role?: UserRole;
}

export type AdminUserSchema = {};
export type AdminGetPageUserResponse = AdminApiResponse<AdminGetPageUserData>;
export type AdminGetUserResponse = AdminApiResponse<AdminGetUserData>;

//class api
export interface AdminCreateClass {
  name: string;
  grade: number;
  max_students: number;
  academic_year?: string;
  code?: string;
  status?: boolean;
}

export interface AdminUpdateClass {
  name?: string;
  owner_id?: string;
  max_students?: number;
  grade?: number;
  status?: boolean;
}

export interface AdminAssignTeacher {
  teacher_id: string;
}
export interface AdminUnassignTeacher {
  teacher_id: string;
}

export interface AdminAssignStudent {
  student_id: string;
}

export interface AdminUnassignStudent {
  student_id: string;
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
  class_room?: string | null;
  homeroom_teacher?: string | null;
  subjects?: string[] | null;
  students?: string[] | null;
  grade: number;
  status: boolean;
}
export interface AdminUpdateClass {
  name?: string;
  owner_id?: string;
  max_students?: number;
  grade?: number;
  status?: boolean;
  class_room?: string | null;
  homeroom_teacher?: string | null;
  subjects?: string[] | null;
  students?: string[] | null;
}

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
export interface AdminUpdateSubject {
  name?: string;
  teacher_id?: string[];
}

export interface AdminCreateSubject {
  name: string;
  teacher_id: string[];
}
export interface AdminUpdateSubject {
  name?: string;
  teacher_id?: string[];
}
// response
export type AdminUpdateStaffResponse = AdminApiResponse<AdminUpdateStaffData>;
export type AdminGetClassResponse = AdminApiResponse<BaseClassDataDTO>;
export type AdminGetAllClassesResponse = AdminApiResponse<BaseClassDataDTO[]>;
export type AdminStudentInfoCreate = BaseStudentInfo["student_info"];
export type AdminStudentInfoUpdate = Partial<BaseStudentInfo["student_info"]>;

export type AdminStudentInfoResponse = AdminApiResponse<BaseStudentInfo>;
export type AdminSubjectResponse = AdminApiResponse<BaseSubject>;
