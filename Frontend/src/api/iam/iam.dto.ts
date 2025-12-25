import type { UserBaseDataDTO } from "~/api/types/user.dto";
import type { UserRole } from "~/api/types/enums/role.enum";

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
