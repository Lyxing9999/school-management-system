<script setup lang="ts">
import { computed, ref } from "vue";
import RemoteSelect from "~/components/selects/base/RemoteSelect.vue";
import { adminService } from "~/api/admin";

const adminApi = adminService();

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

// Cache so we don't refetch every time
const cachedClasses = ref<any[]>([]);

const fetchClasses = async () => {
  if (cachedClasses.value.length > 0) {
    return cachedClasses.value;
  }
  const res = await adminApi.subject.listSubjectNameSelect();
  cachedClasses.value = res?.items ?? [];
  return cachedClasses.value;
};

// Simple bridge v-model so parent stays in control
const innerValue = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});
</script>

<template>
  <RemoteSelect
    v-model="innerValue"
    :fetcher="fetchClasses"
    label-key="label"
    value-key="value"
    :placeholder="props.placeholder ?? 'Select subject'"
    :disabled="props.disabled"
    :multiple="props.multiple"
    :size="props.size"
    clearable
  />
</template>
