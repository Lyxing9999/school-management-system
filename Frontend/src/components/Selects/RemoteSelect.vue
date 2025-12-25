<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { ElSelect, ElOption } from "element-plus";

type AnyObj = Record<string, any>;

type Option = {
  label: string;
  value: any;
  raw?: AnyObj;
  __preloaded?: boolean;
};

const props = defineProps<{
  modelValue: any;
  fetcher: () => Promise<any[]>;
  labelKey?: string; // default "label"
  valueKey?: string; // default "value"
  placeholder?: string;
  disabled?: boolean;
  clearable?: boolean;
  multiple?: boolean;

  preloadedOptions?: any[];

  /**
   * If true:
   * - preloaded options are NOT shown in dropdown when they are currently selected
   * - if user removes a selected preloaded item, it becomes visible again (so user can re-select)
   */
  hidePreloadedInDropdown?: boolean;

  reloadKey?: string | number | boolean | null;

  /** Optional text for empty dropdown */
  emptyLabel?: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: any): void;
}>();

const loading = ref(false);
const mergedOptions = ref<Option[]>([]);

/**
 * IMPORTANT: start EMPTY so ElSelect won't display raw IDs before options exist.
 */
const innerValue = ref<any>(props.multiple ? [] : null);

/**
 * If modelValue changes before options are loaded,
 * store it and apply after loadOptions() finishes.
 */
const pendingModelValue = ref<any>(undefined);

const labelKey = computed(() => props.labelKey ?? "label");
const valueKey = computed(() => props.valueKey ?? "value");

function normalize(items: any[], markPreloaded = false): Option[] {
  return (items ?? []).map((item: AnyObj) => ({
    label: item?.[labelKey.value],
    value: item?.[valueKey.value],
    raw: item,
    __preloaded: markPreloaded,
  }));
}

function uniqByValue(items: Option[]): Option[] {
  const seen = new Set<string>();
  const out: Option[] = [];
  for (const o of items) {
    const id = String(o.value);
    if (!id || seen.has(id)) continue;
    seen.add(id);
    out.push({ ...o, value: id });
  }
  return out;
}

const selectedSet = computed(() => {
  const v = innerValue.value;
  if (v === null || v === undefined) return new Set<string>();
  if (Array.isArray(v)) return new Set(v.map((x) => String(x)));
  return new Set([String(v)]);
});

function shouldHide(opt: Option): boolean {
  if (!props.hidePreloadedInDropdown) return false;
  if (!opt.__preloaded) return false;

  // Hide preloaded ONLY when it is currently selected.
  // If user removes it, it becomes visible again.
  return selectedSet.value.has(String(opt.value));
}

const visibleCount = computed(() => {
  return mergedOptions.value.reduce(
    (acc, opt) => acc + (shouldHide(opt) ? 0 : 1),
    0
  );
});

function applyModelValue(v: any) {
  if (v === null || v === undefined) {
    innerValue.value = props.multiple ? [] : null;
    return;
  }
  innerValue.value = v;
}

async function loadOptions() {
  loading.value = true;
  try {
    const pre = normalize(props.preloadedOptions ?? [], true);
    const fetchedRaw = await props.fetcher();
    const fetched = normalize(fetchedRaw ?? [], false);

    mergedOptions.value = uniqByValue([...pre, ...fetched]);

    // Apply pending modelValue if we got one while loading.
    if (pendingModelValue.value !== undefined) {
      applyModelValue(pendingModelValue.value);
      pendingModelValue.value = undefined;
    } else {
      applyModelValue(props.modelValue);
    }
  } catch (e) {
    mergedOptions.value = uniqByValue(
      normalize(props.preloadedOptions ?? [], true)
    );

    if (pendingModelValue.value !== undefined) {
      applyModelValue(pendingModelValue.value);
      pendingModelValue.value = undefined;
    } else {
      applyModelValue(props.modelValue);
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadOptions);

/**
 * If parent changes modelValue:
 * - if options are ready -> apply immediately
 * - if still loading / no options -> store as pending to avoid ID flash
 */
watch(
  () => props.modelValue,
  (v) => {
    if (loading.value || mergedOptions.value.length === 0) {
      pendingModelValue.value = v;
      return;
    }
    applyModelValue(v);
  }
);

watch(
  () => [props.reloadKey, props.preloadedOptions],
  () => loadOptions(),
  { deep: true }
);

// Emit changes up
watch(
  () => innerValue.value,
  (val) => emit("update:modelValue", val)
);

const emptyLabel = computed(() => props.emptyLabel ?? "No data");
</script>

<template>
  <div class="relative" v-loading="loading">
    <ElSelect
      v-model="innerValue"
      :loading="loading"
      :placeholder="placeholder"
      :disabled="disabled"
      :clearable="clearable"
      :multiple="multiple"
      filterable
    >
      <!-- If everything is hidden and nothing eligible came back, show a disabled “No data” -->
      <ElOption
        v-if="visibleCount === 0"
        key="__empty__"
        value="__empty__"
        :label="emptyLabel"
        disabled
      />

      <!-- Keep all options mounted so ElSelect can resolve labels for selected values -->
      <ElOption
        v-for="opt in mergedOptions"
        :key="String(opt.value)"
        :label="opt.label"
        :value="opt.value"
        v-show="!shouldHide(opt)"
      />
    </ElSelect>
  </div>
</template>
