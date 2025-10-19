// ~/schemas/columns/academic/classColumns.ts
import { ref } from "vue";
import {
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElSwitch,
  ElInputTag,
} from "element-plus";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { BaseClassDataDTO } from "~/api/types/baseClass";

// Reactive student options for remote search
export const studentSelectOptions = ref<{ label: string; value: string }[]>([]);

// Loading state for remote search
export const loading = ref(false);

// Initial class data
export const initialClassData: BaseClassDataDTO = {
  id: "",
  name: "",
  grade: 1,
  max_students: 30,
  status: true,
  academic_year: "",
  code: "",
  class_room: null,
  homeroom_teacher: "",
  subjects: [],
  students: [],
  deleted: false,
  deleted_at: "",
  deleted_by: "",
  created_at: "",
  created_by: "",
  updated_at: "",
  updated_by: "",
};

// Column configuration
export const classColumns: ColumnConfig<BaseClassDataDTO>[] = [
  {
    field: "name",
    label: "Class Name",
    autoSave: true,
    component: ElInput,
    minWidth: "150px", // flexible, grows/shrinks with screen
  },
  {
    field: "grade",
    label: "Grade",
    autoSave: true,
    component: ElInputNumber,
    width: "80px", // small fixed width
    align: "center",
    componentProps: { size: "small", style: "width: 80px" },
    customClass: "text-center",
  },
  {
    field: "max_students",
    label: "Max Students",
    component: ElInputNumber,
    width: "100px", // fixed
    align: "center",
    componentProps: { size: "small", style: "width: 100px" },
    customClass: "text-center",
  },
  {
    field: "academic_year",
    label: "Academic Year",
    component: ElInput,
    width: "120px", // fixed
  },
  {
    field: "code",
    label: "Class Code",
    component: ElInput,
    width: "120px", // fixed
  },
  {
    field: "class_room",
    label: "Classroom",
    component: ElInput,
    width: "120px", // fixed
  },
  {
    field: "homeroom_teacher",
    label: "Homeroom Teacher",
    minWidth: "150px", // flexible
  },
  {
    field: "subjects",
    label: "Subjects",
    useSlots: true,
    slotName: "subjectSlot",
    minWidth: "200px",
  },
  {
    field: "students",
    label: "Students",
    component: ElSelect,
    minWidth: "180px", // flexible
    componentProps: {
      placeholder: "Select students",
      multiple: true,
      filterable: true,
      remote: true,
      remoteMethod: async (query: string) => {
        loading.value = true;
        await new Promise((r) => setTimeout(r, 300));
        studentSelectOptions.value = [
          { label: `Student ${query} 1`, value: `${query}-1` },
          { label: `Student ${query} 2`, value: `${query}-2` },
        ];
        loading.value = false;
      },
      loading,
    },
    childComponent: ElOption,
  },
  {
    field: "status",
    label: "Status",
    component: ElSwitch,
    width: "100px",
    autoSave: true,
    componentProps: {
      activeValue: true,
      inactiveValue: false,
    },
    inlineEditActive: true,
  },
  {
    field: "created_by",
    label: "Created By",
    component: ElInput,
    componentProps: { disabled: true },
    minWidth: "140px", // flexible
    inlineEditActive: true,
  },
  {
    field: "id",
    operation: true,
    label: "Operation",
    inlineEditActive: true,
    fixed: "right",
    align: "center",
    width: "200px", // fixed
    smartProps: {
      headerStyle: { background: "#6B3FA0", color: "#fff" },
      columnClass: "operation-column",
    },
  },
];
