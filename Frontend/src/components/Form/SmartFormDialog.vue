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
</script>

<template>
  <ElDialog
    :model-value="visible"
    :title="title || 'Form'"
    :width="width || '800px'"
    class="smart-dialog"
    @close="handleCancel"
  >
    <div v-if="loading" class="p-4">
      <el-skeleton :rows="3" animated />
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
