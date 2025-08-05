import type { ApiResponse } from "~/types/common/api-response.type";
import type { UserLoginDataDTO } from "./user_login.dto";
import type { UserRegisterDataDTO } from "./user_register.dto";
import type { AdminUserDTO } from "./user_action_dto";

export interface UserRegisterResponseDTO
  extends ApiResponse<UserRegisterDataDTO> {}

export interface UserLoginResponseDTO extends ApiResponse<UserLoginDataDTO> {}

export interface AdminCreateUserResponseDTO
  extends ApiResponse<AdminUserDTO.Create> {}

export interface AdminUpdateUserResponseDTO
  extends ApiResponse<AdminUserDTO.Update> {}

export interface AdminDeleteUserResponseDTO
  extends ApiResponse<AdminUserDTO.Delete> {}

export interface AdminGetUserResponseDTO
  extends ApiResponse<AdminUserDTO.GetResponse[]> {}
