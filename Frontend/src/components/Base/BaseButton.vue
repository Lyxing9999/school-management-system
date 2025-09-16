<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    customClass?: string;
    type?:
      | "primary"
      | "success"
      | "warning"
      | "danger"
      | "info"
      | "default"
      | "text";
    color?: string;
    hoverColor?: string;
    textColor?: string;
    textHoverColor?: string;
  }>(),
  {
    type: "default",
  }
);

const emit = defineEmits<{
  click: [MouseEvent];
}>();

const typeVars: Record<
  string,
  { bg: string; hoverBg: string; text: string; hoverText: string }
> = {
  primary: {
    bg: "var(--button-primary-bg)",
    hoverBg: "var(--button-primary-hover-bg)",
    text: "var(--button-primary-text)",
    hoverText: "var(--button-primary-hover-text)",
  },
  success: {
    bg: "var(--button-success-bg)",
    hoverBg: "var(--button-success-hover-bg)",
    text: "var(--button-success-text)",
    hoverText: "var(--button-success-hover-text)",
  },
  warning: {
    bg: "var(--button-warning-bg)",
    hoverBg: "var(--button-warning-hover-bg)",
    text: "var(--button-warning-text)",
    hoverText: "var(--button-warning-hover-text)",
  },
  danger: {
    bg: "var(--button-danger-bg)",
    hoverBg: "var(--button-danger-hover-bg)",
    text: "var(--button-danger-text)",
    hoverText: "var(--button-danger-hover-text)",
  },
  info: {
    bg: "var(--button-info-bg)",
    hoverBg: "var(--button-info-hover-bg)",
    text: "var(--button-info-text)",
    hoverText: "var(--button-info-hover-text)",
  },
  default: {
    bg: "var(--button-default-bg)",
    hoverBg: "var(--button-default-hover-bg)",
    text: "var(--button-default-text)",
    hoverText: "var(--button-default-hover-text)",
  },
  text: {
    bg: "var(--button-text-bg)",
    hoverBg: "var(--button-text-hover-bg)",
    text: "var(--button-text-text)",
    hoverText: "var(--button-text-hover-text)",
  },
};

const style = computed(() => {
  const t = typeVars[props.type] ?? typeVars.default;

  return {
    "--el-button-bg-color": props.color ?? t.bg,
    "--el-button-text-color": props.textColor ?? t.text,
    "--el-button-hover-bg-color": props.hoverColor ?? t.hoverBg,
    "--el-button-hover-text-color": props.textHoverColor ?? t.hoverText,
  };
});

const classes = computed(() => [props.customClass].filter(Boolean).join(" "));
const handleClick = (event: MouseEvent) => emit("click", event);
</script>

<template>
  <el-button
    v-bind="$attrs"
    :class="classes"
    :style="style"
    @click="handleClick"
  >
    <slot name="iconPre" />
    <slot />
    <slot name="iconPost" />
  </el-button>
</template>

<style scoped></style>
