import type { UserBaseDataDTO } from "~/api/types/user.dto";
import type { UserRole } from "~/api/types/enums/role.enum";
import type { ApiResponse } from "~/api/types/common/api-response.type";

/* Auth */
export type UserLoginForm = {
  email: string;
  password: string;
};

export type UserRegisterForm = {
  email: string;
  password: string;
  role: UserRole;
};

export type AuthData = {
  access_token: string;
  user: UserBaseDataDTO;
};

export type RefreshResponse = {
  access_token: string;
};

export type UserLoginResponse = AuthData;
export type UserRegisterResponse = AuthData;
export type MeResponse = UserBaseDataDTO;
export type RefreshApiResponse = RefreshResponse;

/* Reset password (token-based) */
export type ResetPasswordConfirmPayload = {
  token: string;
  new_password: string;
};

// same shape, keep one name if you prefer
export type ResetPasswordConfirmForm = ResetPasswordConfirmPayload;

export type ResetPasswordConfirmData = {
  message: string;
};

export type ResetPasswordConfirmResponse =
  ApiResponse<ResetPasswordConfirmData>;

/* Change password (logged-in user) */
export type ChangePasswordForm = {
  current_password: string;
  new_password: string;
};

export type ChangePasswordData = {
  message: string;
};

export type ChangePasswordResponse = ApiResponse<ChangePasswordData>;
export type UpdateMePayload = {
  email?: string | null;
  username?: string | null;
};
