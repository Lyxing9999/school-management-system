import type { Field } from "~/components/types/form";
import BaseNameSelect from "~/components/Base/BaseNameSelect.vue";
import type {
  AdminCreateSubject,
  AdminUpdateSubject,
} from "~/api/admin/admin.dto";
import { ElInput } from "element-plus";
import { useNuxtApp } from "#app";

const { $adminService } = useNuxtApp(); // get service from Nuxt plugin

// ------------------ Subject Form Schema ------------------
export const subjectFormSchema: Field<AdminCreateSubject>[] = [
  {
    key: "name",
    label: "Subject Name",
    labelWidth: "120px",
    component: ElInput,
    componentProps: {
      placeholder: "Enter subject name",
    },
    rules: [
      { required: true, message: "Subject name is required", trigger: "blur" },
      { min: 2, message: "At least 2 characters", trigger: "blur" },
    ],
  },
  {
    key: "teacher_id",
    label: "Teacher",
    labelWidth: "120px",
    component: BaseNameSelect,
    componentProps: {
      fetchFn: async (search: string) => {
        const data = await $adminService.getStaffNameSelect(search, "teacher");

        return data.map((s: any) => ({ label: s.staff_name, value: s._id }));
      },
      placeholder: "Enter teacher name",
      multiple: true, // ✅ allow selecting multiple teachers
      collapseTags: false, // show all selected names instead of "3 selected"
    },
    rules: [
      { required: true, message: "Teacher is required", trigger: "blur" },
    ],
  },
];

// ------------------ Edit Form Schema ------------------
export const subjectFormSchemaEdit: Field<Partial<AdminUpdateSubject>>[] =
  subjectFormSchema.map((f) => ({ ...f }));

// ------------------ Data Form Schema ------------------
export const subjectFormData: AdminCreateSubject = {
  name: "",
  teacher_id: [],
};

export const subjectFormDataEdit: AdminUpdateSubject = {
  name: "",
  teacher_id: [],
};
