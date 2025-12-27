<script setup lang="ts">
import type { DateRange, TermValue } from "../../model/filters";

defineProps<{
  dateRange: DateRange;
  term: TermValue;
  termOptions: Array<{ label: string; value: TermValue }>;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:dateRange", v: DateRange): void;
  (e: "update:term", v: TermValue): void;
  (e: "apply"): void;
}>();
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <el-date-picker
      :model-value="dateRange"
      @update:model-value="(v) => emit('update:dateRange', v as DateRange)"
      type="daterange"
      size="small"
      range-separator="→"
      start-placeholder="From"
      end-placeholder="To"
      format="YYYY-MM-DD"
    />

    <el-select
      :model-value="term"
      @update:model-value="(v) => emit('update:term', v as TermValue)"
      placeholder="Term"
      size="small"
      style="min-width: 140px"
    >
      <el-option
        v-for="t in termOptions"
        :key="t.value || 'all'"
        :label="t.label"
        :value="t.value"
      />
    </el-select>

    <BaseButton
      plain
      :loading="loading"
      class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
      @click="emit('apply')"
    >
      Apply filters
    </BaseButton>
  </div>
</template>
