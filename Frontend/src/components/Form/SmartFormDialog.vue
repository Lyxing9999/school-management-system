<script setup lang="ts">
import { ref, reactive, watch } from "vue";
import type { FormInstance } from "element-plus";
import type { Field } from "../types/form";
import { ElDialog } from "element-plus";
import SmartForm from "~/components/Form/SmartForm.vue";

const props = defineProps<{
  modelValue: Record<string, any>; // form data
  visible: boolean;
  title?: string;
  fields: Field[];
  width?: string;
}>();

const emit = defineEmits<{
  (e: "update:visible", val: boolean): void;
  (e: "save", form: Record<string, any>): void;
  (e: "cancel"): void;
}>();

// Local copy of form to pass into SmartForm
const localForm = reactive({ ...props.modelValue });

// Watch parent modelValue to update local form
watch(
  () => props.modelValue,
  (val) => Object.assign(localForm, val),
  { deep: true }
);

// Watch local form to sync back if needed
watch(localForm, (val) => emit("update:modelValue", { ...val }), {
  deep: true,
});

// Handle save from SmartForm
const handleSave = (form: Record<string, any>, elFormRef?: FormInstance) => {
  emit("save", form);
  emit("update:visible", false);
};

// Handle cancel from SmartForm or dialog close
const handleCancel = () => {
  emit("cancel");
  emit("update:visible", false);
};
</script>

<template>
  <ElDialog
    :model-value="visible"
    :title="title || 'Form'"
    :width="width || '800px'"
    class="smart-dialog"
    @close="handleCancel"
  >
    <SmartForm
      v-model="localForm"
      :fields="fields"
      :use-el-form="true"
      @save="handleSave"
      @cancel="handleCancel"
    />
  </ElDialog>
</template>

<style scoped>
:deep(.el-dialog) {
  max-width: 1000px; /* prevent overly wide dialog */
  border-radius: 16px;
}
:deep(.smart-dialog) {
  margin: 0 auto;
}
:deep(.el-dialog__body) {
  padding: 20px 30px;
}

:deep(.smart-form) {
  max-width: 100%;
  margin: 0 auto;
}
</style>
