import { computed, onMounted, ref } from "vue";
import {
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElSwitch,
  ElInputTag,
} from "element-plus";
import type { Field } from "~/components/types/form";
import type {
  AcademicGetTeacherSelectResponseList,
  AcademicGetTeacherSelect,
} from "~/api/academic/academic.dto";

const teacherOptions = ref<{ value: string; label: string }[]>([]);
const studentSelectOptions = ref<{ value: string; label: string }[]>([]);
const loading = ref(false);

const { $academicService } = useNuxtApp();

const remoteMethod = async (query: string) => {
  if (!query) {
    studentSelectOptions.value = [];
    return;
  }
  loading.value = true;
  try {
    const data = await $academicService.getTeacherForSelect(query);
    studentSelectOptions.value = (data ?? []).map(
      (item: AcademicGetTeacherSelect) => ({
        value: item.user_id,
        label: item.staff_name,
      })
    );
  } finally {
    loading.value = false;
  }
};

const loadTeacherOptions = async () => {
  const data = await $academicService.getTeacherNames();
  teacherOptions.value = (data ?? []).map((item: AcademicGetTeacherSelect) => ({
    value: item.user_id,
    label: item.staff_name,
  }));
};

export const initialClassData = {
  name: "",
  grade: 1,
  max_students: 30,
  homeroom_teacher: [] as string[],
  students: [] as string[],
  subjects: [] as string[],
  status: true,
};

export const useClassFormSchema = () => {
  onMounted(async () => {
    await loadTeacherOptions();
    await remoteMethod("");
  });
  return computed<Field[]>(() => [
    {
      key: "name",
      label: "Class Name",
      labelWidth: "120px",
      component: ElInput,
      componentProps: { placeholder: "Enter class name", clearable: true },
    },
    {
      key: "grade",
      label: "Grade",
      labelWidth: "120px",
      component: ElInputNumber,
      componentProps: { min: 1, max: 12, controlsPosition: "right" },
    },
    {
      key: "max_students",
      label: "Max Students",
      labelWidth: "120px",
      component: ElInputNumber,
      componentProps: { min: 1, max: 100, controlsPosition: "right" },
    },
    {
      key: "homeroom_teacher",
      label: "Homeroom Teacher",
      labelWidth: "200px",
      component: ElSelect,
      componentProps: { placeholder: "Select teacher", clearable: true },
      childComponent: ElOption,
      childComponentProps: {
        options: computed(() => teacherOptions.value),
      },
    },
    {
      key: "students",
      label: "Students",
      labelWidth: "200px",
      component: ElSelect,
      componentProps: {
        multiple: true,
        filterable: true,
        remote: true,
        reserveKeyword: true,
        placeholder: "Search students",
        clearable: true,
        loading: loading.value,
        remoteMethod,
      },
      childComponent: ElOption,
      childComponentProps: {
        options: computed(() => studentSelectOptions.value),
      },
    },
    {
      key: "subjects",
      label: "Subjects",
      labelWidth: "200px",
      component: ElInputTag,
      componentProps: { placeholder: "Enter subjects", clearable: true },
    },
    {
      key: "status",
      label: "Status",
      labelWidth: "100px",
      component: ElSwitch,
    },
  ]);
};
