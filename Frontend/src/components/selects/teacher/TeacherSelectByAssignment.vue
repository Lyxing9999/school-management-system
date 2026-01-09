<script setup lang="ts">
import { computed, watch } from "vue";
import RemoteSelect from "~/components/selects/base/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

type SelectItem = { value: string; label: string };

const props = defineProps<{
  modelValue: string | null;
  classId: string;
  subjectId: string | null; // optional
  placeholder?: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string | null): void;
}>();

const fetchTeachers = async (): Promise<SelectItem[]> => {
  if (!props.classId) return [];

  // If subject selected -> filter by assignment
  if (props.subjectId) {
    const res = await adminApi.scheduleSlot.listTeacherSelectByAssignment({
      class_id: props.classId,
      subject_id: props.subjectId,
    });
    return res?.items ?? [];
  }

  // Otherwise fallback to all teachers
  const res = await adminApi.staff.listTeacherSelect();
  return res?.items ?? res ?? [];
};

const innerValue = computed({
  get: () => props.modelValue,
  set: (v: string | null) => emit("update:modelValue", v),
});

// When class/subject changes, reset teacher_id.
// If only 1 teacher available for that assignment, auto-select.
watch(
  () => [props.classId, props.subjectId],
  async () => {
    emit("update:modelValue", null);

    if (props.classId && props.subjectId) {
      const items = await fetchTeachers();
      if (items.length === 1) emit("update:modelValue", items[0].value);
    }
  }
);
</script>

<template>
  <RemoteSelect
    v-model="innerValue"
    :fetcher="fetchTeachers"
    label-key="label"
    value-key="value"
    :placeholder="placeholder ?? 'Select teacher'"
    :disabled="disabled || !classId"
    clearable
  />
</template>
