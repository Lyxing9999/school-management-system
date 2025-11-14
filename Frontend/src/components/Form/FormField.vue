<script
  lang="ts"
  setup
  generic="T extends Record<string, any> = Record<string, any>"
>
import { defineProps, defineEmits, unref, type UnwrapRef, watch } from "vue";
import { ElFormItem, ElInput, ElUpload } from "element-plus";
import DisplayOnlyField from "~/components/Form/DisplayOnlyField.vue";
import type { Field } from "../types/form";
import type { UploadUserFile } from "element-plus";

const props = defineProps<{
  field: Field<T>;
  form: UnwrapRef<Partial<T>>;
  fileList: Record<string, UploadUserFile[]>;
  useElForm: boolean;
  onUploadChange?: (
    key: string,
    files: UploadUserFile[] | UploadUserFile | string
  ) => void;
  onUploadRemove?: (key: string, file: UploadUserFile) => void;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: Partial<T>): void;
  (e: "updateField", key: keyof T, value: any): void;
}>();

// Extract options for select/child components
const getOptionsForField = (field: Field<T>) => {
  let rawOptions: { value: any; label: string }[] = [];
  const options = unref(field.childComponentProps?.options) as
    | { value: any; label: string }[]
    | (() => { value: any; label: string }[])
    | undefined;

  if (typeof options === "function") {
    const result = options();
    rawOptions = Array.isArray(result) ? result : [];
  } else if (Array.isArray(options)) {
    rawOptions = options;
  }

  return rawOptions;
};

// Watch full form changes
watch(
  () => props.form,
  (val) => {
    emit("update:modelValue", JSON.parse(JSON.stringify(val)));
  },
  { deep: true }
);
</script>

<template>
  <ElFormItem
    v-if="useElForm"
    :prop="field.key"
    v-bind="field.formItemProps"
    class="mb-4"
  >
    <!-- Label with icon -->
    <template #label>
      <div style="display: flex; align-items: center; gap: 4px">
        <el-icon v-if="field.iconComponent">
          <component :is="field.iconComponent" />
        </el-icon>
        <span>{{ field.label }}</span>
      </div>
    </template>

    <!-- Display-only field -->
    <template v-if="field.displayOnly">
      <DisplayOnlyField
        :value="props.form[props.field.key as keyof typeof props.form]"
      />
    </template>

    <!-- File upload field -->
    <ElUpload
      v-else-if="field.component === ElUpload"
      :file-list="fileList[field.key as string]"
      list-type="picture-card"
      :auto-upload="false"
      @change="(files) => props.onUploadChange?.(String(field.key), files)"
      @remove="(file) => props.onUploadRemove?.(String(field.key), file)"
      v-bind="field.componentProps"
    />

    <!-- Input / Select / custom component -->
    <component
      v-else
      v-model="props.form[field.key as keyof typeof props.form]"
      :is="field.component || ElInput"
      v-bind="field.componentProps"
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
