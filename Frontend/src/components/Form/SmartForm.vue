<script setup lang="ts" generic="T extends Record<string, any>">
import { reactive, ref, watch, onMounted, type UnwrapRef } from "vue";
import type { Field } from "../types/form";
import { ElUpload } from "element-plus";
import FormRow from "./FormRow.vue";
import FormField from "./FormField.vue";
import type { UploadUserFile } from "element-plus";

const props = defineProps<{
  modelValue: Partial<T>;
  fields: Field<T>[];
  useElForm: boolean;
  elFormRef?: any;
  formProps?: Record<string, any>;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: "save", form: T): void;
  (e: "cancel"): void;
  (e: "update:modelValue", form: Partial<T>): void;
}>();

// -------------------- Reactive form & file list --------------------
const form = reactive({ ...props.modelValue }) as UnwrapRef<Partial<T>>;
const fileList = ref<Record<string, UploadUserFile[]>>({});

// -------------------- Watchers --------------------
// Parent -> local
watch(
  () => props.modelValue,
  (val) => {
    Object.assign(form, val || {});
  },
  { deep: true }
);

// Local -> parent
watch(form, (val) => emit("update:modelValue", { ...val }), { deep: true });

// -------------------- Helpers --------------------
const setFormValue = <K extends keyof T>(key: K, value: any) => {
  (form as Record<string, any>)[key as string] = value;
};

const getFormValue = <K extends keyof T>(key: K) => {
  return (form as Record<string, any>)[key as string];
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

// -------------------- Upload handlers --------------------
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

// -------------------- Init --------------------
onMounted(() => {
  props.fields.forEach((field) => {
    const fieldsToCheck = field.row ?? [field];
    fieldsToCheck.forEach((f) => {
      if (!f.key) return;
      const key = f.key;
      if (f.component === ElUpload && getFormValue(key)) {
        fileList.value[key] = getUploadFileList(getFormValue(key));
      }
    });
  });
});
const handleSave = () => {
  emit("save", form);
};
</script>

<template>
  <component
    :is="useElForm ? 'el-form' : 'div'"
    :model="form"
    ref="elFormRef"
    v-bind="props.formProps"
  >
    <template v-for="(field, index) in props.fields" :key="index">
      <!-- Row of fields -->
      <FormRow
        v-if="field.row"
        :rowFields="field.row"
        :form="form"
        :file-list="fileList"
        :use-el-form="useElForm"
        @upload-change="handleUploadChange"
        @upload-remove="handleUploadRemove"
      />
      <!-- Single field -->
      <FormField
        v-else
        :field="field"
        :form="form"
        :file-list="fileList"
        :use-el-form="useElForm"
        @upload-change="handleUploadChange"
        @upload-remove="handleUploadRemove"
      />
    </template>

    <div class="flex justify-end gap-2 mt-4">
      <BaseButton type="default" @click="emit('cancel')">Cancel</BaseButton>
      <BaseButton type="info" :loading="props.loading" @click="handleSave">
        Save
      </BaseButton>
    </div>
  </component>
</template>
