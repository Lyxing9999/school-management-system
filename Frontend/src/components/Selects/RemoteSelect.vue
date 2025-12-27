<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { ElSelect, ElOption } from "element-plus";

interface Option<T = any> {
  label: string;
  value: T;
  raw?: any;
}

const props = defineProps<{
  modelValue: any;
  fetcher: () => Promise<any[]>;
  labelKey?: string;
  valueKey?: string;
  placeholder?: string;
  disabled?: boolean;
  clearable?: boolean;
  multiple?: boolean;
  // optional key to force refetch when something changes (e.g. classId)
  reloadKey?: string | number | boolean | null;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: any): void;
}>();

const options = ref<Option[]>([]);
const loading = ref(false);

// Internal v-model for ElSelect.
// Start empty; we will sync to props.modelValue *after* options are loaded.
const innerValue = ref<any>(props.multiple ? [] : null);

/**
 * Load remote options and map to {label, value, raw}
 */
const loadOptions = async () => {
  loading.value = true;
  try {
    const data = await props.fetcher();
    const labelKey = props.labelKey ?? "label";
    const valueKey = props.valueKey ?? "value";

    options.value = data.map((item: any) => ({
      label: item[labelKey],
      value: item[valueKey],
      raw: item,
    }));
  } catch (e) {
    console.error("RemoteSelect fetch error:", e);
  } finally {
    loading.value = false;
  }
};

/**
 * Sync internal value from external modelValue.
 * Called only after options are loaded to avoid showing raw IDs.
 */
const syncFromModel = () => {
  // If parent cleared the value explicitly, respect that.
  if (props.modelValue === null || props.modelValue === undefined) {
    innerValue.value = props.multiple ? [] : null;
    return;
  }
  innerValue.value = props.modelValue;
};

// Initial load: fetch options, then sync value.
// If there is a modelValue, the user will see a spinner while options load,
// then the label — never the raw ObjectId.
onMounted(async () => {
  await loadOptions();
  syncFromModel();
});

// When parent changes v-model (from outside), keep in sync.
watch(
  () => props.modelValue,
  () => {
    // If options are already loaded, sync immediately.
    // If we're loading (e.g. reloadKey changed), next loadOptions call will sync again.
    if (!loading.value && options.value.length > 0) {
      syncFromModel();
    }
  }
);

// Emit changes up when user selects a new value.
watch(
  () => innerValue.value,
  (val) => {
    emit("update:modelValue", val);
  }
);

// Refetch when reloadKey changes (e.g. when data source changes)
watch(
  () => props.reloadKey,
  async () => {
    await loadOptions();
    syncFromModel();
    // If you want to clear selection on source change:
    // innerValue.value = props.multiple ? [] : null;
  }
);
</script>

<template>
  <ElSelect
    v-model="innerValue"
    :loading="loading"
    :placeholder="placeholder"
    :disabled="disabled"
    :clearable="clearable"
    :multiple="multiple"
    filterable
  >
    <ElOption
      v-for="opt in options"
      :key="opt.value"
      :label="opt.label"
      :value="opt.value"
    />
  </ElSelect>
</template>
