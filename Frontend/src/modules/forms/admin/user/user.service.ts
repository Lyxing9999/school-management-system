import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";
import type {
  AdminCreateUser,
  AdminUpdateUser,
  AdminGetUserData,
} from "~/api/admin/user/user.dto";

export function useServiceFormUser(): UseFormService<
  AdminCreateUser,
  AdminUpdateUser,
  boolean,
  AdminGetUserData,
  AdminGetUserData,
  AdminGetUserData
> {
  const service = adminService();

  return {
    create: (data) => service.user.createUser(data, { showSuccess: true }),
    update: (id, data) =>
      service.user.updateUser(id, data, { showSuccess: true }),
    delete: async (id) => {
      await service.user.softDeleteUser(id);
      return true;
    },
  };
}
