import type { UseFormService } from "./serviceFormTypes";
import type { Field } from "~/components/types/form";
import type { AdminCreateUser, AdminUpdateUser } from "~/api/admin/user/dto";
import type { AdminCreateStaff, AdminUpdateStaff } from "~/api/admin/staff/dto";
import type { AdminCreateClassDTO } from "~/api/admin/class/dto";
import type { AdminCreateSubjectDTO } from "~/api/admin/subject/dto";
import type {
  AdminCreateScheduleSlotDTO,
  AdminUpdateScheduleSlotDTO,
} from "~/api/admin/schedule/dto";

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
  CLASS: FormRegistryCreateItem<AdminCreateClassDTO, AdminUpdateClassDTO>;
  SUBJECT: FormRegistryCreateItem<AdminCreateSubjectDTO, AdminUpdateSubjectDTO>;
  STUDENT: undefined;

  SCHEDULE_SLOT: FormRegistryCreateItem<
    AdminCreateScheduleSlotDTO,
    AdminUpdateScheduleSlotDTO
  >;
};

export type FormRegistryEdit = {
  USER: FormRegistryEditItem<AdminCreateUser, AdminUpdateUser>;
  STAFF: FormRegistryEditItem<AdminCreateStaff, AdminUpdateStaff>;
  CLASS: FormRegistryEditItem<AdminCreateClassDTO, AdminUpdateClassDTO>;
  SUBJECT: FormRegistryEditItem<AdminCreateSubjectDTO, AdminUpdateSubjectDTO>;
  STUDENT: FormRegistryEditItem<undefined, AdminUpdateStudentInfo>;

  SCHEDULE_SLOT: FormRegistryEditItem<
    AdminCreateScheduleSlotDTO,
    AdminUpdateScheduleSlotDTO
  >;
};
