import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types";
import type { AdminCreateClass, AdminUpdateClass } from "~/api/admin/class/dto";

export function useServiceFormClass(): UseFormService<
  AdminCreateClass,
  AdminUpdateClass
> {
  const service = adminService(); // <-- lazy, called at runtime

  return {
    create: (data) => service.class.createClass(data),
    update: (id, data) => service.class.updateClass(id, data as any),
    delete: async (id) => {
      await service.class.softDeleteClass(id);
      return true;
    },
  };
}
