import { UserRole } from "~/api/types/enums/role.enum";
import type { UserBaseDataDTO } from "~/api/types/user.dto";
import type { ApiResponse } from "~/api/types/common/api-response.type";

export interface UserLoginResponseDTO {
  access_token: string;
  user: UserBaseDataDTO;
}

export interface UserRegisterForm {
  email: string;
  password: string;
  role: UserRole;
}

export interface UserLoginForm {
  email: string;
  password: string;
}

export interface UserRegisterResponseDTO {
  access_token: string;
  user: UserBaseDataDTO;
}
