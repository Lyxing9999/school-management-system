<!-- ~/components/Selects/TeacherStudentSelect.vue -->
<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { teacherService } from "~/api/teacher";

const teacherApi = teacherService();

const props = defineProps<{
  modelValue: string | string[] | null;
  classId: string; // selected class
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
  const res = await teacherApi.teacher.listStudentNamesInClass(props.classId);
  console.log(res);
  // expected backend DTO: [{ id, name }, ...]
  return res?.items ?? [];
};
</script>

<template>
  <RemoteSelect
    :model-value="modelValue"
    @update:modelValue="(v) => emit('update:modelValue', v)"
    :fetcher="fetchStudents"
    :reload-key="classId"
    label-key="name"
    value-key="id"
    :placeholder="placeholder ?? 'Select student'"
    :disabled="disabled || !classId"
    :multiple="multiple"
    :size="size"
    clearable
  />
</template>
