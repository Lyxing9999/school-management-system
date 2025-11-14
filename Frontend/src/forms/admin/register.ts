import {
  userForm,
  staffForm,
  studentForm,
  classForm,
  subjectForm,
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
};
