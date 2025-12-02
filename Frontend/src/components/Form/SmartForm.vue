<script setup lang="ts" generic="T extends Record<string, any>">
import { reactive, ref, watch, onMounted, computed } from "vue";
import type { Field } from "../types/form";
import { ElUpload, type UploadUserFile, type FormInstance } from "element-plus";
import FormRow from "./FormRow.vue";
import FormField from "./FormField.vue";

const props = defineProps<{
  modelValue: Partial<T>;
  fields: Field<T>[];
  useElForm: boolean;
  formProps?: Record<string, any>;
  loading?: boolean; // parent-controlled (API save, etc.)
}>();

const emit = defineEmits<{
  (e: "save", form: T): void;
  (e: "cancel"): void;
}>();

const form = reactive<Record<string, any>>({});
const fileList = ref<Record<string, UploadUserFile[]>>({});

// local flag for “user clicked save”
const submitting = ref(false);

// combined loading state for the button:
// - parent loading (API call)
// - OR local submitting (validation in progress)
const buttonLoading = computed(() => !!props.loading || submitting.value);

// parent -> local (one-way, immediate)
watch(
  () => props.modelValue,
  (val) => {
    Object.keys(form).forEach((k) => delete form[k]);
    Object.assign(form, (val || {}) as Record<string, any>);
  },
  { deep: false, immediate: true }
);

const setFormValue = (key: keyof T | string, value: any) => {
  form[key as string] = value;
};

const getFormValue = (key: keyof T | string) => {
  return form[key as string];
};

const getUploadFileList = (
  urlOrUrls: string | string[] | UploadUserFile[] | null | undefined
): UploadUserFile[] => {
  if (!urlOrUrls) return [];
  const list = Array.isArray(urlOrUrls) ? urlOrUrls : [urlOrUrls];
  return list.map((item) =>
    typeof item === "string"
      ? {
          uid: Date.now() + Math.floor(Math.random() * 1000),
          name: item.split("/").pop() || "File",
          url: item.startsWith("/") ? `${window.location.origin}${item}` : item,
          status: "success" as const,
        }
      : item
  );
};

const getFileUrl = (file?: UploadUserFile) => {
  if (!file) return undefined;
  return file.url ?? (file.raw ? URL.createObjectURL(file.raw) : undefined);
};

const handleUploadChange = (
  key: string,
  files: UploadUserFile[] | UploadUserFile | string
) => {
  const normalizedFiles: UploadUserFile[] =
    typeof files === "string"
      ? getUploadFileList(files)
      : Array.isArray(files)
      ? files.map((f) => ({ ...f, url: getFileUrl(f) }))
      : [{ ...files, url: getFileUrl(files) }];

  fileList.value[key] = normalizedFiles;
  const lastFile = normalizedFiles[normalizedFiles.length - 1];
  setFormValue(key, lastFile?.raw || lastFile?.url || null);
};

const handleUploadRemove = (key: string, file: UploadUserFile) => {
  setFormValue(key, null);
  fileList.value[key] = (fileList.value[key] || []).filter(
    (f) => f.uid !== file.uid
  );
};

onMounted(() => {
  props.fields.forEach((field) => {
    const fieldsToCheck = field.row ?? [field];
    fieldsToCheck.forEach((f) => {
      if (!f.key) return;
      const key = f.key as keyof T;
      if (f.component === ElUpload && getFormValue(key)) {
        fileList.value[f.key as string] = getUploadFileList(getFormValue(key));
      }
    });
  });
});

const elFormRef = ref<FormInstance | null>(null);

const handleSave = async () => {
  // No Element Plus form: just emit
  if (!props.useElForm || !elFormRef.value) {
    emit("save", form as T);
    return;
  }

  submitting.value = true;
  try {
    // Promise-based validate; throws on invalid
    const valid = await elFormRef.value.validate();

    // Element Plus validate() returns true or throws,
    // but we keep check for safety.
    if (valid !== false) {
      emit("save", form as T);
    }
  } catch {
    // Validation failed: do nothing, stay on form
  } finally {
    // Local “validation in progress” is over.
    // Parent may still keep button loading via props.loading
    submitting.value = false;
  }
};
</script>

<template>
  <el-form
    v-if="useElForm"
    :model="form"
    ref="elFormRef"
    v-bind="props.formProps"
  >
    <template v-for="(field, index) in props.fields" :key="index">
      <FormRow
        v-if="field.row"
        :rowFields="field.row"
        :form="form"
        :file-list="fileList"
        :use-el-form="useElForm"
        :el-form-ref="elFormRef"
        @upload-change="handleUploadChange"
        @upload-remove="handleUploadRemove"
      />
      <FormField
        v-else
        :field="field"
        :form="form"
        :file-list="fileList"
        :use-el-form="useElForm"
        :el-form-ref="elFormRef"
        @upload-change="handleUploadChange"
        @upload-remove="handleUploadRemove"
      />
    </template>

    <div class="flex justify-end gap-1 mt-2">
      <BaseButton type="default" @click="emit('cancel')">Cancel</BaseButton>
      <BaseButton
        type="primary"
        class="pr-4 pb-4"
        :loading="buttonLoading"
        @click="handleSave"
      >
        Save
      </BaseButton>
    </div>
  </el-form>

  <!-- Plain div mode (no Element Plus validation) -->
  <div v-else>
    <template v-for="(field, index) in props.fields" :key="index">
      <FormRow
        v-if="field.row"
        :rowFields="field.row"
        :form="form"
        :file-list="fileList"
        :use-el-form="false"
        :el-form-ref="undefined"
        @upload-change="handleUploadChange"
        @upload-remove="handleUploadRemove"
      />
      <FormField
        v-else
        :field="field"
        :form="form"
        :file-list="fileList"
        :use-el-form="false"
        :el-form-ref="undefined"
        @upload-change="handleUploadChange"
        @upload-remove="handleUploadRemove"
      />
    </template>

    <div class="flex justify-end gap-1 mt-2">
      <BaseButton type="default" @click="emit('cancel')">Cancel</BaseButton>
      <BaseButton
        type="primary"
        class="pr-4 pb-4"
        :loading="buttonLoading"
        @click="handleSave"
      >
        Save
      </BaseButton>
    </div>
  </div>
</template>
