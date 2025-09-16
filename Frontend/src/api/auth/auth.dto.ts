import { UserRole } from "~/api/types/enums/role.enum";
import type { UserBaseDataDTO } from "~/api/types/userBase";
import type { ApiResponse } from "~/api/types/common/api-response.type";

/**
 * -------------------------------
 * Generic Auth API Response Wrapper
 * -------------------------------
 */
export type AuthApiResponse<T> = ApiResponse<T>;

/**
 * -------------------------------
 * Base Auth Forms
 * -------------------------------
 */
export interface BaseAuthForm {
  email: string;
  password: string;
}
/**
 * -------------------------------
 * Auth Forms
 * -------------------------------
 */
export interface UserLoginForm extends BaseAuthForm {}

export interface UserRegisterForm extends BaseAuthForm {
  username?: string;
  role: UserRole;
}

export interface UserUpdateForm {
  username?: string;
  email?: string;
  password?: string;
}

/**
 * -------------------------------
 * Auth Data DTOs
 * -------------------------------
 */
export interface AuthDataDTO {
  access_token: string;
  user: UserBaseDataDTO;
}

/**
 * -------------------------------
 * Auth API Responses
 * -------------------------------
 */
export type UserLoginResponseDTO = AuthApiResponse<AuthDataDTO>;
export type UserRegisterResponseDTO = AuthApiResponse<AuthDataDTO>;

/**
 * -------------------------------
 * Example Usage
 * -------------------------------
 * const response: UserLoginResponseDTO = await authApi.login(form);
 * if (response.success) {
 *   console.log(response.data.user.email);
 * }
 */
