import type {
  AdminCreateSubject,
  AdminUpdateSubject,
} from "~/api/admin/subject/dto";

// Create form: fresh object
export const getSubjectFormData = (): AdminCreateSubject => ({
  name: "",
  teacher_id: [],
});

// Update form: reactive object
export const getSubjectFormDataEdit = (data?: Partial<AdminUpdateSubject>) =>
  reactive({
    name: "",
    teacher_id: [],
    ...data,
  });
