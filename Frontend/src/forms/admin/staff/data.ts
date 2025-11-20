import { StaffRole } from "~/api/types/enums/role.enum";
import type { AdminCreateStaff, AdminUpdateStaff } from "~/api/admin/staff/dto";
import { reactive } from "vue";
export const getStaffFormData = (): AdminCreateStaff => ({
  email: "",
  password: "",
  role: StaffRole.TEACHER,
  staff_id: "",
  staff_name: "",
  phone_number: "",
  address: "",
});

export const getStaffFormDataEdit = (data?: Partial<AdminUpdateStaff>) =>
  reactive({
    role: StaffRole.TEACHER,
    staff_id: "",
    staff_name: "",
    phone_number: "",
    address: "",
    ...data,
  });
