import type { AdminCreateClass } from "~/api/admin/class/class.dto";

// Create form: fresh object
export const getClassFormData = (): AdminCreateClass => ({
  name: "",
  teacher_id: null,
  subject_ids: [],
  max_students: 30,
});
// Update form: reactive object
import { reactive } from "vue";
// TODO: Define proper structure for AdminUpdateClass

// export const getClassFormDataEdit = (data?: Partial<AdminUpdateClass>) =>
//   reactive({
//     code: "",
//     name: "hello",
//     grade: 1,
//     max_students: 30,
//     academic_year: "",
//     status: true,
//     ...data,
//   });
