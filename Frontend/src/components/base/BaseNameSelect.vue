<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { debounce } from "lodash-es";

interface Option {
  label: string;
  value: string;
}

const props = defineProps<{
  modelValue?: string[]; // array of selected IDs
  fetchFn: (search?: string, role?: string) => Promise<Option[]>;
  role?: string;
  placeholder?: string;
  multiple?: boolean;
  collapseTags?: boolean;
}>();

const emit = defineEmits(["update:modelValue"]);

const options = ref<Option[]>([]);
const loading = ref(false);

// Fetch options
async function fetchOptions(search = "") {
  loading.value = true;
  try {
    const data = await props.fetchFn(search, props.role);
    options.value = [...(data || [])];
  } finally {
    loading.value = false;
  }
}

// Debounced search
const debouncedSearch = debounce((query: string) => fetchOptions(query), 300);

function handleSearch(query: string) {
  loading.value = true;
  debouncedSearch(query);
}

// Handle select from dropdown
function handleSelect(option: Option) {
  if (!props.modelValue) return;
  // For multi-select, add only if not already selected
  if (props.multiple) {
    const newValue = [...props.modelValue];
    if (!newValue.includes(option.value)) {
      newValue.push(option.value);
    }
    emit("update:modelValue", newValue);
  } else {
    emit("update:modelValue", [option.value]);
  }
}

// Watch for modelValue and auto-fill options for display
watch(
  () => props.modelValue,
  async (newVal) => {
    if (!newVal || newVal.length === 0) return;
    const loadedOptions = await props.fetchFn(); // fetch all teachers
    const selectedOptions = loadedOptions.filter((o) =>
      newVal.includes(o.value)
    );
    options.value = selectedOptions.concat(
      loadedOptions.filter((o) => !newVal.includes(o.value))
    );
  },
  { immediate: true }
);

onMounted(() => fetchOptions());
</script>

<template>
  <el-select
    v-model="props.modelValue"
    :multiple="props.multiple"
    filterable
    remote
    clearable
    :collapse-tags="props.collapseTags"
    :placeholder="props.placeholder || 'Select options'"
    :remote-method="handleSearch"
    :loading="loading"
    @change="(val) => emit('update:modelValue', val)"
    @select="handleSelect"
    class="w-full"
  >
    <el-option
      v-for="option in options"
      :key="option.value"
      :label="option.label"
      :value="option.value"
    />
  </el-select>
</template>
