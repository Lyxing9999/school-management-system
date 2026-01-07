import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { UserBaseDataDTO } from "~/api/types/user.dto";
import { Role } from "~/api/types/enums/role.enum";
import type { Status } from "~/api/types/enums/status.enum";
export type AdminApiResponse<T> = ApiResponse<T>;

/* User Data */
export interface AdminGetUserData extends UserBaseDataDTO {}

export interface AdminGetUserItemData extends UserBaseDataDTO {
  created_by_name: string;
}
export interface AdminGetPageUserData {
  items: AdminGetUserItemData[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface AdminCreateUser {
  username?: string;
  email: string;
  password: string;
  role: Role;
}

export interface AdminUpdateUser {
  username?: string;
  email?: string;
  password?: string;
  role?: Role;
}

export interface AdminUpdateUserStatus {
  status: Status;
}
export interface AdminPasswordResetResponse {
  message: string;
  // MVP/dev only (if backend returns token). Remove later.
  token?: string;
}
export type AdminGetUserResponse = AdminApiResponse<AdminGetUserData>;
export type AdminGetPageUserResponse = AdminApiResponse<AdminGetPageUserData>;

export type AdminPasswordResetApiResponse =
  AdminApiResponse<AdminPasswordResetResponse>;
