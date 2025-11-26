=
<script
  lang="ts"
  setup
  generic="T extends Record<string, any> = Record<string, any>"
>
import { watch, nextTick } from "vue";
import { ElFormItem, ElInput, ElUpload, type FormInstance } from "element-plus";
import DisplayOnlyField from "~/components/Form/DisplayOnlyField.vue";
import type { Field } from "../types/form";
import type { UploadUserFile } from "element-plus";

const props = defineProps<{
  field: Field<T>;
  form: Partial<T>;
  elFormRef?: FormInstance | null;
  fileList: Record<string, UploadUserFile[]>;
  useElForm: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: Partial<T>): void;
  (e: "updateField", key: keyof T, value: any): void;
}>();

const getOptionsForField = (field: Field<T>) => {
  let rawOptions: { value: any; label: string }[] = [];
  const src = field.childComponentProps?.options;

  if (!src) return rawOptions;

  if (typeof src === "function") {
    const result = src();
    rawOptions = Array.isArray(result) ? result : [];
  } else if (Array.isArray(src)) {
    rawOptions = src;
  } else if (isRef(src) && Array.isArray(src.value)) {
    rawOptions = src.value;
  }

  return rawOptions;
};

watch(
  () => props.form,
  (val) => {
    emit("update:modelValue", JSON.parse(JSON.stringify(val)));
  },
  { deep: true }
);

const handleInput = async () => {
  if (!props.useElForm || !props.field.key) return;
  const formInstance = props.elFormRef as FormInstance | null;
  if (!formInstance) return;
  await nextTick();
  formInstance.validateField(props.field.key as string);
};
</script>

<template>
  <ElFormItem
    v-if="useElForm"
    :prop="field.key"
    v-bind="field.formItemProps"
    class="mb-4"
  >
    <template #label>
      <div style="display: flex; align-items: center; gap: 4px">
        <el-icon v-if="field.iconComponent">
          <component :is="field.iconComponent" />
        </el-icon>
        <span>{{ field.label }}</span>
      </div>
    </template>

    <template v-if="field.displayOnly">
      <DisplayOnlyField
        :value="props.form[props.field.key as keyof typeof props.form]"
      />
    </template>

    <ElUpload
      v-else-if="field.component === ElUpload"
      :file-list="fileList[field.key as string]"
      list-type="picture-card"
      :auto-upload="false"
      @change="(files) => $emit('upload-change', String(field.key), files)"
      @remove="(file) => $emit('upload-remove', String(field.key), file)"
      v-bind="field.componentProps"
    />

    <component
      v-else
      v-model="props.form[field.key as keyof typeof props.form]"
      :is="field.component || ElInput"
      v-bind="field.componentProps"
      @input="handleInput"
      @change="handleInput"
      @blur="handleInput"
      @update:modelValue="handleInput"
    >
      <component
        v-for="opt in getOptionsForField(field)"
        :is="field.childComponent"
        :key="opt.value"
        :label="opt.label"
        :value="opt.value"
      />
    </component>
  </ElFormItem>
</template>
