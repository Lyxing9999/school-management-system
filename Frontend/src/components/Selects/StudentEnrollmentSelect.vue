<script setup lang="ts">
import { computed } from "vue";
import RemoteSelect from "~/components/Selects/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

type StudentValue = string | string[] | null;
type SelectOption = { value: string; label: string };

const props = defineProps<{
  classId: string;
  modelValue: StudentValue;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  loading?: boolean;
  preloadedOptions?: SelectOption[];
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: StudentValue): void;
}>();

const innerValue = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

function normalizeApiItems(res: any): SelectOption[] {
  const items = res?.data?.items ?? res?.items ?? [];
  return (items as any[]).map((x) => ({
    value: String(x.value ?? x.id ?? x._id),
    label: String(x.label ?? x.name ?? x.value),
  }));
}

const fetchEligible = async (): Promise<SelectOption[]> => {
  if (!props.classId) return [];
  const res = await adminApi.class.listStudentsForEnrollmentSelect(
    props.classId
  );
  return normalizeApiItems(res);
};

const reloadKey = computed(
  () => `${props.classId}|${(props.preloadedOptions ?? []).length}`
);
</script>

<template>
  <div class="relative" v-loading="!!loading">
    <RemoteSelect
      v-model="innerValue"
      :fetcher="fetchEligible"
      :preloaded-options="preloadedOptions"
      :hide-preloaded-in-dropdown="true"
      :reload-key="reloadKey"
      label-key="label"
      value-key="value"
      :placeholder="placeholder ?? 'Select students to enroll'"
      :disabled="disabled || !!loading"
      :multiple="multiple"
      clearable
    />
  </div>
</template>
