import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";
import type { AdminCreateSubject } from "~/api/admin/subject/subject.dto";
import type { SubjectDTO } from "~/api/types/school.dto";
export function useServiceFormSubject(): UseFormService<
  AdminCreateSubject,
  never,
  boolean,
  SubjectDTO
> {
  const service = adminService(); // called at runtime

  return {
    create: (data) =>
      service.subject.createSubject(data, {
        showSuccess: true,
        showError: true,
      }),
  };
}
