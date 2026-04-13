<script setup lang="ts">
import { computed, useSlots } from "vue";

const props = withDefaults(
  defineProps<{
    stackOnMobile?: boolean;
    bordered?: boolean;
    elevated?: boolean;
    compact?: boolean;
    align?: "start" | "center";
    soft?: boolean;
    accented?: boolean;
  }>(),
  {
    stackOnMobile: true,
    bordered: true,
    elevated: false,
    compact: false,
    align: "center",
    soft: true,
    accented: true,
  },
);

const slots = useSlots();

const hasLeft = computed(() => !!slots.left);
const hasRight = computed(() => !!slots.right);
</script>

<template>
  <section
    class="page-toolbar"
    :class="{
      'page-toolbar--bordered': bordered,
      'page-toolbar--elevated': elevated,
      'page-toolbar--compact': compact,
      'page-toolbar--stack-mobile': stackOnMobile,
      'page-toolbar--only-left': hasLeft && !hasRight,
      'page-toolbar--only-right': !hasLeft && hasRight,
      'page-toolbar--align-start': align === 'start',
      'page-toolbar--soft': soft,
      'page-toolbar--accented': accented,
    }"
  >
    <div v-if="hasLeft" class="page-toolbar__left">
      <slot name="left" />
    </div>

    <div v-if="hasRight" class="page-toolbar__right">
      <slot name="right" />
    </div>
  </section>
</template>

<style scoped>
.page-toolbar {
  position: relative;
  overflow: hidden;

  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;

  background: var(--color-card, var(--el-bg-color-overlay));
  color: var(--text-color, var(--el-text-color-primary));

  transition: background-color var(--transition-base, 0.2s ease),
    border-color var(--transition-base, 0.2s ease),
    box-shadow var(--transition-base, 0.2s ease),
    transform var(--transition-base, 0.2s ease);
}

.page-toolbar--soft {
  background: color-mix(
    in srgb,
    var(--color-card, var(--el-bg-color-overlay)) 94%,
    var(--color-primary-light-9, rgba(255, 82, 161, 0.05)) 6%
  );
}

.page-toolbar--compact {
  padding: 10px 12px;
  gap: 10px;
}

.page-toolbar--bordered {
  border: 1px solid
    color-mix(
      in srgb,
      var(--border-color, var(--el-border-color-light)) 88%,
      var(--color-primary, var(--el-color-primary)) 12%
    );
}

.page-toolbar--elevated {
  box-shadow: 0 8px 20px
    color-mix(
      in srgb,
      var(--card-shadow, rgba(17, 24, 39, 0.08)) 75%,
      transparent
    );
}

.page-toolbar--accented::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 2px;
  background: var(--color-primary, var(--el-color-primary));
  opacity: 0.35;
}

.page-toolbar--only-left,
.page-toolbar--only-right {
  grid-template-columns: 1fr;
}

.page-toolbar--align-start {
  align-items: start;
}

