// ~/schemas/registry/AdminFormRegistry.ts
import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";

import {
  serviceFormUser,
  serviceFormStaff,
  serviceFormStudent,
} from "~/services/formServices/adminFormService";

import { userFormSchema, userFormData } from "~/schemas/forms/admin/userForm";

import {
  staffFormSchema,
  staffFormData,
  staffFormSchemaEdit,
  staffFormDataEdit,
} from "~/schemas/forms/admin/staffForm";

import {
  studentInfoFormSchemaEdit,
  studentInfoFormDataEdit,
} from "~/schemas/forms/admin/studentForm";

import type {
  AdminCreateUser,
  AdminUpdateUsers,
  AdminGetUserData,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  AdminStudentInfoUpdate,
  AdminStudentInfoCreate,
} from "~/api/admin/admin.dto";

// --- Registry item types ---
export type FormRegistryCreateItem<C extends object> = {
  service: UseFormService<C, any, any>;
  schema: Field<C>[];
  formData: () => C;
};

export type FormRegistryEditItem<U extends object> = {
  service: UseFormService<any, U, any>;
  schema: Field<U>[];
  formData: () => U;
};

// --- Create registry ---
export const formRegistryCreate = {
  USER: {
    service: serviceFormUser,
    schema: userFormSchema,
    formData: () => ({ ...userFormData } as AdminCreateUser),
  },
  STAFF: {
    service: serviceFormStaff,
    schema: staffFormSchema,
    formData: () => ({ ...staffFormData } as AdminCreateStaff),
  },
} as const satisfies Record<"USER" | "STAFF", FormRegistryCreateItem<any>>;

// --- Edit registry ---
export const formRegistryEdit = {
  USER: {
    service: serviceFormUser,
    schema: userFormSchema,
    formData: () => ({ ...userFormData } as AdminUpdateUsers),
  },
  STAFF: {
    service: serviceFormStaff,
    schema: staffFormSchemaEdit,
    formData: () => ({ ...staffFormDataEdit } as AdminUpdateStaff),
  },
  STUDENT: {
    service: serviceFormStudent,
    schema: studentInfoFormSchemaEdit,
    formData: () => ({ ...studentInfoFormDataEdit } as AdminStudentInfoUpdate),
  },
} as const satisfies Record<
  "USER" | "STAFF" | "STUDENT",
  FormRegistryEditItem<any>
>;
