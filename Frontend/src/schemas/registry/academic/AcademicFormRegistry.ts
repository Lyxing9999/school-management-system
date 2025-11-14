import { computed, toRefs } from "vue";
import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";
import { useFormCreate } from "~/composables/useFormCreate";
import { useFormEdit } from "~/composables/useFormEdit";
import { toInlineEditUpdateService } from "~/composables/inline-edit/useInlineEdit";

import {
  serviceFormStudentIAM,
  serviceFormStudentInfo,
  serviceFormClass,
} from "~/services/formServices/academicFormService";



import {
  studentFormData,
  studentFormSchema,
  studentFormSchemaEdit,
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
export const academicService = {
  studentIAM: serviceFormStudentIAM, // IAM-level: create/update/delete/list
  studentInfo: serviceFormStudentInfo, // Info-level: update student info only
};

// -------------------------
// Form Registries
// -------------------------
export const formRegistryCreate: CreateRegistryItem = {
  STUDENT: {
    service: serviceFormStudentIAM,
    schema: studentFormSchema,
    formData: () => ({ ...studentFormData }),
  },
  CLASS: {
    service: serviceFormStudentIAM,
    schema: studentFormSchema,
    formData: () => ({ ...studentFormData }),
  },
};

export const formRegistryEdit: EditRegistryItem = {
  USER: {
    service: academicService.studentIAM,
    schema: studentFormSchemaEdit,
    formData: () => ({ ...studentFormData }),
  },
  STUDENT: {
    service: academicService.studentInfo,
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
