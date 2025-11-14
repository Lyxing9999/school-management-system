<script setup lang="ts" generic="I extends Record<string, any>">
import { reactive, toRaw, watch } from "vue";
import type { FormInstance, FormProps } from "element-plus";
import type { Field } from "../types/form";
import SmartForm from "~/components/Form/SmartForm.vue";
import { ElDialog } from "element-plus";

// -------------------- Props --------------------
const props = defineProps<{
  modelValue: Partial<I>; // form data from parent (reactive)
  visible: boolean; // dialog visibility
  title?: string; // optional dialog title
  fields: Field<I>[]; // form schema fields
  elFormRef?: FormInstance; // optional Element Plus form ref
  widthDialog?: string; // dialog width
  loading?: boolean; // loading state
  formProps?: Partial<FormProps>; // extra form props
}>();

// -------------------- Emits --------------------
const emit = defineEmits<{
  (e: "update:modelValue", value: Partial<I>): void;
  (e: "update:visible", value: boolean): void;
  (e: "save", payload: Partial<I>): void;
  (e: "cancel"): void;
}>();

// -------------------- Reactive Form --------------------

const localForm = reactive<Record<string, any>>({});
props.fields.forEach((f) => {
  if (f.key) localForm[f.key] = props.modelValue?.[f.key] ?? "";
  if (f.row)
    f.row.forEach((r) => {
      if (r.key) localForm[r.key] = props.modelValue?.[r.key] ?? "";
    });
});

// Sync local → parent
watch(
  localForm,
  (val) => {
    emit("update:modelValue", toRaw(val));
  },
  {
    deep: true,
  }
);

// -------------------- Handlers --------------------
const handleCancel = () => {
  emit("cancel");
  emit("update:visible", false);
};
const handleSave = (payload: Partial<I>) => {
  emit("save", payload);
};
</script>

<template>
  <ElDialog
    :model-value="visible"
    :title="title || 'Form'"
    :width="widthDialog || '800px'"
    class="smart-dialog"
    @close="handleCancel"
  >
    <SmartForm
      v-model="localForm"
      :fields="fields"
      :use-el-form="true"
      :el-form-ref="elFormRef"
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
:deep(.el-dialog) {
  max-width: 1000px;
  border-radius: 16px;
}
:deep(.el-dialog__body) {
  padding: 20px 30px;
}
</style>
