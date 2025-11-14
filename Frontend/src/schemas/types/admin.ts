import type {
  AdminCreateUser,
  AdminUpdateUser,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminStudentInfoUpdate,
  AdminGetUserData,
  AdminGetStaffData,
  AdminCreateClass,
  AdminCreateSubject,
  AdminUpdateSubject,
  AdminUpdateClass,
} from "~/api/admin/admin.dto";
import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";
import type { BaseClassDataDTO } from "~/api/types/class.dto";
import type { BaseSubject } from "~/api/types/subject.dto";
// Registry item types
export type FormRegistryCreateItem<C extends object> = {
  service: UseFormService<C, any, any, any, any, any>;
  schema?: Field<C>[];
  formData?: () => C;
};

export type FormRegistryEditItem<U extends object> = {
  service: UseFormService<any, U, any, any, any, any>;
  schema?: Field<U>[];
  formData?: () => U;
};

// Role maps
export type RoleCreateMap = {
  USER: AdminCreateUser;
  STAFF: AdminCreateStaff;
  CLASS: AdminCreateClass;
  STUDENT: AdminStudentInfoUpdate;
  SUBJECT: AdminCreateSubject;
};

export type RoleEditMap = {
  USER: AdminUpdateUser;
  STAFF: AdminUpdateStaff;
  STUDENT: AdminStudentInfoUpdate;
  CLASS: AdminUpdateClass;
  SUBJECT: AdminUpdateSubject;
};

// Dynamic registry
export type CreateRegistryItem = {
  [K in keyof RoleCreateMap]: FormRegistryCreateItem<RoleCreateMap[K]>;
};

export type EditRegistryItem = {
  [K in keyof RoleEditMap]: FormRegistryEditItem<RoleEditMap[K]>;
};

// Form maps
export type CreateFormMap = {
  USER: AdminCreateUser;
  STAFF: AdminCreateStaff;
  STUDENT: AdminStudentInfoUpdate;
  CLASS: AdminCreateClass;
  SUBJECT: AdminCreateSubject;
};

export type GetFormMap = {
  USER: AdminGetUserData;
  STAFF: AdminGetStaffData;
  STUDENT: AdminStudentInfoUpdate;
  CLASS: BaseClassDataDTO;
  SUBJECT: BaseSubject;
};

// Edit mode types
export type EditMode = "USER" | "STAFF" | "STUDENT" | "CLASS" | "SUBJECT";

export type EditFormType<T extends EditMode> = T extends "USER"
  ? AdminUpdateUser
  : T extends "STAFF"
  ? AdminUpdateStaff
  : T extends "STUDENT"
  ? AdminStudentInfoUpdate
  : T extends "CLASS"
  ? BaseClassDataDTO
  : T extends "SUBJECT"
  ? AdminUpdateSubject
  : never;

export type GetEditFormType<T extends EditMode> = T extends "USER"
  ? AdminUpdateUser
  : T extends "STAFF"
  ? AdminUpdateStaff
  : T extends "STUDENT"
  ? AdminStudentInfoUpdate
  : T extends "CLASS"
  ? BaseClassDataDTO
  : T extends "SUBJECT"
  ? BaseSubject
  : never;
