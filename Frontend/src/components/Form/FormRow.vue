<script
  lang="ts"
  setup
  generic="T extends Record<string, any> = Record<string, any>"
>
import { defineProps, reactive } from "vue";
import FormField from "./FormField.vue";
import type { Field } from "../types/form";
import type { FormInstance } from "element-plus";

const props = defineProps<{
  rowFields: Field<T>[];
  form: Partial<T>;
  fileList: Record<string, any>;
  useElForm: boolean;
  elFormRef?: FormInstance | null;
}>();

// Make fileList reactive locally if needed
const localFileList = reactive({ ...props.fileList });

// Update localFileList when FormField emits change
function handleUploadChange(key: string, files: any) {
  localFileList[key] = Array.isArray(files) ? files : [files];
}

// Optional: handle file remove
function handleUploadRemove(key: string, file: any) {
  if (localFileList[key]) {
    localFileList[key] = localFileList[key].filter((f: any) => f !== file);
  }
}
</script>

<template>
  <el-row :gutter="20" class="mb-4">
    <el-col
      v-for="subField in rowFields"
      :key="subField.key"
      :span="24 / rowFields.length"
    >
      <FormField
        :field="subField"
        :form="form"
        :el-form-ref="props.elFormRef"
        :file-list="localFileList"
        :use-el-form="useElForm"
        @update:modelValue="(val) => Object.assign(form, val)"
        @updateField="(key, value) => (form[key] = value)"
        @onUploadChange="handleUploadChange"
        @onUploadRemove="handleUploadRemove"
      />
    </el-col>
  </el-row>
</template>
