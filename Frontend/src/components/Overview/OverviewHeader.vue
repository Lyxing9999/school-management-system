<script setup lang="ts">
import { computed } from "vue";
import BaseInputSearch from "~/components/Base/BaseInputSearch.vue";

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },

  // Search
  showSearch: { type: Boolean, default: false },
  searchModelValue: { type: String, default: "" },
  searchPlaceholder: { type: String, default: "Search..." },
  searchDisabled: { type: Boolean, default: false },

  // Reset
  showReset: { type: Boolean, default: false },
  resetLabel: { type: String, default: "Reset" },
  resetDisabled: { type: Boolean, default: false },

  // Refresh
  showRefresh: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  refreshLabel: { type: String, default: "Refresh" },

  stats: {
    type: Array as () => Array<{
      key?: string | number;
      value: number;
      singular?: string;
      plural?: string;
      label?: string;
      suffix?: string;
      prefix?: string;
      variant?: "primary" | "secondary";
      dotClass?: string;
    }>,
    default: () => [],
  },
});

const emit = defineEmits<{
  (e: "refresh"): void;
  (e: "update:searchModelValue", value: string): void;
  (e: "reset"): void;
}>();

const searchValue = computed({
  get: () => props.searchModelValue,
  set: (v: string) => emit("update:searchModelValue", v),
});

function onReset() {
  emit("update:searchModelValue", "");
  emit("reset");
}

function pluralize(stat: {
  value: number;
  singular?: string;
  plural?: string;
  label?: string;
}) {
  if (stat.label) return stat.label;
  if (!stat.singular) return "";
  if (stat.value === 1) return stat.singular;
  return stat.plural ?? `${stat.singular}s`;
}
</script>

<template>
  <div
    class="mb-4 bg-gradient-to-r from-[var(--color-primary-light-9)] to-[var(--color-primary-light-9)] border border-[color:var(--color-primary-light-9)] shadow-sm rounded-2xl p-5"
  >
    <!-- Row 1: Title/Description + Actions -->
    <el-row :gutter="16" align="top" class="overview-top">
      <el-col :xs="24" :sm="16" :md="18">
        <h1
          class="text-2xl font-bold flex items-center gap-2 text-[color:var(--color-dark)]"
        >
          {{ title }}
          <slot name="icon" />
        </h1>

        <p
          v-if="description"
          class="text-sm text-[color:var(--color-primary-light-1)] mt-1"
        >
          {{ description }}
        </p>
      </el-col>

      <el-col :xs="24" :sm="8" :md="6">
        <div class="flex gap-2 justify-start sm:justify-end mt-3 sm:mt-0">
          <slot name="actions">
            <BaseButton
              v-if="showReset"
              plain
              class="w-full sm:w-auto reset-btn"
              :disabled="disabled || resetDisabled"
              @click="onReset"
            >
              {{ resetLabel }}
            </BaseButton>
          </slot>
        </div>
      </el-col>
    </el-row>

    <!-- Divider + Row 2: Controls -->
    <div
      v-if="showSearch || showReset || $slots.filters"
      class="mt-4 pt-4 border-t border-[color:var(--color-primary-light-8)]"
    >
      <!-- Search + Reset in a grid that wraps nicely -->
      <el-row v-if="showSearch || showReset" :gutter="12" align="middle">
        <el-col :xs="24" :sm="16" :md="12">
          <BaseInputSearch
            v-if="showSearch"
            v-model="searchValue"
            :placeholder="searchPlaceholder"
            clearable
            :disabled="disabled || searchDisabled"
            class="w-full"
          />
        </el-col>

        <el-col :xs="24" :sm="8" :md="4">
          <BaseButton
            v-if="showReset"
            plain
            class="w-full sm:w-auto reset-btn reset-btn--danger"
            :disabled="disabled || resetDisabled"
            @click="onReset"
          >
            {{ resetLabel }}
          </BaseButton>
        </el-col>
      </el-row>

      <!-- Filters slot (you can use el-row inside the slot too) -->
      <div v-if="$slots.filters" class="mt-3">
        <slot name="filters" />
      </div>
    </div>

    <!-- Row 3: Stats -->
    <div v-if="stats?.length" class="mt-4">
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <template v-for="stat in stats" :key="stat.key ?? stat.label">
          <span
            v-if="stat.variant === 'primary'"
            class="inline-flex items-center gap-1 rounded-full bg-[var(--color-primary-light-8)] text-[color:var(--color-primary)] px-3 py-0.5 border border-[var(--color-primary-light-5)]"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />
            {{ stat.value }} {{ pluralize(stat) }}
          </span>

          <span
            v-else
            class="inline-flex items-center gap-1 rounded-full bg-white text-gray-700 px-3 py-0.5 border border-gray-200"
          >
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="stat.dotClass ?? 'bg-emerald-500'"
            />
            <span v-if="stat.prefix">{{ stat.prefix }}</span>
            <span>{{ stat.value }} {{ pluralize(stat) }}</span>
            <span v-if="stat.suffix">{{ stat.suffix }}</span>
          </span>
        </template>
      </div>

      <div v-if="$slots['custom-stats']" class="mt-2">
        <slot name="custom-stats" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.overview-top :deep(.el-col) {
  /* prevents odd spacing in some Element Plus grid cases */
  min-width: 0;
}
.reset-btn {
  border-radius: 10px;
  font-weight: 650;

  border: 1px solid
    color-mix(in srgb, var(--border-color) 70%, var(--color-primary) 30%) !important;
  color: color-mix(
    in srgb,
    var(--text-color) 78%,
    var(--muted-color) 22%
  ) !important;
  background: color-mix(
    in srgb,
    var(--color-card) 92%,
    var(--color-bg) 8%
  ) !important;

  transition: background-color var(--transition-base),
    border-color var(--transition-base), color var(--transition-base),
    transform var(--transition-base);
}

.reset-btn:hover:not(.is-disabled):not([disabled]) {
  background: var(--hover-bg) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 55%,
    var(--color-primary) 45%
  ) !important;
  color: var(--text-color) !important;
  transform: translateY(-0.5px);
}

.reset-btn:active:not(.is-disabled):not([disabled]) {
  transform: translateY(0);
}

/* ✅ Disabled: make it look intentionally disabled (not “normal”) */
.reset-btn.is-disabled,
.reset-btn[disabled],
.reset-btn:disabled {
  background: color-mix(
    in srgb,
    var(--color-card) 75%,
    var(--color-bg) 25%
  ) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 92%,
    transparent
  ) !important;
  color: color-mix(in srgb, var(--muted-color) 85%, transparent) !important;

  opacity: 1 !important; /* avoid Element Plus “washed” opacity */
  cursor: not-allowed !important;
  transform: none !important;
}

/* Dark mode: keep disabled darker (avoid looking like enabled) */
html[data-theme="dark"] .reset-btn {
  background: color-mix(
    in srgb,
    var(--color-card) 88%,
    var(--color-bg) 12%
  ) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 78%,
    var(--color-primary) 22%
  ) !important;
}

html[data-theme="dark"] .reset-btn.is-disabled,
html[data-theme="dark"] .reset-btn[disabled],
html[data-theme="dark"] .reset-btn:disabled {
  background: color-mix(
    in srgb,
    var(--color-card) 92%,
    var(--color-bg) 8%
  ) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 92%,
    transparent
  ) !important;
  color: color-mix(in srgb, var(--muted-color) 82%, transparent) !important;
}
</style>
