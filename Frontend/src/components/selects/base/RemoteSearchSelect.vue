<script setup lang="ts">
import {
  ref,
  computed,
  watch,
  onMounted,
  nextTick,
  onBeforeUnmount,
} from "vue";
import { ElSelect, ElOption } from "element-plus";

type AnyObj = Record<string, any>;

export type RemoteResult<T = AnyObj> = {
  items: T[];
  nextCursor?: string | null;
};

type Option = {
  label: string;
  value: string;
  raw?: AnyObj;
  __preloaded?: boolean;
};

const props = defineProps<{
  modelValue: any;

  /**
   * fetcher(q, cursor, signal) must return either:
   *  - { items: [...], nextCursor?: string|null }
   *  - OR a plain array of items (treated as {items, nextCursor:null})
   */
  fetcher: (
    q: string,
    cursor?: string | null,
    signal?: AbortSignal
  ) => Promise<RemoteResult | AnyObj[]>;

  labelKey?: string; // default "label"
  valueKey?: string; // default "value"
  placeholder?: string;
  disabled?: boolean;
  clearable?: boolean;
  multiple?: boolean;

  preloadedOptions?: AnyObj[];

  /** If true => preloaded options NEVER show in dropdown (still mounted for label resolution). */
  hidePreloadedInDropdown?: boolean;

  reloadKey?: string | number | boolean | null;

  /** Search behavior */
  minQueryLength?: number; // default 2
  debounceMs?: number; // default 600

  /** Default dropdown list (when opening with empty query) */
  defaultLimit?: number; // default 20 (backend uses q="" + limit)
  showDefaultOnOpen?: boolean; // default true

  /** Prevent keyboard Backspace/Delete from removing selected tags */
  preventKeyboardRemove?: boolean; // default true

  /** UI labels */
  emptyLabel?: string; // default "Type to search"
  noResultsLabel?: string; // default "No results"
  searchingLabel?: string; // default "Searching..."
  loadingLabel?: string; // default "Loading..."
  loadMoreLabel?: string; // default "Load more"
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: any): void;
}>();

const selectRef = ref<any>(null);

const loading = ref(false);
const debouncing = ref(false);
const isInitialized = ref(false);

const mergedOptions = ref<Option[]>([]);
const query = ref("");
const nextCursor = ref<string | null>(null);

const innerValue = ref<any>(props.multiple ? [] : null);
const pendingModelValue = ref<any>(undefined);

const labelKey = computed(() => props.labelKey ?? "label");
const valueKey = computed(() => props.valueKey ?? "value");

const minLen = computed(() => props.minQueryLength ?? 2);
const debounceMs = computed(() => props.debounceMs ?? 600);

const defaultLimit = computed(() =>
  Math.max(0, Math.min(props.defaultLimit ?? 20, 50))
);
const showDefaultOnOpen = computed(() => props.showDefaultOnOpen ?? true);
const preventKeyboardRemove = computed(
  () => props.preventKeyboardRemove ?? true
);

const emptyLabel = computed(() => props.emptyLabel ?? "Type to search");
const noResultsLabel = computed(() => props.noResultsLabel ?? "No results");
const searchingLabel = computed(() => props.searchingLabel ?? "Searching...");
const loadingLabel = computed(() => props.loadingLabel ?? "Loading...");
const loadMoreLabel = computed(() => props.loadMoreLabel ?? "Load more");

