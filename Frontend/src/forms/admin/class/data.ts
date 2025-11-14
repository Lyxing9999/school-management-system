import type { AdminCreateClass, AdminUpdateClass } from "~/api/admin/class/dto";

// Create form: fresh object
export const getClassFormData = (): AdminCreateClass => ({
  code: "234234",
  name: "hello",
  grade: 1,
  max_students: 30,
  academic_year: "",
  status: true,
});

// Update form: reactive object
import { reactive } from "vue";
export const getClassFormDataEdit = (data?: Partial<AdminUpdateClass>) =>
  reactive({
    code: "",
    name: "hello",
    grade: 1,
    max_students: 30,
    academic_year: "",
    status: true,
    ...data,
  });
