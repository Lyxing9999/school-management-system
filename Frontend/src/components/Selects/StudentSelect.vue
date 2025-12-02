<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { adminService } from "~/api/admin";
import { computed } from "vue";

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

// simple in-memory cache so subsequent dialogs are instant
let cachedStudents: any[] | null = null;

const fetchStudents = async () => {
  if (cachedStudents) {
    return cachedStudents;
  }

  const res = await adminApi.user.listStudentNamesSelect();
  cachedStudents = res?.items ?? [];
  return cachedStudents;
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
    label-key="username"
    value-key="id"
    :placeholder="placeholder ?? 'Select student'"
    :disabled="disabled"
    :multiple="multiple"
    clearable
  />
</template>
