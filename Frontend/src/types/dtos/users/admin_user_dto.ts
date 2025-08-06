import type { UserResponseDataDTO } from "./user_action_dto";

export interface AdminCreateUserDataDTO extends UserResponseDataDTO {
  created_by: string;
}

export interface AdminUpdateUserDataDTO extends UserResponseDataDTO {
  updated_by: string;
}

export interface AdminDeleteUserDataDTO extends UserResponseDataDTO {
  deleted_by: string;
}

export interface AdminFindUserDataDTO extends UserResponseDataDTO {
  created_by: string;
  updated_by: string;
  deleted_by: string;
}
