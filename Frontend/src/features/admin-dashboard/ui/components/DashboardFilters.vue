<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import type { DateRange } from "../../model/filters";

const props = defineProps<{
  dateRange: DateRange;
  loading?: boolean;
  canReset?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:dateRange", v: DateRange): void;
  (e: "apply"): void;
  (e: "reset"): void;
}>();

/** Normalize DateRange coming from Element Plus */
function normalizeDateRange(v: unknown): DateRange {
  if (!v) return null;
  if (!Array.isArray(v)) return null;
  if (v.length !== 2) return null;

  const [a, b] = v as any[];
  if (!(a instanceof Date) || !(b instanceof Date)) return null;
  return [a, b];
}

/** Auto-apply with small debounce to avoid double calls */
let t: ReturnType<typeof setTimeout> | null = null;
function scheduleApply() {
  if (t) clearTimeout(t);
  t = setTimeout(() => emit("apply"), 250);
}

onBeforeUnmount(() => {
  if (t) clearTimeout(t);
});

/** Date change handler */
function onDateRangeChange(v: unknown) {
  const normalized = normalizeDateRange(v);
  emit("update:dateRange", normalized);

  // apply immediately (but debounced)
  scheduleApply();
}

/** Reset: clear range + apply */
function onReset() {
  emit("update:dateRange", null);
  emit("reset"); // optional: if parent tracks reset intent
  scheduleApply();
}

/** Optional: apply once when popper closes (if you prefer less requests)
 *  If you want this, uncomment and remove scheduleApply() above.
 */
// function onPickerVisibleChange(visible: boolean) {
//   if (!visible) scheduleApply();
// }
</script>

<template>
  <div class="df-bar">
    <el-date-picker
      class="df-date"
      popper-class="date-range-popper"
      placement="bottom-start"
      :teleported="true"
      :model-value="props.dateRange"
      @update:model-value="onDateRangeChange"
      type="daterange"
      size="small"
      range-separator="→"
      start-placeholder="From"
      end-placeholder="To"
      format="YYYY-MM-DD"
      :disabled="props.loading"
      :clearable="true"
      :popper-options="{
        strategy: 'fixed',
        modifiers: [
          { name: 'offset', options: { offset: [0, 8] } },
          {
            name: 'preventOverflow',
            options: { padding: 12, boundary: 'viewport' },
          },
          { name: 'flip', options: { padding: 12, boundary: 'viewport' } },
          {
            name: 'computeStyles',
            options: { adaptive: false, gpuAcceleration: false },
          },
        ],
      }"
    />

    <BaseButton
      plain
      size="small"
      class="df-reset"
      :disabled="props.loading || props.canReset === false"
      @click="onReset"
    >
      Reset
    </BaseButton>
  </div>
</template>

<style scoped>
.df-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  width: 100%;
}

.df-date {
  width: 100%;
  min-width: 0;
}

/* Mobile: stack */
@media (max-width: 768px) {
  .df-bar {
    grid-template-columns: 1fr;
  }
  .df-reset {
    width: 100%;
    justify-content: center;
  }
}
</style>
