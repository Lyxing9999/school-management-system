<script
  lang="ts"
  setup
  generic="T extends Record<string, any> = Record<string, any>"
>
import FormField from "./FormField.vue";
import type { Field } from "../types/form";
import type { FormInstance } from "element-plus";
import type { UploadUserFile } from "element-plus";

defineProps<{
  rowFields: Field<T>[];
  form: Record<string, any>;
  fileList: Record<string, UploadUserFile[]>;
  useElForm: boolean;
  elFormRef?: FormInstance | null;
}>();

const emit = defineEmits<{
  (
    e: "upload-change",
    key: string,
    files: UploadUserFile[] | UploadUserFile | string
  ): void;
  (e: "upload-remove", key: string, file: UploadUserFile): void;
}>();
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
        :el-form-ref="elFormRef"
        :file-list="fileList"
        :use-el-form="useElForm"
        @upload-change="(key, files) => emit('upload-change', key, files)"
        @upload-remove="(key, file) => emit('upload-remove', key, file)"
      />
    </el-col>
  </el-row>
</template>
