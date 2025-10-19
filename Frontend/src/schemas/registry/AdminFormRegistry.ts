import { toRefs } from "vue";
import {
  serviceFormUser,
  serviceFormStaff,
  serviceFormStudent,
  serviceClass,
} from "~/services/formServices/adminFormService";
import { userFormSchema, userFormData } from "~/schemas/forms/admin/userForm";
import { userFormSchemaEdit } from "~/schemas/forms/admin/userForm";
import {
  staffFormSchema,
  staffFormData,
  staffFormSchemaEdit,
  staffFormDataEdit,
} from "~/schemas/forms/admin/staffForm";
import {
  classFormSchema,
  classFormData,
} from "~/schemas/forms/admin/classForm";
import {
  studentInfoFormSchemaEdit,
  studentInfoFormDataEdit,
} from "~/schemas/forms/admin/studentForm";
import type { AdminStudentInfoUpdate } from "~/api/admin/admin.dto";

import type {
  CreateRegistryItem,
  EditRegistryItem,
} from "~/schemas/types/admin";

// Create registry
export const formRegistryCreate: CreateRegistryItem = {
  USER: {
    service: serviceFormUser,
    schema: userFormSchema,
    formData: () => ({ ...userFormData }),
  },
  STAFF: {
    service: serviceFormStaff,
    schema: staffFormSchema,
    formData: () => ({ ...staffFormData }),
  },
  STUDENT: {
    service: serviceFormStudent,
    schema: undefined,
    formData: undefined,
  },
  CLASS: {
    service: serviceClass,
    schema: classFormSchema,
    formData: () => ({ ...classFormData }),
  },
};

// Edit registry
export const formRegistryEdit: EditRegistryItem = {
  USER: {
    service: serviceFormUser,
    schema: userFormSchemaEdit,
    formData: () => ({ ...userFormData }),
  },
  STAFF: {
    service: serviceFormStaff,
    schema: staffFormSchemaEdit,
    formData: () => ({ ...staffFormDataEdit }),
  },
  STUDENT: {
    service: serviceFormStudent,
    schema: studentInfoFormSchemaEdit,
    formData: () => {
      const { photo_file, ...rest } = studentInfoFormDataEdit;
      return {
        ...toRefs(rest),
        photo_file,
      } as AdminStudentInfoUpdate & { photo_file: typeof photo_file };
    },
  },
  CLASS: {
    service: serviceClass,
    schema: undefined,
    formData: undefined,
  },
};
