import type { Field } from "~/components/types/form";
import BaseNameSelect from "~/components/Base/BaseNameSelect.vue";
import type {
  AdminCreateSubject,
  AdminUpdateSubject,
} from "~/api/admin/subject/dto";
import { ElInput } from "element-plus";

const { $adminService } = useNuxtApp();
export const subjectFormSchema: Field<AdminCreateSubject>[] = [
  {
    key: "name",
    label: "Subject Name",
    component: ElInput,
    componentProps: {
      placeholder: "Enter subject name",
    },
  },
  {
    key: "teacher_id",
    label: "Teacher",
    component: BaseNameSelect,
    componentProps: {
      fetchFn: async (search: string) => {
        const data = await $adminService.getStaffNameSelect(search, "teacher");

        return data.map((s: any) => ({ label: s.staff_name, value: s._id }));
      },
      placeholder: "Enter teacher name",
      multiple: true, 
      collapseTags: false, 
    },
  },
];

export const subjectFormSchemaEdit: Field<AdminUpdateSubject>[] =
  subjectFormSchema as unknown as Field<AdminUpdateSubject>[];
