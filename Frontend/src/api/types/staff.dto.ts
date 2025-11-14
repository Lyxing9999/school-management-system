import { StaffRole } from "./enums/role.enum";

export interface StaffBaseDataDTO {
  id: string;
  username?: string;
  email: string;
  staff_id: string;
  user_id: string;
  staff_name: string;
  role: StaffRole;
  phone_number: string;
  address: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
}
