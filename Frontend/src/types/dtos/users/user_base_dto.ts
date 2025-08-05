import type { Role } from "~/types";

export interface UserBaseDTO {
  id: string;
  username?: string;
  email?: string;
  role: Role;
}