function normalize(items: AnyObj[], markPreloaded = false): Option[] {
  return (items ?? []).map((item) => ({
    label: String(item?.[labelKey.value] ?? ""),
    value: String(item?.[valueKey.value] ?? ""),
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

function applyModelValue(v: any) {
  if (v === null || v === undefined) {
    innerValue.value = props.multiple ? [] : null;
    return;
  }
  innerValue.value = v;
}

/**
 * Requirement:
 * preloadedOptions (students already in class) must NEVER show in dropdown
 */
function shouldHide(opt: Option): boolean {
  if (!props.hidePreloadedInDropdown) return false;
  return !!opt.__preloaded;
}

const visibleCount = computed(() => {
  return mergedOptions.value.reduce(
    (acc, opt) => acc + (shouldHide(opt) ? 0 : 1),
    0
  );
});

const showEmptyState = computed(() => {
  if (loading.value) return false;
  if (debouncing.value) return false;
  if (!isInitialized.value) return false;
  return visibleCount.value === 0;
});

/**
 * Status label logic:
 * - < minLen => "Type at least X characters..."
 * - >= minLen & no results => "No results"
 * - empty query => emptyLabel
 */
const emptyStateLabel = computed(() => {
  const keyword = (query.value || "").trim();

  if (keyword.length > 0 && keyword.length < minLen.value) {
    return `Type at least ${minLen.value} characters to search`;
  }
  if (keyword.length >= minLen.value) {
    return noResultsLabel.value;
  }
  return emptyLabel.value;
});

/** Keep only preloaded options mounted (so selected labels resolve) */
function buildPreloadedOnly() {
  const pre = normalize(props.preloadedOptions ?? [], true);
  mergedOptions.value = uniqByValue(pre);
}

function parseFetcherResult(res: RemoteResult | AnyObj[]) {
  if (Array.isArray(res))
    return { items: res, nextCursor: null as string | null };
  return { items: res.items ?? [], nextCursor: res.nextCursor ?? null };
}

/** trailing debounce + abort + stale guard */
let debounceTimer: any = null;
let ctrl: AbortController | null = null;
let seq = 0;

function cleanupTimers() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = null;
  debouncing.value = false;
}

async function runFetch(
  keyword: string,
  cursor: string | null,
  append: boolean
) {
  const mySeq = ++seq;

  ctrl?.abort();
  ctrl = new AbortController();

  try {
    const res = await props.fetcher(keyword, cursor, ctrl.signal);
    if (mySeq !== seq) return;

    const parsed = parseFetcherResult(res);
    nextCursor.value = parsed.nextCursor ?? null;

    const pre = normalize(props.preloadedOptions ?? [], true);
    const fetched = normalize(parsed.items ?? [], false);

    mergedOptions.value = append
      ? uniqByValue([...mergedOptions.value, ...fetched])
      : uniqByValue([...pre, ...fetched]);

    isInitialized.value = true;

    if (pendingModelValue.value !== undefined) {
      applyModelValue(pendingModelValue.value);
      pendingModelValue.value = undefined;
    }
  } catch (e: any) {
    if (e?.name === "AbortError" || e?.code === "ERR_CANCELED") return;
    if (mySeq !== seq) return;

    nextCursor.value = null;
    buildPreloadedOnly();
    isInitialized.value = true;
  } finally {
    if (mySeq === seq) loading.value = false;
  }
}

async function loadDefault() {
  if (!showDefaultOnOpen.value) return;
  if (defaultLimit.value <= 0) return;

  // backend uses q="" + limit (you pass limit inside fetcher)
  nextCursor.value = null;
  await runFetch("", null, false);
}

function resetToEmptyState() {
  nextCursor.value = null;
  buildPreloadedOnly(); // visibleCount becomes 0 because preloaded hidden
  isInitialized.value = true;
  loading.value = false;
  cleanupTimers();
}

/** Element Plus remote-method */
function onRemoteSearch(q: string) {
  query.value = q;

  // stop spinner while typing
  loading.value = false;

  cleanupTimers();
  ctrl?.abort();
  ctrl = null;
  seq++;

  const keyword = (q || "").trim();

  // empty query:
  // - keep default behavior: load default list
  if (keyword.length === 0) {
    if (showDefaultOnOpen.value && defaultLimit.value > 0) {
      loading.value = true;
      runFetch("", null, false);
    } else {
      resetToEmptyState();
    }
    return;
  }

  // below min length => show empty message (not stale results)
  if (keyword.length < minLen.value) {
    resetToEmptyState();
    return;
  }

  // real search (debounced)
  debouncing.value = true;
  debounceTimer = setTimeout(() => {
    debouncing.value = false;
    nextCursor.value = null;
    loading.value = true;
    runFetch(keyword, null, false);
  }, debounceMs.value);
}

async function loadMore() {
  if (!nextCursor.value) return;

  const keyword = (query.value || "").trim();
  if (keyword.length < minLen.value) return;

  loading.value = true;
  await runFetch(keyword, nextCursor.value, true);
}

/** When dropdown opens: load default list smoothly */
async function onVisibleChange(visible: boolean) {
  if (!visible) return;

  const keyword = (query.value || "").trim();
  if (keyword.length === 0 || keyword.length < minLen.value) {
    loading.value = true;
    await loadDefault();
  }
}

/** Prevent Backspace/Delete from removing selected tag when input is empty. */
let removeKeyHandlerCleanup: null | (() => void) = null;

function bindPreventKeyboardRemove() {
  if (!preventKeyboardRemove.value) return;

  nextTick(() => {
    const root: HTMLElement | null = selectRef.value?.$el ?? null;
    if (!root) return;

    const input = root.querySelector("input") as HTMLInputElement | null;
    if (!input) return;

    const handler = (e: KeyboardEvent) => {
      if (!props.multiple) return;
      if (e.key !== "Backspace" && e.key !== "Delete") return;
      if ((input.value ?? "").length === 0) {
        e.preventDefault();
        e.stopPropagation();
      }
    };

    input.addEventListener("keydown", handler);
    removeKeyHandlerCleanup = () =>
      input.removeEventListener("keydown", handler);
  });
}

onMounted(() => {
  buildPreloadedOnly();
  applyModelValue(props.modelValue);
  bindPreventKeyboardRemove();
});

onBeforeUnmount(() => {
  cleanupTimers();
  ctrl?.abort();
  removeKeyHandlerCleanup?.();
});

/** Parent modelValue updates */
watch(
  () => props.modelValue,
  (v) => {
    if (loading.value && mergedOptions.value.length === 0) {
      pendingModelValue.value = v;
      return;
    }
    applyModelValue(v);
  }
);

/** Reset when reloadKey or preloadedOptions change */
watch(
  () => [props.reloadKey, props.preloadedOptions],
  () => {
    query.value = "";
    nextCursor.value = null;

    cleanupTimers();
    ctrl?.abort();
    ctrl = null;
    seq++;

    isInitialized.value = false;
    buildPreloadedOnly();

    if (pendingModelValue.value !== undefined) {
      applyModelValue(pendingModelValue.value);
      pendingModelValue.value = undefined;
    } else {
      applyModelValue(props.modelValue);
    }
  },
  { deep: true }
);

/** Emit changes up */
watch(
  () => innerValue.value,
  (val) => emit("update:modelValue", val)
);
</script>

<template>
  <div class="relative" v-loading="loading">
    <ElSelect
      ref="selectRef"
      v-model="innerValue"
      :loading="loading"
      :placeholder="placeholder"
      :disabled="disabled"
      :clearable="clearable"
      :multiple="multiple"
      filterable
      remote
      reserve-keyword
      :remote-method="onRemoteSearch"
      @visible-change="onVisibleChange"
    >
      <!-- One status row: Loading / Searching / Empty -->
      <ElOption
        v-if="loading || debouncing || showEmptyState"
        key="__status__"
        value="__status__"
        :label="
          loading ? loadingLabel : debouncing ? searchingLabel : emptyStateLabel
        "
        disabled
      />

      <ElOption
        v-for="opt in mergedOptions"
        :key="String(opt.value)"
        :label="opt.label"
        :value="opt.value"
        v-show="!shouldHide(opt)"
      />

      <ElOption
        v-if="nextCursor && !loading && !debouncing"
        key="__load_more__"
        value="__load_more__"
        :label="loadMoreLabel"
        @click.stop.prevent="loadMore"
      />
    </ElSelect>
  </div>
</template>
