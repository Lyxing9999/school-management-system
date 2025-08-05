import type { UserBaseDTO } from "./user_base_dto";

export interface UserRegisterDataDTO {
  access_token: string;
  user: Pick<UserBaseDTO, "id" | "username" | "role" | "email">;
}
