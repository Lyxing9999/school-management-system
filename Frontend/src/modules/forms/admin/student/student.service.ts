import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";

import type {
  AdminCreateStudent,
  StudentBaseDataDTO,
  AdminUpdateStudent,
} from "~/api/admin/student/student.dto";
import {
  createStudentZod,
  updateStudentZod,
} from "~/modules/forms/admin/student/student.validation";

export function useServiceFormStudent(): UseFormService<
  AdminCreateStudent,
  AdminUpdateStudent,
  boolean,
  StudentBaseDataDTO,
  StudentBaseDataDTO,
  StudentBaseDataDTO
> {
  const adminApiService = adminService();

  return {
    // ---------------- CREATE ----------------
    create: async (data) => {
      const validation = createStudentZod.safeParse(data);

      if (!validation.success) {
        const errorMessage = validation.error.errors[0].message;
        ElMessage.error(errorMessage);
        throw new Error(errorMessage);
      }

      return adminApiService.student.createStudent(
        validation.data as AdminCreateStudent,
        {
          showSuccess: true,
        }
      );
    },

    // ---------------- UPDATE ----------------
    update: async (id, data) => {
      const validation = updateStudentZod.safeParse(data);

      if (!validation.success) {
        const errorMessage = validation.error.errors[0].message;
        ElMessage.error(errorMessage);
        throw new Error(errorMessage);
      }

      return adminApiService.student.updateStudentUserId(
        id,
        validation.data as AdminUpdateStudent,
        {
          showSuccess: true,
        }
      );
    },

    getDetail: (id) => adminApiService.student.getStudentUserId(id),
  };
}
