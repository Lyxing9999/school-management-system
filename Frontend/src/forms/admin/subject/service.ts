import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types/serviceFormTypes";
import type {
  AdminCreateSubjectDTO as AdminCreateSubject,
  AdminUpdateSubjectDTO as AdminUpdateSubject,
} from "~/api/admin/subject/dto";

export function useServiceFormSubject(): UseFormService<
  AdminCreateSubject,
  AdminUpdateSubject
> {
  const service = adminService(); // called at runtime

  return {
    create: (data) => service.subject.createSubject(data),
    update: (id, data) => service.subject.updateSubject(id, data),
    delete: async (id) => {
      await service.subject.deleteSubject(id);
      return true;
    },
  };
}
