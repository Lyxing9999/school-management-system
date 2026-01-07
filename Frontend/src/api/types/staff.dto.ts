import { StaffRole } from "./enums/role.enum";
import type { LifecycleDTO } from "./lifecycle.dto";
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
  lifecycle: LifecycleDTO;
}
