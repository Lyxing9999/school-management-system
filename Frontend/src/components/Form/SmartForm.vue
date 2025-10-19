<script
  lang="ts"
  setup
  generic="T extends Record<string, any> = Record<string, any>"
>
import { reactive, ref, watch, unref } from "vue";
import { ElInput, ElForm, ElFormItem } from "element-plus";
import type { Field } from "../types/form";
import type { FormInstance } from "element-plus";
import { ElUpload } from "element-plus";
import DisplayOnlyField from "~/components/Form/DisplayOnlyField.vue";

const props = defineProps<{
  modelValue: Partial<T>;
  useElForm: boolean;
  fields: Field<T>[];
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: "save", form: T, elFormRef: FormInstance | undefined): void;
  (e: "cancel", form: T, elFormRef: FormInstance | undefined): void;
  (e: "update:modelValue", value: T): void;
}>();

const form = reactive({ ...props.modelValue });
const elFormRef = ref<FormInstance>();

watch(
  () => props.modelValue,
  (val) => {
    Object.assign(form, val);
  },
  { deep: true }
);

import type { UploadUserFile } from "element-plus";
const fileList = ref<Record<string, UploadUserFile[]>>({});
watch(form, (val) => emit("update:modelValue", { ...val }), { deep: true });
const getUploadFileList = (
  urlOrUrls: string | string[] | UploadUserFile[] | null | undefined
): UploadUserFile[] => {
  if (!urlOrUrls) return [];

  const list = Array.isArray(urlOrUrls) ? urlOrUrls : [urlOrUrls];

  return list.map((item) => {
    if (typeof item === "string") {
      return {
        uid: Date.now() + Math.floor(Math.random() * 1000),
        name: item.split("/").pop() || "Photo",
        url: item.startsWith("/") ? `${window.location.origin}${item}` : item,
        status: "success" as const,
      };
    }
    return item; // already UploadUserFile
  });
};

// Map backend URL to UploadUserFile
const getOptionsForField = (field: Field) => {
  let rawOptions: any[] = [];

  // unwrap ref if needed
  const options = unref(field.childComponentProps?.options);

  if (typeof options === "function") {
    const result = options();
    rawOptions = Array.isArray(result) ? result : [];
  } else if (Array.isArray(options)) {
    rawOptions = options;
  }

  return rawOptions.map((opt) => ({ value: opt.value, label: opt.label }));
};
// Handle upload changes
const handleUploadChange = (
  key: string,
  files: UploadUserFile[] | UploadUserFile | string
) => {
  let normalizedFiles: UploadUserFile[] = [];

  if (typeof files === "string") {
    normalizedFiles = getUploadFileList(files);
  } else if (Array.isArray(files)) {
    normalizedFiles = files.map((f) => ({
      ...f,
      url: f.url || (f.raw ? URL.createObjectURL(f.raw) : undefined),
    }));
  } else {
    normalizedFiles = [
      { ...files, url: files.url || URL.createObjectURL(files.raw) },
    ];
  }

  // Update reactive fileList
  fileList.value[key] = normalizedFiles;

  // Update form[key] with raw file or URL
  const lastFile = normalizedFiles[normalizedFiles.length - 1];
  form[key] = lastFile ? lastFile.raw || lastFile.url : null;
};
const handleUploadRemove = (key: string, file: UploadUserFile) => {
  // Update form value
  form[key] = null;

  // Safely update fileList
  if (fileList.value[key]) {
    fileList.value[key] = fileList.value[key].filter((f) => f.uid !== file.uid);
  }
};
onMounted(() => {
  props.fields.forEach((field) => {
    if (field.row) {
      field.row.forEach((subField) => {
        if (subField.component === ElUpload && form[subField.key]) {
          fileList.value[subField.key] = getUploadFileList(form[subField.key]);
        }
      });
    } else {
      if (field.component === ElUpload && form[field.key]) {
        fileList.value[field.key] = getUploadFileList(form[field.key]);
      }
    }
  });
});
</script>

<template>
  <component :is="useElForm ? ElForm : 'div'" :model="form" ref="elFormRef">
    <template v-for="(field, index) in fields" :key="index">
      <!-- Row fields: multiple inline -->
      <el-row v-if="field.row" :gutter="20" class="mb-4">
        <el-col
          v-for="subField in field.row"
          :key="subField.key"
          :span="24 / field.row.length"
        >
          <ElFormItem
            v-if="useElForm"
            :label="subField.label"
            :prop="subField.key"
            :label-width="subField.labelWidth"
            :label-position="subField.labelPosition"
            :rules="subField.rules"
          >
            <!-- Label with optional icon -->
            <template #label>
              <div style="display: flex; align-items: center; gap: 4px">
                <el-icon v-if="subField.iconComponent">
                  <component :is="subField.iconComponent" />
                </el-icon>
                <span>{{ subField.label }}</span>
              </div>
            </template>

            <!-- Display-only mode -->
            <template v-if="subField.displayOnly">
              <slot name="displayOnly" :value="form[subField.key]">
                <DisplayOnlyField :value="form[subField.key]" />
              </slot>
            </template>
            <ElUpload
              v-if="subField.component === ElUpload"
              :file-list="fileList[subField.key]"
              list-type="picture-card"
              :auto-upload="false"
              @change="(files) => handleUploadChange(subField.key, files)"
              @remove="(file) => handleUploadRemove(subField.key, file)"
              v-bind="subField.componentProps"
            />

            <!-- Editable field -->
            <component
              v-else
              v-model="form[subField.key]"
              :is="subField.component || ElInput"
              v-bind="subField.componentProps"
            >
              <component
                v-if="subField.component !== ElUpload"
                v-for="opt in getOptionsForField(subField)"
                :is="subField.childComponent"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </component>
          </ElFormItem>
        </el-col>
      </el-row>

      <!-- Single field fallback -->
      <ElFormItem
        v-else
        :label="field.label"
        :prop="field.key"
        :label-width="field.labelWidth"
        :label-position="field.labelPosition"
        :rules="field.rules"
        class="mb-4"
      >
        <!-- Label with optional icon -->
        <template #label>
          <div style="display: flex; align-items: center; gap: 4px">
            <el-icon v-if="field.iconComponent">
              <component :is="field.iconComponent" />
            </el-icon>
            <span>{{ field.label }}</span>
          </div>
        </template>

        <!-- Display-only mode -->
        <template v-if="field.displayOnly">
          <slot name="displayOnly" :value="form[field.key]">
            <DisplayOnlyField :value="form[field.key]" />
          </slot>
        </template>

        <!-- Editable field -->
        <ElUpload
          v-if="field.component === ElUpload"
          :file-list="fileList[field.key] || getUploadFileList(form[field.key])"
          list-type="picture-card"
          :auto-upload="false"
          @change="(files) => handleUploadChange(field.key, files)"
          @remove="(file) => handleUploadRemove(field.key, file)"
          :show-file-list="true"
          v-bind="field.componentProps"
        />
        <component
          v-else
          v-model="form[field.key]"
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

    <!-- Operation buttons -->
    <template v-if="$slots.operation">
      <slot name="operation" :form="form" :elFormRef="elFormRef" />
    </template>
    <template v-else>
      <div class="flex justify-end gap-2 mt-4">
        <BaseButton type="default" @click="emit('cancel', form, elFormRef)">
          Cancel
        </BaseButton>
        <BaseButton
          type="info"
          class="w-20"
          :loading="loading"
          @click="emit('save', form, elFormRef)"
        >
          Save
        </BaseButton>
      </div>
    </template>
  </component>
</template>
