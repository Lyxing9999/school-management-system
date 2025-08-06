import type { ApiResponse } from "~/types/common/api-response.type";
import type { UserLoginDataDTO, UserRegisterDataDTO } from "./user_auth_dto";
import type { UserResponseDataDTO } from "./user_action_dto";

export type UserRegisterResponseDTO = ApiResponse<UserRegisterDataDTO>;

export type UserLoginResponseDTO = ApiResponse<UserLoginDataDTO>;

export type UserUpdateResponseDTO = ApiResponse<UserResponseDataDTO>;

export type UserResponseDTO = ApiResponse<UserResponseDataDTO>;

export type UserResponseDTOList = ApiResponse<UserResponseDataDTO[]>;
