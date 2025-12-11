import type {
  FormRegistryCreateItem,
  FormRegistryEditItem,
} from "../formRegistry";

import type {
  AdminCreateUser,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";

import type { AdminCreateClass } from "~/api/admin/class/class.dto";

import type {
  AdminCreateStaff,
  AdminUpdateStaff,
} from "~/api/admin/staff/staff.dto";

import type { AdminCreateSubject } from "~/api/admin/subject/subject.dto";

import type {
  AdminCreateScheduleSlot,
  AdminUpdateScheduleSlot,
} from "~/api/admin/schedule/schedule.dto";

import type { AdminCreateStudent } from "~/api/admin/student/student.dto";

export type AdminFormRegistryCreate = {
  USER: FormRegistryCreateItem<AdminCreateUser, never>;
  STAFF: FormRegistryCreateItem<AdminCreateStaff, never>;
  CLASS: FormRegistryCreateItem<AdminCreateClass, never>;
  SUBJECT: FormRegistryCreateItem<AdminCreateSubject, never>;
  STUDENT: FormRegistryCreateItem<AdminCreateStudent, never>;
  SCHEDULE_SLOT: FormRegistryCreateItem<
    AdminCreateScheduleSlot,
    AdminUpdateScheduleSlot
  >;
};

export type AdminFormRegistryEdit = {
  USER: FormRegistryEditItem<never, AdminUpdateUser>;
  STAFF: FormRegistryEditItem<never, AdminUpdateStaff>;
  SCHEDULE_SLOT: FormRegistryEditItem<never, AdminUpdateScheduleSlot>;
};

export type AdminFormModeCreate = keyof AdminFormRegistryCreate;
export type AdminFormModeEdit = keyof AdminFormRegistryEdit;
