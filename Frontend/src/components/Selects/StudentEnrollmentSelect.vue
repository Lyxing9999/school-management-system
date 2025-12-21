<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { adminService } from "~/api/admin";
import { computed } from "vue";

const adminApi = adminService();

type StudentValue = string | string[] | null;

const props = defineProps<{
  classId: string;
  modelValue: StudentValue;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  loading?: boolean;

  options?:
    | { value: string; label: string }[]
    | (() => { value: string; label: string }[]);
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: StudentValue): void;
}>();
watch(
  () => props.classId,
  () => {
    fetchAllStudents();
  }
);
const fetchAllStudents = async () => {
  if (!props.classId) return [];
  const res = await adminApi.class.listStudentsForEnrollmentSelect(
    props.classId
  );
  return res?.items ?? [];
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
