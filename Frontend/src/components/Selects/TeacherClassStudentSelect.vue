<!-- ~/components/Selects/TeacherStudentSelect.vue -->
<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { teacherService } from "~/api/teacher";
import { computed } from "vue";

const teacherApi = teacherService();

const props = defineProps<{
  modelValue: string | string[] | null;
  classId: string;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  size?: "small" | "default" | "large";
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string | string[] | null): void;
}>();

const fetchStudents = async () => {
  if (!props.classId) return [];
  const res = await teacherApi.teacher.listStudentNamesOptionsClass(
    props.classId
  );
  return res?.items ?? [];
};
const innerValue = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});
</script>

<template>
  <RemoteSelect
    v-model="innerValue"
    :fetcher="fetchStudents"
    :reload-key="classId"
    label-key="label"
    value-key="value"
    :placeholder="placeholder ?? 'Select student'"
    :disabled="disabled || !classId"
    :multiple="multiple"
    :size="size"
    clearable
  />
</template>
