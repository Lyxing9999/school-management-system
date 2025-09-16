import { ref, reactive, computed } from "vue";
import { AdminService } from "~/services/adminService";
import { AdminApi } from "~/api/admin/admin.api";
import type { AdminFindTeacherSelect } from "~/api/admin/admin.dto";
export const ownerOptions = ref<{ label: string; value: string }[]>([]);
export const fetchOwners = async () => {
  const adminService = new AdminService(new AdminApi(useNuxtApp().$api));
  const res = await adminService.getTeacherSelect();
  ownerOptions.value =
    res?.map((u: AdminFindTeacherSelect) => ({
      label: u.staff_name,
      value: u.id,
    })) || [];
};

import {
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElSwitch,
} from "element-plus";
import type { Field } from "~/components/types/form";

export const formData = reactive({
  name: "",
  owner_id: "",
  grade: 0,
  max_students: 30,
  status: true,
});

export const useClassFormSchema = () => {
  return computed<Field[]>(() => [
    {
      key: "name",
      labelWidth: "100px",
      label: "Class Name",
      labelPosition: "left",
      component: ElInput,
      componentProps: {
        placeholder: "Enter class name",
      },
    },

    {
      key: "owner_id",
      labelWidth: "100px",
      label: "Owner",
      labelPosition: "left",
      component: ElSelect,
      componentProps: {
        placeholder: "Enter owner name",
        style: "width: 150px",
      },
      childComponent: ElOption,
      childComponentProps: {
        options: ownerOptions.value || [],
      },
    },
    {
      key: "grade",
      label: "Grade",
      labelPosition: "left",
      labelWidth: "100px",
      component: ElInputNumber,
      componentProps: {
        type: "number",
        min: 1,
        max: 12,
      },
      rules: [
        {
          required: true,
          message: "Please input grade",
          trigger: "blur",
        },
        {
          validator: (rule: any, value: any) =>
            value >= 1 && value <= 12
              ? true
              : new Error("Grade must be between 1 and 12"),
          trigger: "blur",
        },
      ],
    },
    {
      key: "max_students",
      labelWidth: "100px",
      label: "Max Students",
      labelPosition: "left",
      component: ElInputNumber,
      componentProps: {
        type: "number",
        min: 1,
        max: 100,
      },
      rules: [
        {
          required: true,
          message: "Please input max students",
          trigger: "blur",
        },
        {
          validator: (rule: any, value: any) =>
            value >= 1 && value <= 100
              ? true
              : new Error("Max students must be between 1 and 100"),
          trigger: "blur",
        },
      ],
    },
    {
      key: "status",
      label: "Status",
      labelPosition: "left",
      component: ElSwitch,
      componentProps: {},
      rules: [
        {
          required: true,
          message: "Please input status",
          trigger: "change",
        },
      ],
    },
  ]);
};
