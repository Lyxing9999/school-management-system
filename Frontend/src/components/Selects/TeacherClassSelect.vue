<!-- ~/components/Selects/TeacherClassSelect.vue -->
<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { teacherService } from "~/api/teacher";

const teacherApi = teacherService();

const props = withDefaults(
  defineProps<{
    modelValue: string | string[] | null;
    placeholder?: string;
    disabled?: boolean;
    multiple?: boolean;
    size?: "small" | "default" | "large";
  }>(),
  {
    multiple: false,
    size: "default",
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", value: string | string[] | null): void;
}>();

const fetchClasses = async () => {
  const res = await teacherApi.teacher.listClassNameSelect();
  console.log(res);
  // expected: [{ id, name }, ...]
  return res?.items ?? [];
};

const innerValue = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});
</script>

<template>
  <RemoteSelect
    v-model="innerValue"
    :fetcher="fetchClasses"
    label-key="name"
    value-key="id"
    :placeholder="placeholder ?? 'Select class'"
    :disabled="disabled"
    :multiple="multiple"
    :size="size"
    clearable
  />
</template>
