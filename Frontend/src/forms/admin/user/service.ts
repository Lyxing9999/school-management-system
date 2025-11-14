import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types";
import type { AdminCreateUser, AdminUpdateUser } from "~/api/admin/user/dto";

export function useServiceFormUser(): UseFormService<
  AdminCreateUser,
  AdminUpdateUser
> {
  const adminApiService = adminService();

  return {
    create: (data) => adminApiService.user.createUser(data),
    update: (id, data) => adminApiService.user.updateUser(id, data),
    delete: async (id) => {
      await adminApiService.user.deleteUser(id);
      return true; // consider calling this "soft delete" if backend uses soft delete
    },
  };
}
