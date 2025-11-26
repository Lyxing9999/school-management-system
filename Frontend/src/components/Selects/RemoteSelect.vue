<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { ElSelect, ElOption } from "element-plus";

interface Option<T = any> {
  label: string;
  value: T;
  raw?: any;
}

const props = defineProps<{
  modelValue: any; // for v-model
  fetcher: () => Promise<any[]>; // how to load data
  labelKey?: string; // prop name in raw item
  valueKey?: string; // prop name in raw item
  placeholder?: string;
  disabled?: boolean;
  clearable?: boolean;
  multiple?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: any): void;
}>();

const options = ref<Option[]>([]);
const loading = ref(false);
const innerValue = ref(props.modelValue);

// keep innerValue and parent v-model synced
watch(
  () => props.modelValue,
  (v) => {
    innerValue.value = v;
  }
);

watch(innerValue, (v) => {
  emit("update:modelValue", v);
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
  } catch (e) {
    console.error("RemoteSelect fetch error:", e);
  } finally {
    loading.value = false;
  }
};

onMounted(loadOptions);
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
