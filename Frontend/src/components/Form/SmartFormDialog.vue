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
  width?: string; // e.g. "60%", "800px", "400"
  loading?: boolean;
  formProps?: Partial<FormProps>;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: Partial<I>): void;
  (e: "update:visible", value: boolean): void;
  (e: "save", payload: Partial<I>): void;
  (e: "cancel"): void;
}>();

// Bridge `v-model` from parent, but only for passing into SmartForm
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

// 1) Extract a numeric width from props.width
const numericWidth = computed(() => {
  if (!props.width) return 800; // default if nothing provided

  // handle "800px", "60%", "400", etc.
  const match = String(props.width).match(/\d+/);
  if (!match) return 800;

  const n = Number(match[0]);
  if (Number.isNaN(n) || n <= 0) return 800;
  return n;
});

// 2) Decide column count based on width
//    - narrow dialog  => 1 column
//    - medium dialog  => 2 columns
//    - wide dialog    => 3 columns
const colSkeleton = computed(() => {
  const w = numericWidth.value;

  if (w <= 480) return 1;
  if (w <= 900) return 2;
  return 3;
});

// 3) Decide row count based on field count and columns
//    Basic heuristic: rows ≈ ceil(fields / columns), but minimum 3 rows
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
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    @close="handleCancel"
  >
    <div v-if="loading" class="p-4">
      <el-skeleton :rows="rowSkeleton" :columns="colSkeleton" animated />
    </div>

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
