<script setup lang="ts">
import RemoteSelect from "~/components/selects/base/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

const props = defineProps<{
  modelValue: string | string[] | null;
  placeholder?: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string | string[] | null): void;
}>();

const fetchTeachers = async () => {
  const res = await adminApi.staff.listTeacherSelect();

  return res?.items ?? res ?? [];
};

const innerValue = computed({
  get: () => props.modelValue,
  set: (v: string | string[] | null) => emit("update:modelValue", v),
});


</script>

<template>
  <RemoteSelect
    v-model="innerValue"
    :fetcher="fetchTeachers"
    label-key="label"
    value-key="value"
    :placeholder="placeholder ?? 'Select teacher'"
    :disabled="disabled"
    clearable
  />
</template>
