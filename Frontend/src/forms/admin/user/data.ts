import type { AdminCreateUser, AdminUpdateUser } from "~/api/admin/user/dto";
import { UserRole } from "~/api/types/enums/role.enum";
import { reactive } from "vue";

// Create form: fresh object
export const getUserFormData = (): AdminCreateUser => ({
  username: "",
  email: "",
  password: "",
  role: UserRole.STUDENT,
});

// Update form: reactive object
export const getUserFormDataEdit = (data?: Partial<AdminUpdateUser>) =>
  reactive({
    username: "",
    email: "",
    password: "",
    role: UserRole.STUDENT,
    ...data,
  });
