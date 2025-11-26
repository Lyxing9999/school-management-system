<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

const props = defineProps<{
  modelValue: string | null;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string | null): void;
}>();

const fetchStudents = async () => {
  const res = await adminApi.user.getStudentNameSelect();
  return res?.items ?? [];
};
</script>

<template>
  <RemoteSelect
    :model-value="props.modelValue"
    @update:modelValue="(v) => emit('update:modelValue', v)"
    :fetcher="fetchStudents"
    label-key="username"
    value-key="id"
    :placeholder="placeholder ?? 'Select student'"
    :disabled="disabled"
    :multiple="multiple"
    clearable
  />
</template>
