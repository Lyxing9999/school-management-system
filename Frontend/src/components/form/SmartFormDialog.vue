<script setup lang="ts" generic="I extends Record<string, any>">
import { computed, toValue, type MaybeRefOrGetter } from "vue";
import type { FormProps } from "element-plus";
import type { Field } from "../types/form";
import SmartForm from "~/components/form/SmartForm.vue";
import { ElDialog } from "element-plus";

const props = defineProps<{
  modelValue: Partial<I>;
  visible: boolean;
  title?: string;
  fields: MaybeRefOrGetter<Field<I>[]>;
  useElForm?: boolean;

  width?: string;

  fullscreen?: boolean;
  top?: string;
  appendToBody?: boolean;
  lockScroll?: boolean;
  destroyOnClose?: boolean;

  loading?: boolean;
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

const resolvedFields = computed(() => toValue(props.fields) ?? []);

const handleCancel = () => {
  emit("cancel");
  emit("update:visible", false);
};

const handleSave = (payload: Partial<I>) => emit("save", payload);

/** Skeleton sizing when width uses clamp(...) */
const numericWidth = computed(() => {
  const raw = props.width ?? "800px";
  const s = String(raw);

  if (s.includes("clamp(")) {
    const nums = s.match(/\d+/g)?.map(Number) ?? [];
    const max = nums.length ? nums[nums.length - 1] : 800;
    return Number.isFinite(max) ? max : 800;
  }

  const match = s.match(/\d+/);
  const n = match ? Number(match[0]) : 800;
  return Number.isFinite(n) && n > 0 ? n : 800;
});

const colSkeleton = computed(() => {
  const w = numericWidth.value;
  if (w <= 480) return 1;
  if (w <= 900) return 2;
  return 3;
});

const rowSkeleton = computed(() => {
  const totalFields = resolvedFields.value.length ?? 0;
  const cols = colSkeleton.value || 1;
  if (totalFields === 0) return 3;
  return Math.max(3, Math.ceil(totalFields / cols));
});

const handleBeforeClose = (done: () => void) => {
  if (props.loading || props.initialLoading) return;
  handleCancel();
  done();
};
</script>

<template>
  <ElDialog
    :model-value="visible"
    :title="title || 'Form'"
    :width="width || '800px'"
    :fullscreen="!!fullscreen"
    :top="top || '10vh'"
    :append-to-body="appendToBody ?? true"
    :lock-scroll="lockScroll ?? true"
    :destroy-on-close="destroyOnClose ?? false"
    class="smart-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="true"
    :before-close="handleBeforeClose"
  >
    <div v-if="initialLoading" class="p-4">
      <el-skeleton :rows="rowSkeleton" :columns="colSkeleton" animated />
    </div>

    <SmartForm
      v-else
      :model-value="localForm"
      :fields="resolvedFields"
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

<style scoped>
/* Mobile dialog UX (works for both fullscreen and non-fullscreen) */
@media (max-width: 768px) {
  /* fullscreen dialog */
  :deep(.smart-dialog .el-dialog.is-fullscreen) {
    margin: 0 !important;
    border-radius: 0 !important;
  }

  :deep(.smart-dialog .el-dialog__header) {
    padding: 14px 14px 10px;
    border-bottom: 1px solid var(--border-color);
  }

  :deep(.smart-dialog .el-dialog__body) {
    padding: 12px 14px 16px;
    background: var(--color-card);
    max-height: calc(100dvh - 56px); /* safe on mobile */
    overflow: auto;
  }

  :deep(.smart-dialog .el-dialog__footer) {
    padding: 12px 14px;
    border-top: 1px solid var(--border-color);
    background: color-mix(in srgb, var(--color-card) 92%, var(--color-bg) 8%);
  }
}
</style>
