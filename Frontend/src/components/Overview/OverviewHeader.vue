<script setup lang="ts">
const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
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
  showRefresh: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  refreshLabel: { type: String, default: "Refresh" },
});

defineEmits<{
  (e: "refresh"): void;
}>();

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
    class="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-[var(--color-primary-light-9)] to-[var(--color-primary-light-9)] border border-[color:var(--color-primary-light-9)] shadow-sm rounded-2xl p-5"
  >
    <!-- Left side: title, description, filters, stats -->
    <div class="space-y-2">
      <h1
        class="text-2xl font-bold flex items-center gap-2 text-[color:var(--color-dark)]"
      >
        {{ title }}
        <slot name="icon" />
      </h1>

      <p
        v-if="description"
        class="text-sm text-[color:var(--color-primary-light-1)]"
      >
        {{ description }}
      </p>

      <!-- Page-specific filters / controls -->
      <div
        v-if="$slots.filters"
        class="mt-3 pt-3 border-t border-[color:var(--color-primary-light-8)] flex flex-col gap-2"
      >
        <slot name="filters" />
      </div>

      <!-- Optional stats section -->
      <div
        v-if="stats && stats.length"
        class="flex flex-wrap items-center gap-2 mt-2 text-xs"
      >
        <template v-for="stat in stats" :key="stat.key ?? stat.label">
          <!-- primary pill -->
          <span
            v-if="stat.variant === 'primary'"
            class="inline-flex items-center gap-1 rounded-full bg-[var(--color-primary-light-8)] text-[color:var(--color-primary)] px-3 py-0.5 border border-[var(--color-primary-light-5)]"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />
            {{ stat.value }}
            {{ pluralize(stat) }}
          </span>

          <!-- secondary pill -->
          <span
            v-else
            class="inline-flex items-center gap-1 rounded-full bg-white text-gray-700 px-3 py-0.5 border border-gray-200"
          >
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="stat.dotClass ?? 'bg-emerald-500'"
            />
            <span v-if="stat.prefix">
              {{ stat.prefix }}
            </span>
            <span>
              {{ stat.value }}
              {{ pluralize(stat) }}
            </span>
            <span v-if="stat.suffix">
              {{ stat.suffix }}
            </span>
          </span>
        </template>
      </div>

      <!-- Or completely custom stats -->
      <div v-if="$slots['custom-stats']" class="mt-1">
        <slot name="custom-stats" />
      </div>
    </div>

    <!-- Right side: actions -->
    <div class="flex items-center gap-2 justify-end">
      <slot name="actions">
        <BaseButton
          v-if="showRefresh"
          plain
          :loading="loading"
          :disabled="disabled"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="$emit('refresh')"
        >
          {{ refreshLabel }}
        </BaseButton>
      </slot>
    </div>
  </div>
</template>
