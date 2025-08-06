import type { UserResponseDataDTO } from "./user_action_dto";

export interface UserLoginDataDTO {
  access_token: string;
  user: Pick<UserResponseDataDTO, "id" | "username" | "role" | "email">;
}

export interface UserRegisterDataDTO extends UserLoginDataDTO {}
