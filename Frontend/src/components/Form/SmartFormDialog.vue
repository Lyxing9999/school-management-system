<script setup lang="ts" generic="I extends Record<string, any>">
import { reactive, toRaw, watch, ref } from "vue";
import type { FormInstance, FormProps } from "element-plus";
import type { Field } from "../types/form";
import SmartForm from "~/components/Form/SmartForm.vue";
import { ElDialog } from "element-plus";

const props = defineProps<{
  modelValue: Partial<I>;
  visible: boolean;
  title?: string;
  fields: Field<I>[];
  useElForm?: boolean;
  widthDialog?: string;
  loading?: boolean;
  formProps?: Partial<FormProps>;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: Partial<I>): void;
  (e: "update:visible", value: boolean): void;
  (e: "save", payload: Partial<I>): void;
  (e: "cancel"): void;
}>();

// local form state
const localForm = reactive<Record<string, any>>({});
props.fields.forEach((f) => {
  if (f.key) localForm[f.key] = props.modelValue?.[f.key] ?? "";
  if (f.row)
    f.row.forEach((r) => {
      if (r.key) localForm[r.key] = props.modelValue?.[r.key] ?? "";
    });
});

// sync local → parent
watch(
  localForm,
  (val) => {
    emit("update:modelValue", toRaw(val));
  },
  { deep: true }
);

const handleCancel = () => {
  emit("cancel");
  emit("update:visible", false);
};

const handleSave = async (payload: Partial<I>) => {
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
