import { UserRole } from "~/api/types/enums/role.enum";
import type { UserBaseDataDTO } from "~/api/types/user.dto";
import type { ApiResponse } from "~/api/types/common/api-response.type";

export type IamApiResponse<T> = ApiResponse<T>;

export interface UserLogin {
  access_token: string;
  user: UserBaseDataDTO;
}

export interface UserRegister {
  email: string;
  password: string;
  role: UserRole;
}

export interface UserLoginForm {
  email: string;
  password: string;
}

export interface UserRegister {
  access_token: string;
  user: UserBaseDataDTO;
}

export interface AuthData {
  access_token: string;
  user: UserBaseDataDTO;
}

export type UserLoginResponse = IamApiResponse<UserLogin>;

export type UserRegisterResponse = IamApiResponse<UserRegister>;

export type AuthDataResponse = IamApiResponse<AuthData>;
