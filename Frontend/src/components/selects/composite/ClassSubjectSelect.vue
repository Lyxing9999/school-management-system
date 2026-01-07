<script setup lang="ts">
import { computed, watch, ref } from "vue";
import RemoteSelect from "~/components/selects/base/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

const props = defineProps<{
  modelValue: string | null;
  classId: string;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string | null): void;
}>();

const reloadKey = ref(0);

const fetchSubjects = async () => {
  if (!props.classId) return [];
  const res = await adminApi.class.listSubjectsSelectInClass(props.classId);
  return res?.items ?? [];
};

const innerValue = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

// IMPORTANT: when class changes -> clear subject + refetch
watch(
  () => props.classId,
  (next, prev) => {
    if (next !== prev) {
      emit("update:modelValue", null);
      reloadKey.value++;
    }
  }
);
</script>

<template>
  <RemoteSelect
    :key="reloadKey"
    v-model="innerValue"
    :fetcher="fetchSubjects"
    label-key="label"
    value-key="value"
    :placeholder="placeholder ?? 'Select subject'"
    :disabled="disabled || !classId"
    :multiple="multiple"
    clearable
  />
</template>
