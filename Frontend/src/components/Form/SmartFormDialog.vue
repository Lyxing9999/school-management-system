<script setup lang="ts" generic="I extends Record<string, any>">
import { computed } from "vue";
import type { FormProps } from "element-plus";
import type { Field } from "../types/form";
import SmartForm from "~/components/Form/SmartForm.vue";
import { ElDialog } from "element-plus";

const props = defineProps<{
  modelValue: Partial<I>;
  visible: boolean;
  title?: string;
  fields: Field<I>[];
  useElForm?: boolean;
  width?: string;
  /**
   * Loading while saving/submitting the form.
   * Used by SmartForm (buttons, disabling, etc.).
   */
  loading?: boolean;
  /**
   * Loading while initializing / fetching detail.
   * Used ONLY to show skeleton instead of form.
   */
  initialLoading?: boolean;
  formProps?: Partial<FormProps>;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: Partial<I>): void;
  (e: "update:visible", value: boolean): void;
  (e: "save", payload: Partial<I>): void;
  (e: "cancel"): void;
}>();

const localForm = computed<Partial<I>>({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const handleCancel = () => {
  emit("cancel");
  emit("update:visible", false);
};

const handleSave = (payload: Partial<I>) => {
  emit("save", payload);
};

/**
 * Helpers to compute skeleton layout based on width + field count
 */
const numericWidth = computed(() => {
  if (!props.width) return 800;
  const match = String(props.width).match(/\d+/);
  if (!match) return 800;
  const n = Number(match[0]);
  if (Number.isNaN(n) || n <= 0) return 800;
  return n;
});

const colSkeleton = computed(() => {
  const w = numericWidth.value;
  if (w <= 480) return 1;
  if (w <= 900) return 2;
  return 3;
});

const rowSkeleton = computed(() => {
  const totalFields = props.fields?.length ?? 0;
  const cols = colSkeleton.value || 1;
  if (totalFields === 0) return 3;
  const rowsByFields = Math.ceil(totalFields / cols);
  return Math.max(3, rowsByFields);
});
</script>

<template>
  <ElDialog
    :model-value="visible"
    :title="title || 'Form'"
    :width="width || '800px'"
    class="smart-dialog"
    :close-on-click-modal="!loading && !initialLoading"
    :close-on-press-escape="!loading && !initialLoading"
    @close="handleCancel"
  >
    <!-- INITIAL LOAD SKELETON (edit: fetching detail) -->
    <div v-if="initialLoading" class="p-4">
      <el-skeleton :rows="rowSkeleton" :columns="colSkeleton" animated />
    </div>

    <!-- NORMAL FORM (visible both idle + saving) -->
    <SmartForm
      v-else
      :model-value="localForm"
      :fields="fields"
      :use-el-form="true"
      :form-props="{
        statusIcon: true,
        inlineMessage: true,
        ...props.formProps,
      }"
      :loading="loading"
      @save="handleSave"
      @cancel="handleCancel"
    />
  </ElDialog>
</template>
