import { Role, UserRole, StaffRole } from "./enums/role.enum";

/**
 * @description User Base Data
 * @example
 * {
 *  id: "1",
 *  username: "admin",
 *  email: "admin@admin.com",
 *  role: "admin",
 *  created_by: "admin",
 *  created_at: "2022-01-01T00:00:00.000Z",
 *  updated_at: "2022-01-01T00:00:00.000Z"
 *  deleted: false
 *  deleted_at: "2022-01-01T00:00:00.000Z"
 *  deleted_by: "admin"
 * }
 */

export interface UserBaseDataDTO {
  id: string;
  username?: string;
  email: string;
  password?: string | null;
  role: UserRole | StaffRole;
  created_by: string;
  created_at: string;
  updated_at: string;
  deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
}
