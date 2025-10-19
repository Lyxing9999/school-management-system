import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";
import type {
  AcademicStudentInfoUpdate,
  AcademicCreateStudentData,
} from "~/api/academic/academic.dto";

// Registry item types
export type FormRegistryEditItem<U extends object> = {
  service: UseFormService<any, U, any, any, any, any>;
  schema: Field<U>[];
  formData: () => U;
};

export type RoleEditMap = {
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

// Edit mode types
export type EditMode = "STUDENT";

export type EditFormType<T extends EditMode> = AcademicStudentInfoUpdate;
export type GetEditFormType<T extends EditMode> = AcademicStudentInfoUpdate;
