import {
  userForm,
  staffForm,
  studentInfoForm,
  classForm,
  subjectForm,
  scheduleSlotForm,
} from "~/modules/forms/admin";

import type {
  AdminFormRegistryCreate,
  AdminFormRegistryEdit,
} from "../types/register/admin";

// -------------------- CREATE FORMS --------------------
export const adminFormRegistryCreate: AdminFormRegistryCreate = {
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
    schema: subjectForm.subjectFormFields,
    formData: () => ({ ...subjectForm.getSubjectFormData() }), // fresh object
  },
  SCHEDULE_SLOT: {
    service: () => scheduleSlotForm.useServiceFormScheduleSlot(),
    schema: scheduleSlotForm.scheduleFormSchema,
    formData: () => ({ ...scheduleSlotForm.getScheduleFormData() }), // fresh object
  },
};

// -------------------- EDIT FORMS --------------------
export const adminFormRegistryEdit: AdminFormRegistryEdit = {
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
  SCHEDULE_SLOT: {
    service: () => scheduleSlotForm.useServiceFormScheduleSlot(),
    schema: scheduleSlotForm.scheduleFormSchemaEdit,
    formData: () => scheduleSlotForm.getScheduleFormDataEdit(), // reactive object
  },
  STUDENT: {
    service: () => studentInfoForm.useServiceFormStudentInfo(),
    schema: studentInfoForm.studentInfoFormSchemaEdit,
    formData: () => studentInfoForm.getStudentInfoFormDataEdit(), // reactive object
  },
};
