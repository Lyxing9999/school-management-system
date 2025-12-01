import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types/serviceFormTypes";
import type { AdminCreateUser, AdminUpdateUser } from "~/api/admin/user/dto";

export function useServiceFormUser(): UseFormService<
  AdminCreateUser,
  AdminUpdateUser
> {
  const adminApiService = adminService();

  return {
    create: (data) =>
      adminApiService.user.createUser(data, { showSuccess: true }),
    update: (id, data) =>
      adminApiService.user.updateUser(id, data, { showSuccess: true }),
    delete: async (id) => {
      await adminApiService.user.softDeleteUser(id);
      return true;
    },
  };
}
