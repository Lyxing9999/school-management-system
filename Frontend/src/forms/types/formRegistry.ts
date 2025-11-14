import type { UseFormService } from "../types";
import type { Field } from "~/components/types/form";
import type { AdminCreateUser, AdminUpdateUser } from "~/api/admin/user/dto";
import type { AdminCreateStaff, AdminUpdateStaff } from "~/api/admin/staff/dto";
import type { AdminCreateClass, AdminUpdateClass } from "~/api/admin/class/dto";
import type {
  AdminCreateSubject,
  AdminUpdateSubject,
} from "~/api/admin/subject/dto";
import type {
  AdminCreateStudentInfo,
  AdminUpdateStudentInfo,
} from "~/api/admin/student/dto";
export type FormRegistryCreateItem<C, U> = {
  service: () => UseFormService<C, U>;
  schema: Field<C>[];
  formData: () => C;
};

export type FormRegistryEditItem<C, U> = {
  service: () => UseFormService<C, U>;
  schema: Field<Partial<U>>[];
  formData: () => U;
};

export type FormRegistryCreate = {
  USER: FormRegistryCreateItem<AdminCreateUser, AdminUpdateUser>;
  STAFF: FormRegistryCreateItem<AdminCreateStaff, AdminUpdateStaff>;
  CLASS: FormRegistryCreateItem<AdminCreateClass, AdminUpdateClass>;
  SUBJECT: FormRegistryCreateItem<AdminCreateSubject, AdminUpdateSubject>;
  STUDENT: undefined;
};

export type FormRegistryEdit = {
  USER: FormRegistryEditItem<AdminCreateUser, AdminUpdateUser>;
  STAFF: FormRegistryEditItem<AdminCreateStaff, AdminUpdateStaff>;
  CLASS: FormRegistryEditItem<AdminCreateClass, AdminUpdateClass>;
  SUBJECT: FormRegistryEditItem<AdminCreateSubject, AdminUpdateSubject>;
  STUDENT: FormRegistryEditItem<undefined, AdminUpdateStudentInfo>;
};
