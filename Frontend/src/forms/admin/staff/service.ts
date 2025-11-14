import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types";
import type { AdminCreateStaff, AdminUpdateStaff } from "~/api/admin/staff/dto";

export function useServiceFormStaff(): UseFormService<
  AdminCreateStaff,
  AdminUpdateStaff
> {
  // ✅ lazy call inside the function
  const adminApiService = adminService();

  return {
    create: (data) => adminApiService.staff.createStaff(data), // create staff linked by create user
    update: (id, data) => adminApiService.staff.updateStaff(id, data),
    // delete: can be added in the future
  };
}
