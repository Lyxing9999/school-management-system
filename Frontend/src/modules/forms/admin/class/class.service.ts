import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";

import type { AdminCreateClass } from "~/api/admin/class/class.dto";
import type { ClassSectionDTO } from "~/api/types/school.dto";
export function useServiceFormClass(): UseFormService<
  AdminCreateClass,
  never,
  boolean,
  ClassSectionDTO,
  never,
  never
> {
  const service = adminService();

  return {
    create: (data) => service.class.createClass(data),
    delete: async (id) => {
      await service.class.softDeleteClass(id);
      return true;
    },
  };
}
