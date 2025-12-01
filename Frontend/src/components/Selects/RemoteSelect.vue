<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
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

const innerValue = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

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
    console.log(options.value);
  } catch (e) {
    console.error("RemoteSelect fetch error:", e);
  } finally {
    loading.value = false;
  }
};

onMounted(loadOptions);

// refetch when reloadKey changes (e.g. when classId changes)
watch(
  () => props.reloadKey,
  () => {
    loadOptions();
    // optional: reset selected value when data source changed
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
