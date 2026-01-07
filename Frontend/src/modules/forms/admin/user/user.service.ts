import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";
import type {
  AdminCreateUser,
  AdminUpdateUser,
  AdminGetUserData,
} from "~/api/admin/user/user.dto";

import { createUserZod, updateUserZod } from "./user.validation";

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
    create: async (data) => {
      const validation = createUserZod.safeParse(data);
      if (!validation.success) {
        const errorMessage = validation.error.errors[0].message;
        ElMessage.error(errorMessage);
        throw new Error(errorMessage);
      }
      return service.user.createUser(validation.data as AdminCreateUser, {
        showSuccess: true,
      });
    },

    update: async (id, data) => {
      const validation = updateUserZod.safeParse(data);
      if (!validation.success) {
        const errorMessage = validation.error.errors[0].message;
        ElMessage.error(errorMessage);
        throw new Error(errorMessage);
      }
      const cleanData = { ...validation.data };
      if (!cleanData.password) {
        delete cleanData.password;
      }
      return service.user.updateUser(id, cleanData as AdminUpdateUser, {
        showError: false,
      });
    },

    delete: async (id) => {
      await service.user.softDeleteUser(id);
      return true;
    },
  };
}
