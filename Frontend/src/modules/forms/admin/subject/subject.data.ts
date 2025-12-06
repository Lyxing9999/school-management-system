import type { AdminCreateSubject } from "~/api/admin/subject/subject.dto";

// Create form: fresh object
export const getSubjectFormData = (): AdminCreateSubject => ({
  name: "",
  code: "",
  description: "",
  allowed_grade_levels: [],
});

// Update form: reactive object
// TODO in MVP VER2