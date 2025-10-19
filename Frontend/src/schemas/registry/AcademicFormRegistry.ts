import { computed, toRefs } from "vue";
import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";
import { useFormCreate } from "~/composables/useFormCreate";
import { useFormEdit } from "~/composables/useFormEdit";
import { toInlineEditUpdateService } from "~/composables/inline-edit/useInlineEdit";

import {
  serviceFormStudentIAM,
  serviceFormStudentInfo,
} from "~/services/formServices/academicFormService";

import {
  studentFormData,
  studentFormSchema,
  studentInfoFormDataEdit,
  studentInfoFormSchemaEdit,
} from "~/schemas/forms/academic/studentForm";

import type {
  AcademicCreateStudentData,
  AcademicStudentData,
  AcademicStudentInfoUpdate,
} from "~/api/academic/academic.dto";

import type {
  CreateRegistryItem,
  EditRegistryItem,
} from "~/schemas/types/academic";

// -------------------------
// Registry
// -------------------------
export const academicFormRegistry = {
  studentIAM: serviceFormStudentIAM, // IAM-level: create/update/delete/list
  studentInfo: serviceFormStudentInfo, // Info-level: update student info only
};

// -------------------------
// Inline Edit Service
// -------------------------
export const inlineEditService = computed(() =>
  toInlineEditUpdateService<AcademicStudentData>(
    academicFormRegistry.studentIAM as UseFormService<
      any,
      Partial<AcademicStudentData>,
      AcademicStudentData,
      AcademicStudentData,
      never
    >
  )
);

// -------------------------
// Form Registries
// -------------------------
export const formRegistryCreate: CreateRegistryItem = {
  STUDENT: {
    service: academicFormRegistry.studentIAM,
    schema: studentFormSchema,
    formData: () => ({ ...studentFormData }),
  },
};

export const formRegistryEdit: EditRegistryItem = {
  STUDENT: {
    service: academicFormRegistry.studentInfo,
    schema: studentInfoFormSchemaEdit,
    formData: () => {
      const { photo_file, ...rest } = studentInfoFormDataEdit;
      return {
        ...toRefs(rest),
        photo_file,
      } as AcademicStudentInfoUpdate & { photo_file: typeof photo_file };
    },
  },
};

// -------------------------
// Composition API Hooks
// -------------------------
export const useCreateForm = () =>
  useFormCreate(
    () => formRegistryCreate.STUDENT.service,
    () => formRegistryCreate.STUDENT.formData(),
    () =>
      formRegistryCreate.STUDENT.schema as Field<AcademicCreateStudentData>[]
  );

export const useEditForm = () =>
  useFormEdit(
    () => formRegistryEdit.STUDENT.service,
    () => formRegistryEdit.STUDENT.formData(),
    () => formRegistryEdit.STUDENT.schema as Field<AcademicStudentInfoUpdate>[]
  );
