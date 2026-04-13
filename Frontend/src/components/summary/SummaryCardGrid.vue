<script setup lang="ts">
import { computed } from "vue";

type SummaryItem = {
  key?: string | number;
  label: string;
  value: string | number;
  helper?: string;
  tone?: "default" | "primary" | "success" | "warning" | "danger";
};

const props = withDefaults(
  defineProps<{
    items: SummaryItem[];
    columns?: 2 | 3 | 4 | 5 | 6;
    compact?: boolean;
    elevated?: boolean;
  }>(),
  {
    columns: 4,
    compact: false,
    elevated: false,
  },
);

const gridClass = computed(() => `summary-grid--cols-${props.columns}`);
</script>

<template>
  <section
    class="summary-grid"
    :class="[
      gridClass,
      {
        'summary-grid--compact': compact,
        'summary-grid--elevated': elevated,
      },
    ]"
  >
    <article
      v-for="(item, index) in items"
      :key="item.key ?? item.label ?? index"
      class="summary-card"
      :class="`summary-card--${item.tone || 'default'}`"
    >
      <span class="summary-card__label">{{ item.label }}</span>
      <strong class="summary-card__value">{{ item.value }}</strong>
      <small v-if="item.helper" class="summary-card__helper">
        {{ item.helper }}
      </small>
    </article>
  </section>
</template>

<style scoped>
.summary-grid {
  display: grid;
  gap: 12px;
}

.summary-grid--cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.summary-grid--cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.summary-grid--cols-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.summary-grid--cols-5 {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.summary-grid--cols-6 {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.summary-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid var(--border-color, var(--el-border-color-light));
  background: var(--color-card, var(--el-bg-color-overlay));
  color: var(--text-color, var(--el-text-color-primary));
  overflow: hidden;

  transition: border-color var(--transition-base, 0.2s ease),
    background-color var(--transition-base, 0.2s ease),
    box-shadow var(--transition-base, 0.2s ease),
    transform var(--transition-base, 0.2s ease);
}

.summary-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: transparent;
  border-radius: 14px 0 0 14px;
}

.summary-card:hover {
  transform: translateY(-1px);
  background: color-mix(
    in srgb,
    var(--color-card, var(--el-bg-color-overlay)) 92%,
    var(--hover-bg, var(--color-bg, #f5f7fa)) 8%
  );
}

.summary-grid--compact .summary-card {
  padding: 12px;
  gap: 4px;
}

.summary-grid--elevated .summary-card {
  box-shadow: 0 8px 20px
    color-mix(
      in srgb,
      var(--card-shadow, rgba(17, 24, 39, 0.08)) 75%,
      transparent
    );
}

.summary-card__label {
  font-size: 12px;
  line-height: 1.4;
  color: var(--muted-color, var(--el-text-color-secondary));
}

.summary-card__value {
  font-size: 24px;
  line-height: 1.1;
  font-weight: 750;
  color: var(--text-color, var(--el-text-color-primary));
  word-break: break-word;
}

.summary-card__helper {
  font-size: 12px;
  line-height: 1.4;
  color: var(--muted-color, var(--el-text-color-secondary));
  word-break: break-word;
}

/* default */
.summary-card--default {
  border-color: var(--border-color, var(--el-border-color-light));
  background: var(--color-card, var(--el-bg-color-overlay));
}

.summary-card--default::before {
  background: color-mix(
    in srgb,
    var(--border-color, var(--el-border-color-light)) 70%,
    transparent
  );
}

/* primary */
.summary-card--primary {
  border-color: color-mix(
    in srgb,
    var(--color-primary, var(--el-color-primary)) 18%,
    var(--border-color, var(--el-border-color-light)) 82%
  );
  background: color-mix(
    in srgb,
    var(--color-card, var(--el-bg-color-overlay)) 94%,
    var(--color-primary-light-8, var(--el-color-primary-light-9)) 6%
  );
}

.summary-card--primary::before {
  background: var(--color-primary, var(--el-color-primary));
}

/* success */
.summary-card--success {
  border-color: var(--status-success-border, var(--border-color));
  background: color-mix(
    in srgb,
    var(--color-card, var(--el-bg-color-overlay)) 94%,
    var(--status-success-bg, rgba(34, 197, 94, 0.08)) 6%
  );
}

.summary-card--success::before {
  background: var(--status-success, #22c55e);
}

/* warning */
.summary-card--warning {
  border-color: var(--status-warning-border, var(--border-color));
  background: color-mix(
    in srgb,
    var(--color-card, var(--el-bg-color-overlay)) 94%,
    var(--status-warning-bg, rgba(245, 158, 11, 0.08)) 6%
  );
}

.summary-card--warning::before {
  background: var(--status-warning, #f59e0b);
}

/* danger */
.summary-card--danger {
  border-color: var(--status-danger-border, var(--border-color));
  background: color-mix(
    in srgb,
    var(--color-card, var(--el-bg-color-overlay)) 94%,
    var(--status-danger-bg, rgba(239, 68, 68, 0.08)) 6%
  );
}

.summary-card--danger::before {
  background: var(--status-danger, #ef4444);
}

@media (max-width: 1180px) {
  .summary-grid--cols-6,
  .summary-grid--cols-5,
  .summary-grid--cols-4 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .summary-grid--cols-6,
  .summary-grid--cols-5,
  .summary-grid--cols-4,
  .summary-grid--cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .summary-grid--cols-6,
  .summary-grid--cols-5,
  .summary-grid--cols-4,
  .summary-grid--cols-3,
  .summary-grid--cols-2 {
    grid-template-columns: 1fr;
  }

  .summary-card__value {
    font-size: 20px;
  }
}
</style>
