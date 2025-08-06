import type { Role } from "~/types";

export interface UserResponseDataDTO {
  id: string;
  username: string;
  role: Role;
  email: string | null;
}

export type UserResponseDataDTOList = UserResponseDataDTO[];

export interface UserUpdateDataDTO {
  username: string | null;
  role: Role | null;
  email: string | null;
}
