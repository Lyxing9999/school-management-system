<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

const props = defineProps<{
  modelValue: number | null;
  placeholder?: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: number | null): void;
}>();

const fetchTeachers = async () => {
  const res = await adminApi.staff.getTeacherSelect();

  return res?.items ?? res ?? [];
};
</script>

<template>
  <RemoteSelect
    :model-value="props.modelValue"
    @update:modelValue="(v) => emit('update:modelValue', v)"
    :fetcher="fetchTeachers"
    label-key="staff_name"
    value-key="user_id"
    :placeholder="placeholder ?? 'Select teacher'"
    :disabled="disabled"
    clearable
  />
</template>
