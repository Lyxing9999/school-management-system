<script setup lang="ts">
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { teacherService } from "~/api/teacher";

const teacherApi = teacherService();

const props = defineProps<{
  modelValue: string | null;
  classId: string; // which class we’re loading subjects for
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string | null): void;
}>();

// Calls: GET /teacher/me/classes/<class_id>/subjects
const fetchSubjects = async () => {
  if (!props.classId) return [];
  const res = await teacherApi.teacher.listSubjectsInClass(props.classId);
  console.log(res);
  // res should be TeacherSubjectSelectNameListDTO
  // { items: [{ id: string, name: string | code: string, ... }, ...] }
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
    :fetcher="fetchSubjects"
    label-key="name"
    value-key="id"
    :placeholder="placeholder ?? 'Select subject'"
    :disabled="disabled"
    :multiple="multiple"
    clearable
  />
</template>
