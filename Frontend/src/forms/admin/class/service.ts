import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types/serviceFormTypes";

export function useServiceFormClass(): UseFormService<any, any> {
  const service = adminService();

  return {
    create: (data) => service.class.createClass(data),
    update: (id, data) =>
      service.class.assignClassTeacher(id, data, { showSuccess: true }),
    delete: async (id) => {
      await service.class.softDeleteClass(id);
      return true;
    },
  };
}
