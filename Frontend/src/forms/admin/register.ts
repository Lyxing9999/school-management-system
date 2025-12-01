import {
  userForm,
  staffForm,
  studentForm,
  classForm,
  subjectForm,
  scheduleSlotForm,
} from "~/forms/admin";

import type {
  FormRegistryCreate,
  FormRegistryEdit,
} from "~/forms/types/formRegistry";

// -------------------- CREATE FORMS --------------------
export const formRegistryCreate: FormRegistryCreate = {
  USER: {
    service: () => userForm.useServiceFormUser(),
    schema: userForm.userFormSchema,
    formData: () => ({ ...userForm.getUserFormData() }), // fresh object
  },
  STAFF: {
    service: () => staffForm.useServiceFormStaff(),
    schema: staffForm.staffFormSchema,
    formData: () => ({ ...staffForm.getStaffFormData() }), // fresh object
  },
  CLASS: {
    service: () => classForm.useServiceFormClass(),
    schema: classForm.classFormSchema,
    formData: () => ({ ...classForm.getClassFormData() }), // fresh object
  },
  SUBJECT: {
    service: () => subjectForm.useServiceFormSubject(),
    schema: subjectForm.subjectFormSchema,
    formData: () => ({ ...subjectForm.getSubjectFormData() }), // fresh object
  },
  STUDENT: undefined,
  SCHEDULE_SLOT_BY_CLASS: {
    service: () => scheduleSlotForm.useServiceFormScheduleSlot(),
    schema: scheduleSlotForm.scheduleFormSchemaByClass,
    formData: () => ({ ...scheduleSlotForm.getScheduleFormData() }), // fresh object
  },
  SCHEDULE_SLOT_BY_TEACHER: {
    service: () => scheduleSlotForm.useServiceFormScheduleSlot(),
    schema: scheduleSlotForm.scheduleFormSchemaByTeacher,
    formData: () => ({ ...scheduleSlotForm.getScheduleFormData() }), // fresh object
  },
};

// -------------------- EDIT FORMS --------------------
export const formRegistryEdit: FormRegistryEdit = {
  USER: {
    service: () => userForm.useServiceFormUser(),
    schema: userForm.userFormSchemaEdit,
    formData: () => userForm.getUserFormDataEdit(), // reactive object
  },
  STAFF: {
    service: () => staffForm.useServiceFormStaff(),
    schema: staffForm.staffFormSchemaEdit,
    formData: () => staffForm.getStaffFormDataEdit(), // reactive object
  },
  CLASS: {
    service: () => classForm.useServiceFormClass(),
    schema: classForm.classFormSchemaEdit,
    formData: () => classForm.getClassFormDataEdit(), // reactive object
  },
  SUBJECT: {
    service: () => subjectForm.useServiceFormSubject(),
    schema: subjectForm.subjectFormSchemaEdit,
    formData: () => subjectForm.getSubjectFormDataEdit(), // reactive object
  },
  STUDENT: {
    service: () => studentForm.useServiceFormStudentInfo(),
    schema: studentForm.studentInfoFormSchemaEdit,
    formData: () => studentForm.getStudentInfoFormDataEdit(), // reactive object
  },
  SCHEDULE_SLOT_BY_CLASS: {
    service: () => scheduleSlotForm.useServiceFormScheduleSlot(),
    schema: scheduleSlotForm.scheduleFormSchemaEdit,
    formData: () => scheduleSlotForm.getScheduleFormDataEdit(), // reactive object
  },
  SCHEDULE_SLOT_BY_TEACHER: {
    service: () => scheduleSlotForm.useServiceFormScheduleSlot(),
    schema: scheduleSlotForm.scheduleFormSchemaEdit,
    formData: () => scheduleSlotForm.getScheduleFormDataEdit(), // reactive object
  },
};
