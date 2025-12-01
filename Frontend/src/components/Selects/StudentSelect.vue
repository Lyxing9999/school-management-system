<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

type StudentValue = string | string[] | null;

const props = defineProps<{
  modelValue: StudentValue;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: StudentValue): void;
}>();

const fetchStudents = async (_id?: string) => {
  const res = await adminApi.user.listStudentNamesSelect();
  return res?.items ?? [];
};

const handleUpdate = (v: StudentValue) => {
  emit("update:modelValue", v);
};
</script>

<template>
  <RemoteSelect
    :model-value="props.modelValue"
    @update:modelValue="handleUpdate"
    :fetcher="fetchStudents"
    label-key="username"
    value-key="id"
    :placeholder="placeholder ?? 'Select student'"
    :disabled="disabled"
    :multiple="multiple"
    clearable
  />
</template>
