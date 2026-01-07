<script setup lang="ts">
const props = defineProps<{
  loading?: boolean;
  disabled?: boolean;
  title?: string;
  confirmText?: string;
  cancelText?: string;
}>();

const emit = defineEmits<{
  (e: "confirm"): void;
  (e: "cancel"): void;
}>();

function onConfirm() {
  emit("confirm");
}

function onCancel() {
  emit("cancel");
}
</script>

<template>
  <div class="flex items-center">
    <el-popconfirm
      popper-class="sc-popconfirm"
      :title="title || 'Are you sure you want to save the changes?'"
      :confirm-button-text="confirmText || 'Yes'"
      :cancel-button-text="cancelText || 'No'"
      @confirm="onConfirm"
      @cancel="onCancel"
    >
      <template #reference>
        <el-button
          class="compact-btn"
          type="text"
          size="small"
          :loading="props.loading"
          aria-label="Save"
        >
          <el-icon><Edit /></el-icon>
        </el-button>
      </template>
    </el-popconfirm>

    <el-button
      class="compact-btn"
      type="text"
      size="small"
      aria-label="Cancel"
      @click="onCancel"
      :disabled="props.loading"
    >
      <el-icon><Close /></el-icon>
    </el-button>
  </div>
</template>

<style scoped>
/* compact icon buttons (token-driven, input-suffix friendly) */
/* compact icon buttons (token-driven, input-suffix friendly) */
.compact-btn {
  /* consistent hit area without looking “big” */
  width: 28px;
  height: 28px;
  padding: 0 !important;

  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;

  border-radius: 10px !important;

  /* system colors */
  background: transparent !important;
  border: 1px solid transparent !important;
  color: color-mix(
    in srgb,
    var(--text-color) 78%,
    var(--muted-color) 22%
  ) !important;

  transition: background-color var(--transition-base),
    border-color var(--transition-base), color var(--transition-base),
    transform var(--transition-base);
}

/* keep icons crisp */
.compact-btn :deep(svg) {
  width: 16px;
  height: 16px;
}

/* hover/active uses your semantic tokens */
.compact-btn:hover:not(.is-disabled):not([disabled]) {
  background: var(--hover-bg) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 70%,
    transparent
  ) !important;
  color: var(--text-color) !important;
}

.compact-btn:active:not(.is-disabled):not([disabled]) {
  background: var(--active-bg) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 70%,
    transparent
  ) !important;
}

/* save button: gently lean primary on hover (system accent) */
.compact-btn[aria-label="Save"]:hover:not(.is-disabled):not([disabled]) {
  color: var(--color-primary) !important;
  border-color: color-mix(
    in srgb,
    var(--color-primary) 40%,
    transparent
  ) !important;
}

/* cancel button: neutral (no red unless you have danger tokens) */
.compact-btn[aria-label="Cancel"]:hover:not(.is-disabled):not([disabled]) {
  color: color-mix(
    in srgb,
    var(--text-color) 88%,
    var(--muted-color) 12%
  ) !important;
}

/* keyboard focus ring */
.compact-btn:focus-visible {
  outline: 2px solid color-mix(in srgb, var(--color-primary) 65%, transparent);
  outline-offset: 2px;
}

/* disabled */
.compact-btn.is-disabled,
.compact-btn[disabled],
.compact-btn:disabled {
  opacity: 1 !important;
  cursor: not-allowed !important;
  background: transparent !important;
  border-color: transparent !important;
  color: color-mix(in srgb, var(--muted-color) 78%, transparent) !important;
}

/* optional: slightly larger tap target on touch */
@media (max-width: 768px) {
  .compact-btn {
    width: 32px;
    height: 32px;
    border-radius: 12px !important;
  }
}
</style>
