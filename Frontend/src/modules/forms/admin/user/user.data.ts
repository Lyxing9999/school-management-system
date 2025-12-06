import type {
  AdminCreateUser,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";
import { Role } from "~/api/types/enums/role.enum";
import { reactive } from "vue";

// Create form: fresh object
export const getUserFormData = (): AdminCreateUser => ({
  username: "",
  email: "",
  password: "",
  role: Role.STUDENT,
});

// Update form: reactive object
export const getUserFormDataEdit = (data?: Partial<AdminUpdateUser>) =>
  reactive({
    username: "",
    email: "",
    password: "",
    role: Role.STUDENT,
    ...data,
  });
