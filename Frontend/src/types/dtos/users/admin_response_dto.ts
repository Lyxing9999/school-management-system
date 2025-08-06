import type { ApiResponse } from "~/types/common/api-response.type";
import { mapAliasList, mapAliases, type AliasMap } from "~/utils";
import type {
  AdminCreateUserDataDTO,
  AdminUpdateUserDataDTO,
  AdminDeleteUserDataDTO,
  AdminFindUserDataDTO,
} from "./admin_user_dto";


export type AdminCreateUserResponseDTO = ApiResponse<AdminCreateUserDataDTO>;

export type AdminUpdateUserResponseDTO = ApiResponse<AdminUpdateUserDataDTO>;

export type AdminDeleteUserResponseDTO = ApiResponse<AdminDeleteUserDataDTO>;

export type AdminFindUserResponseDTO = ApiResponse<AdminFindUserDataDTO>;

export type AdminFindUserResponseDTOList = ApiResponse<AdminFindUserDataDTO[]>;
