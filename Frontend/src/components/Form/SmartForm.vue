<script setup lang="ts" generic="T extends Record<string, any>">
import { reactive, ref, watch, onMounted, type UnwrapRef } from "vue";
import type { Field } from "../types/form";
import { ElUpload, type UploadUserFile, type FormInstance } from "element-plus";
import FormRow from "./FormRow.vue";
import FormField from "./FormField.vue";

const props = defineProps<{
  modelValue: Partial<T>;
  fields: Field<T>[];
  useElForm: boolean;
  formProps?: Record<string, any>;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: "save", form: T): void;
  (e: "cancel"): void;
  (e: "update:modelValue", form: Partial<T>): void;
}>();

const form = reactive({ ...props.modelValue }) as UnwrapRef<Partial<T>>;
const fileList = ref<Record<string, UploadUserFile[]>>({});

// Parent → local
watch(
  () => props.modelValue,
  (val) => {
    Object.assign(form, val || {});
  },
  { deep: true }
);

// Local → parent
watch(form, (val) => emit("update:modelValue", { ...val }), { deep: true });

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
  setFormValue(key as any, lastFile?.raw || lastFile?.url || null);
};

const handleUploadRemove = (key: string, file: UploadUserFile) => {
  setFormValue(key as any, null);
  fileList.value[key] = (fileList.value[key] || []).filter(
    (f) => f.uid !== file.uid
  );
};

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

const elFormRef = ref<FormInstance | null>(null);

const handleSave = () => {
  console.log(elFormRef.value);
  if (!elFormRef.value) return;
  elFormRef.value.validate((valid) => {
    if (valid) {
      console.log("ths");
      emit("save", form as T);
    }
  });
};
</script>

<template>
  <!-- When using Element Plus form -->
  <el-form
    v-if="useElForm"
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
        :el-form-ref="elFormRef"
        @upload-remove="handleUploadRemove"
      />

      <!-- Single field -->
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

    <div class="flex justify-end gap-2 mt-4">
      <BaseButton type="default" @click="emit('cancel')">Cancel</BaseButton>
      <BaseButton type="info" :loading="props.loading" @click="handleSave">
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

    <div class="flex justify-end gap-2 mt-4">
      <BaseButton type="default" @click="emit('cancel')">Cancel</BaseButton>
      <BaseButton type="info" :loading="props.loading" @click="handleSave">
        Save
      </BaseButton>
    </div>
  </div>
</template>
