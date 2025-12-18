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
  loading?: boolean;

  // passed via componentProps.options from your Field renderer
  options?:
    | { value: string; label: string }[]
    | (() => { value: string; label: string }[]);
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: StudentValue): void;
}>();

let cachedAll: { value: string; label: string }[] | null = null;

const fetchAllStudents = async () => {
  if (cachedAll) return cachedAll;

  const res = await adminApi.student.listStudentNamesSelect();
  cachedAll = res?.items ?? [];
  return cachedAll;
};

const innerValue = computed({
  get: () => props.modelValue,
  set: (v: StudentValue) => emit("update:modelValue", v),
});

const resolvedPreloaded = computed(() => {
  if (!props.options) return [];
  return typeof props.options === "function" ? props.options() : props.options;
});
</script>

<template>
  <div class="relative" v-loading="!!props.loading">
    <RemoteSelect
      v-model="innerValue"
      :fetcher="fetchAllStudents"
      :preloaded-options="resolvedPreloaded"
      label-key="label"
      value-key="value"
      :placeholder="placeholder ?? 'Select student'"
      :disabled="disabled || !!props.loading"
      :multiple="multiple"
      clearable
    />
  </div>
</template>
