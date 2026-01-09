<script setup lang="ts">
import { computed, watch, ref } from "vue";
import RemoteSelect from "~/components/selects/base/RemoteSelect.vue";
import { teacherService } from "~/api/teacher";
import type { TeacherScheduleSlotSelectDTO } from "~/api/teacher/dto";

const api = teacherService();

const props = defineProps<{
  modelValue: string | null;
  classId: string;
  date: string; // "YYYY-MM-DD"
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  limit?: number;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string | null): void;
  (e: "selected", slot: TeacherScheduleSlotSelectDTO | null): void;
}>();

const reloadKey = ref(0);
const slotCache = ref<TeacherScheduleSlotSelectDTO[]>([]);

function emitSelectedByValue(value: string | null) {
  if (!value) {
    emit("selected", null);
    return;
  }
  const hit = slotCache.value.find((x) => String(x.value) === String(value));
  emit("selected", hit ?? null);
}

const fetchSlots = async () => {
  if (!props.classId) {
    slotCache.value = [];
    return [];
  }

  const res = await api.teacher.listScheduleSlotSelect(
    {
      class_id: props.classId,
      date: props.date,
      limit: props.limit ?? 200,
    },
    { showError: false }
  );

  const items = (res?.items ?? []) as TeacherScheduleSlotSelectDTO[];
  slotCache.value = items;

  // IMPORTANT: once cache is loaded, re-emit selected for current value
  emitSelectedByValue(props.modelValue);

  return items;
};

const innerValue = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

// If class/date changes, reset selection and force reload
watch(
  () => [props.classId, props.date],
  ([nextClass, nextDate], [prevClass, prevDate]) => {
    if (nextClass !== prevClass || nextDate !== prevDate) {
      emit("update:modelValue", null);
      emit("selected", null);
      slotCache.value = [];
      reloadKey.value++;
    }
  }
);

// When value changes, emit selected if cache already loaded
watch(
  () => props.modelValue,
  (v) => {
    emitSelectedByValue(v);
  }
);
</script>

<template>
  <RemoteSelect
    :key="reloadKey"
    v-model="innerValue"
    :fetcher="fetchSlots"
    label-key="label"
    value-key="value"
    :placeholder="placeholder ?? 'Select schedule slot'"
    :disabled="disabled || !classId"
    :multiple="multiple"
    clearable
  />
</template>
