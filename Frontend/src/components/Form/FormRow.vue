<script
  setup
  lang="ts"
  generic="T extends Record<string, any> = Record<string, any>"
>
import FormField from "./FormField.vue";
import type { Field } from "../types/form";
import type { FormInstance, UploadUserFile } from "element-plus";

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
  <div class="form-row-grid">
    <FormField
      v-for="subField in rowFields"
      :key="subField.key"
      :field="subField"
      :form="form"
      :el-form-ref="elFormRef"
      :file-list="fileList"
      :use-el-form="useElForm"
      @upload-change="(key, files) => emit('upload-change', key, files)"
      @upload-remove="(key, file) => emit('upload-remove', key, file)"
    />
  </div>
</template>

<style scoped>
.form-row-grid {
  display: grid;
  gap: 20px;
  margin-bottom: 16px;

  /* CTO default: responsive without breakpoints */
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

/* Optional: slightly tighter on very small screens */
@media (max-width: 480px) {
  .form-row-grid {
    gap: 12px;
    grid-template-columns: 1fr;
  }
}
</style>
