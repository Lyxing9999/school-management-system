import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { UserBaseDataDTO } from "~/api/types/user.dto";
import { UserRole } from "~/api/types/enums/role.enum";

export type AdminApiResponse<T> = ApiResponse<T>;

/* User Data */
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

export type AdminGetUserResponse = AdminApiResponse<AdminGetUserData>;
export type AdminGetPageUserResponse = AdminApiResponse<AdminGetPageUserData>;
