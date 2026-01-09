<script setup lang="ts">
import { computed, watch, onBeforeUnmount } from "vue";

type Model = string | number | null;
type Size = "default" | "small" | "large";

const props = withDefaults(
  defineProps<{
    modelValue: Model;
    placeholder?: string;
    clearable?: boolean;
    size?: Size;
    prefixIcon?: string;
    suffixIcon?: string;

    /** Fire search after user stops typing (debounced) */
    autoSearch?: boolean;
    /** Debounce delay in ms */
    debounce?: number;
    /** Trim strings for search/emit */
    trim?: boolean;

    /**
     * Optional guard:
     * - if true, autoSearch will NOT fire when value is empty string
     * - still fires on Enter if you want
     */
    ignoreEmpty?: boolean;
  }>(),
  {
    placeholder: "Search…",
    clearable: true,
    size: "default",
    autoSearch: true,
    debounce: 350,
    trim: true,
    ignoreEmpty: false,
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", v: Model): void;
  (e: "search", v: Model): void;
  (e: "clear"): void;
}>();

const model = computed<Model>({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

function normalize(v: Model): Model {
  if (typeof v === "string") {
    const s = props.trim ? v.trim() : v;
    return s;
  }
  return v;
}

function shouldAutoSearch(v: Model) {
  if (!props.autoSearch) return false;
  const nv = normalize(v);
  if (props.ignoreEmpty && (nv === "" || nv === null)) return false;
  return true;
}

function searchNow() {
  emit("search", normalize(model.value));
}

function clear() {
  emit("update:modelValue", null);
  emit("clear");
  // optional: reload unfiltered data
  emit("search", null);
}

/** Debounce timer (fires ONLY after user stops typing) */
let timer: number | null = null;

watch(
  () => props.modelValue,
  (v) => {
    if (!shouldAutoSearch(v)) return;

    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => {
      emit("search", normalize(v));
      timer = null;
    }, props.debounce);
  }
);

onBeforeUnmount(() => {
  if (timer) window.clearTimeout(timer);
});
</script>

<template>
  <el-input
    v-model="model"
    class="base-search"
    :placeholder="props.placeholder"
    :clearable="props.clearable"
    :prefix-icon="props.prefixIcon"
    :suffix-icon="props.suffixIcon"
    :size="props.size"
    @keyup.enter="searchNow"
    @clear="clear"
  >
    <template v-if="$slots.suffix" #suffix>
      <slot
        name="suffix"
        :value="model"
        :set="(v: Model) => (model = v)"
        :search="searchNow"
        :clear="clear"
      />
    </template>
  </el-input>
</template>

<style scoped>
.base-search {
  width: 100%;
  min-width: 0;
}
</style>