.page-toolbar__left,
.page-toolbar__right {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.page-toolbar__left {
  justify-content: flex-start;
  flex: 1 1 420px;
}

.page-toolbar__right {
  justify-content: flex-end;
  flex: 0 1 auto;
  gap: 8px;
}

/* Search should have priority */
.page-toolbar__left :deep(.toolbar-search),
.page-toolbar__right :deep(.toolbar-search) {
  width: min(100%, 560px);
  max-width: 560px;
  flex: 1 1 520px;
  min-width: 360px;
}

/* Filters */
.page-toolbar__left :deep(.toolbar-select),
.page-toolbar__right :deep(.toolbar-select) {
  width: 180px;
  flex: 0 1 180px;
}

.page-toolbar__left :deep(.toolbar-date),
.page-toolbar__right :deep(.toolbar-date) {
  width: 180px;
  flex: 0 1 180px;
}

.page-toolbar__left :deep(.el-input),
.page-toolbar__left :deep(.el-select),
.page-toolbar__left :deep(.el-date-editor),
.page-toolbar__right :deep(.el-input),
.page-toolbar__right :deep(.el-select),
.page-toolbar__right :deep(.el-date-editor) {
  max-width: 100%;
}

.page-toolbar :deep(.el-input__wrapper),
.page-toolbar :deep(.el-select__wrapper),
.page-toolbar :deep(.el-textarea__inner) {
  background: color-mix(
    in srgb,
    var(--color-card, var(--el-bg-color-overlay)) 96%,
    var(--color-primary-light-9, rgba(255, 82, 161, 0.05)) 4%
  );
  box-shadow: inset 0 0 0 1px
    color-mix(
      in srgb,
      var(--border-color, var(--el-border-color-light)) 90%,
      var(--color-primary, var(--el-color-primary)) 10%
    );
  color: var(--text-color, var(--el-text-color-primary));
  transition: box-shadow var(--transition-base, 0.2s ease),
    background-color var(--transition-base, 0.2s ease);
}

.page-toolbar :deep(.el-input__wrapper:hover),
.page-toolbar :deep(.el-select__wrapper:hover),
.page-toolbar :deep(.el-textarea__inner:hover) {
  box-shadow: inset 0 0 0 1px
    color-mix(
      in srgb,
      var(--border-color, var(--el-border-color-light)) 72%,
      var(--color-primary, var(--el-color-primary)) 28%
    );
}

.page-toolbar :deep(.el-input__wrapper.is-focus),
.page-toolbar :deep(.el-select__wrapper.is-focused),
.page-toolbar :deep(.el-textarea__inner:focus) {
  box-shadow: inset 0 0 0 1px
      color-mix(
        in srgb,
        var(--color-primary, var(--el-color-primary)) 45%,
        transparent
      ),
    0 0 0 3px
      color-mix(
        in srgb,
        var(--color-primary, var(--el-color-primary)) 10%,
        transparent
      );
}

/* Sidebar-aware desktop breakpoint */
@media (max-width: 1360px) {
  .page-toolbar {
    grid-template-columns: 1fr;
  }

  .page-toolbar__left,
  .page-toolbar__right {
    width: 100%;
    justify-content: flex-start;
  }

  .page-toolbar__left :deep(.toolbar-search),
  .page-toolbar__right :deep(.toolbar-search) {
    width: 100%;
    max-width: 100%;
    flex: 1 1 100%;
    min-width: 0;
  }
}

/* Tablet */
@media (max-width: 900px) {
  .page-toolbar__left,
  .page-toolbar__right {
    gap: 8px;
  }

  .page-toolbar__left :deep(.toolbar-select),
  .page-toolbar__right :deep(.toolbar-select),
  .page-toolbar__left :deep(.toolbar-date),
  .page-toolbar__right :deep(.toolbar-date) {
    width: 170px;
    flex: 0 1 170px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .page-toolbar--stack-mobile {
    grid-template-columns: 1fr;
  }

  .page-toolbar--stack-mobile .page-toolbar__left,
  .page-toolbar--stack-mobile .page-toolbar__right {
    width: 100%;
    justify-content: flex-start;
  }

  .page-toolbar--stack-mobile .page-toolbar__left :deep(.toolbar-search),
  .page-toolbar--stack-mobile .page-toolbar__right :deep(.toolbar-search),
  .page-toolbar--stack-mobile .page-toolbar__left :deep(.toolbar-select),
  .page-toolbar--stack-mobile .page-toolbar__right :deep(.toolbar-select),
  .page-toolbar--stack-mobile .page-toolbar__left :deep(.toolbar-date),
  .page-toolbar--stack-mobile .page-toolbar__right :deep(.toolbar-date) {
    width: 100%;
    max-width: 100%;
    flex: 1 1 100%;
    min-width: 0;
  }

  .page-toolbar--stack-mobile .page-toolbar__left > :deep(.el-button),
  .page-toolbar--stack-mobile .page-toolbar__left > :deep(button),
  .page-toolbar--stack-mobile .page-toolbar__left > :deep(.base-button),
  .page-toolbar--stack-mobile .page-toolbar__right > :deep(.el-button),
  .page-toolbar--stack-mobile .page-toolbar__right > :deep(button),
  .page-toolbar--stack-mobile .page-toolbar__right > :deep(.base-button) {
    width: 100%;
  }
}

@media (max-width: 520px) {
  .page-toolbar {
    padding: 10px 12px;
    gap: 10px;
  }
}
</style>
