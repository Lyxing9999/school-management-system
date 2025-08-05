<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  type?:
    | "text"
    | "default"
    | "primary"
    | "success"
    | "warning"
    | "info"
    | "danger";
  size?: "default" | "small" | "large";
  disabled?: boolean;
  loading?: boolean;
  icon?: string;
  plain?: boolean;
  round?: boolean;
  circle?: boolean;
  text?: boolean;
  link?: boolean;
  href?: string;
  target?: string;
  rel?: string;
  customClass?: string;
  classes?: string;
  style?: string;
}>();

// Define emits for better TypeScript support
const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const classes = computed(() =>
  [props.classes, props.customClass].filter(Boolean).join(" ")
);

// Handle click with proper event emission
const handleClick = (event: MouseEvent) => {
  emit("click", event);
};
</script>

<template>
  <el-button
    v-bind="$attrs"
    :type="props.type"
    :size="props.size"
    :disabled="props.disabled"
    :loading="props.loading"
    :icon="props.icon"
    :plain="props.plain"
    :round="props.round"
    :circle="props.circle"
    :text="props.text"
    :link="props.link"
    :href="props.href"
    :class="classes"
    :target="props.target"
    :rel="props.rel"
    :style="props.style"
    @click="handleClick"
  >
    <slot />
  </el-button>
</template>

<style scoped>
.el-button {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
  transition: all 0.3s ease;
}

.el-button:hover {
  color: var(--el-color-primary-dark-2);
  background-color: var(--el-color-primary-light-8);
  border-color: var(--el-color-primary-light-6);
}

.el-button:active {
  color: var(--el-color-primary-dark-2);
  background-color: var(--el-color-primary-light-7);
  border-color: var(--el-color-primary-light-5);
}

.el-button:focus {
  color: var(--el-color-primary-dark-2);
  background-color: var(--el-color-primary-light-8);
  border-color: var(--el-color-primary-light-6);
  outline: 2px solid var(--el-color-primary-light-5);
  outline-offset: 2px;
}

.el-button.is-disabled,
.el-button:disabled {
  color: var(--el-color-primary-light-5);
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Danger button variants */
.el-button--danger {
  color: var(--el-color-danger);
  background-color: var(--el-color-danger-light-9);
  border-color: var(--el-color-danger-light-7);
}

.el-button--danger:hover {
  color: var(--el-color-danger-dark-2);
  background-color: var(--el-color-danger-light-8);
  border-color: var(--el-color-danger-light-6);
}

.el-button--danger:active {
  color: var(--el-color-danger-dark-2);
  background-color: var(--el-color-danger-light-7);
  border-color: var(--el-color-danger-light-5);
}

.el-button--danger:focus {
  color: var(--el-color-danger-dark-2);
  background-color: var(--el-color-danger-light-8);
  border-color: var(--el-color-danger-light-6);
  outline-color: var(--el-color-danger-light-5);
}

.el-button--danger.is-disabled,
.el-button--danger:disabled {
  color: var(--el-color-danger-light-5);
  background-color: var(--el-color-danger-light-9);
  border-color: var(--el-color-danger-light-7);
}

/* Success button variants */
.el-button--success {
  color: var(--el-color-success);
  background-color: var(--el-color-success-light-9);
  border-color: var(--el-color-success-light-7);
}

.el-button--success:hover {
  color: var(--el-color-success-dark-2);
  background-color: var(--el-color-success-light-8);
  border-color: var(--el-color-success-light-6);
}

/* Warning button variants */
.el-button--warning {
  color: var(--el-color-warning);
  background-color: var(--el-color-warning-light-9);
  border-color: var(--el-color-warning-light-7);
}

.el-button--warning:hover {
  color: var(--el-color-warning-dark-2);
  background-color: var(--el-color-warning-light-8);
  border-color: var(--el-color-warning-light-6);
}

/* Info button variants */
.el-button--info {
  color: var(--el-color-info);
  background-color: var(--el-color-info-light-9);
  border-color: var(--el-color-info-light-7);
}

.el-button--info:hover {
  color: var(--el-color-info-dark-2);
  background-color: var(--el-color-info-light-8);
  border-color: var(--el-color-info-light-6);
}
</style>
