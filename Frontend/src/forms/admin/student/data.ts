import type {
  AdminCreateStudentInfo,
  AdminUpdateStudentInfo,
} from "~/api/admin/student/dto";
import { reactive, ref } from "vue";

// File reference
const photo_file = ref<File | null>(null);

// Create form: fresh object
export const getStudentInfoFormData = (): AdminCreateStudentInfo & {
  photo_file?: File | null;
} => ({
  student_id: "",
  full_name: "",
  first_name: "",
  last_name: "",
  birth_date: "",
  gender: "",
  grade_level: 0,
  classes: [],
  enrollment_date: "",

  address: "",
  photo_url: "",
  photo_file: null,
});

// Update form: reactive object
export const getStudentInfoFormDataEdit = (
  data?: Partial<AdminUpdateStudentInfo>
) =>
  reactive({
    student_id: "",
    full_name: "",
    first_name: "",
    last_name: "",
    birth_date: "",
    gender: "",
    grade_level: 0,
    classes: [],
    enrollment_date: "",
    address: "",
    photo_url: "",
    photo_file: null,
    ...data,
  });
