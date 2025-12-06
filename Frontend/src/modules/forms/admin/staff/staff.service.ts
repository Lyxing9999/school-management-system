import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";
import type {
  AdminCreateStaff,
  AdminUpdateStaff,
} from "~/api/admin/staff/staff.dto";

export function useServiceFormStaff(): UseFormService<
  AdminCreateStaff,
  AdminUpdateStaff
> {
  const adminApiService = adminService();

  return {
    create: (data) => adminApiService.staff.createStaff(data), // create staff linked by create user
    update: (id, data) => adminApiService.staff.updateStaff(id, data),
    // delete: can be added in the future
    getDetail: (id: string) => adminApiService.staff.getStaffDetail(id),
  };
}
