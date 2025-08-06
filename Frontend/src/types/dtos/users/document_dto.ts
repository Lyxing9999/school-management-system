import type { Role } from "~/types";

export interface DocumentDBDTO {
  id: string;
  username: string | null;
  role: Role;
  email: string | null;
  password: string;
  created_by: string | null;
  updated_by: string | null;
  deleted_by: string | null;
}
