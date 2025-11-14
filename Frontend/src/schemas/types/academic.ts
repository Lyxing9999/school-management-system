import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";
import type {
  AcademicStudentInfoUpdate,
  AcademicCreateStudentData,
  AcademicUpdateStudentData,
  AcademicGetStudentResponse,
  AcademicStudentInfoResponse,
} from "~/api/academic/academic.dto";

// Registry item types
export type FormRegistryEditItem<U extends object> = {
  service: UseFormService<any, U, any, any, any, any>;
  schema: Field<U>[];
  formData: () => U;
};
export type FormRegistryCreateItem<C extends object> = {
  service: UseFormService<C, any, any, any, any, any>;
  schema?: Field<C>[];
  formData?: () => C;
};

export type RoleEditMap = {
  USER: AcademicUpdateStudentData;
  STUDENT: AcademicStudentInfoUpdate;
};
export type RoleCreateMap = {
  STUDENT: AcademicCreateStudentData;
};
// Dynamic registry
export type EditRegistryItem = {
  [K in keyof RoleEditMap]: FormRegistryEditItem<RoleEditMap[K]>;
};

export type CreateRegistryItem = {
  [K in keyof RoleCreateMap]: FormRegistryEditItem<RoleCreateMap[K]>;
};

export type CreateFormMap = {
  USER: AcademicCreateStudentData;
  STUDENT: AcademicStudentInfoUpdate;
  SUBJECT: AcademicCreateSubject;
};

export type GetFormMap = {
  USER: AcademicGetStudentResponse;
  STUDENT: AcademicStudentInfoResponse;
  SUBJECT: BaseSubject;
};
