<script setup lang="ts">
import { computed, useAttrs } from "vue";

const attrs = useAttrs();

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
    plain?: boolean;
    color?: string;
    hoverColor?: string;
    textColor?: string;
    textHoverColor?: string;
    loading?: boolean;
  }>(),
  {
    type: "default",
    plain: false,
  }
);

const emit = defineEmits<{ click: [MouseEvent] }>();

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

const isPlain = computed(() => {
  // supports <BaseButton plain> or <BaseButton v-bind="{ plain: true }">
  const attrPlain = attrs.plain !== undefined && attrs.plain !== false;
  return Boolean(props.plain || attrPlain);
});

const style = computed(() => {
  const t = typeVars[props.type] ?? typeVars.default;

  const baseBg = props.color ?? t.bg;
  const baseHoverBg = props.hoverColor ?? t.hoverBg;
  const baseText = props.textColor ?? t.text;
  const baseHoverText = props.textHoverColor ?? t.hoverText;

  const isText = props.type === "text";
  const isFilled = ["primary", "success", "warning", "danger", "info"].includes(
    props.type ?? "default"
  );
  const isCustomBg = Boolean(props.color);

  // ===== PLAIN MODE (important) =====
  if (isPlain.value && !isText) {
    // tint source: colored types use their color; default plain uses primary accent
    const tintSource = isFilled || isCustomBg ? baseBg : "var(--color-primary)";

    const plainHover = `color-mix(in srgb, ${tintSource} var(--btn-plain-hover-pct), transparent)`;
    const plainActive = `color-mix(in srgb, ${tintSource} var(--btn-plain-active-pct), transparent)`;

    return {
      "--el-button-bg-color": "transparent",
      "--el-button-text-color": isFilled || isCustomBg ? tintSource : baseText,

      "--el-button-hover-bg-color": plainHover,
      "--el-button-hover-text-color":
        isFilled || isCustomBg ? tintSource : "var(--color-primary)",

      "--el-button-border-color":
        isFilled || isCustomBg ? tintSource : "var(--btn-border)",
      "--el-button-hover-border-color":
        isFilled || isCustomBg ? tintSource : "var(--btn-border-hover)",
      "--el-button-active-border-color":
        isFilled || isCustomBg ? tintSource : "var(--btn-border-active)",

      "--el-button-active-bg-color": plainActive,
      "--el-button-active-text-color":
        isFilled || isCustomBg ? tintSource : "var(--color-primary)",

      "--el-button-disabled-bg-color": "transparent",
      "--el-button-disabled-text-color": "var(--btn-disabled-text)",
      "--el-button-disabled-border-color": "var(--btn-disabled-border)",

      "--el-border-radius-base": "var(--btn-radius)",
    } as Record<string, string>;
  }

  // ===== NORMAL (filled / default / text) =====
  const border = isText
    ? "transparent"
    : isFilled || isCustomBg
    ? baseBg
    : "var(--btn-border)";

  const hoverBorder = isText
    ? "transparent"
    : isFilled || Boolean(props.hoverColor) || isCustomBg
    ? baseHoverBg
    : "var(--btn-border-hover)";

  const activeBg = `color-mix(in srgb, var(--el-button-hover-bg-color) 85%, var(--btn-filled-active-mix) 15%)`;
  const activeBorder = isText
    ? "transparent"
    : isFilled || isCustomBg
    ? activeBg
    : "var(--btn-border-active)";

  return {
    "--el-button-bg-color": baseBg,
    "--el-button-text-color": baseText,
    "--el-button-hover-bg-color": baseHoverBg,
    "--el-button-hover-text-color": baseHoverText,

    "--el-button-border-color": border,
    "--el-button-hover-border-color": hoverBorder,
    "--el-button-active-border-color": activeBorder,

    "--el-button-active-bg-color": activeBg,
    "--el-button-active-text-color": "var(--el-button-hover-text-color)",

    "--el-button-disabled-bg-color": "var(--btn-disabled-bg)",
    "--el-button-disabled-text-color": "var(--btn-disabled-text)",
    "--el-button-disabled-border-color": "var(--btn-disabled-border)",

    "--el-border-radius-base": "var(--btn-radius)",
  } as Record<string, string>;
});

const classes = computed(() => [props.customClass].filter(Boolean).join(" "));
const handleClick = (event: MouseEvent) => emit("click", event);
</script>

<template>
  <el-button
    v-bind="$attrs"
    :class="classes"
    :style="style"
    :loading="props.loading"
    :disabled="props.loading || Boolean($attrs.disabled)"
    @click="handleClick"
  >
    <slot name="iconPre" />
    <slot />
    <slot name="iconPost" />
  </el-button>
</template>

<style scoped>
:deep(.el-button) {
  border-radius: var(--btn-radius);
  font-weight: var(--btn-font-weight);
  transition: background-color var(--transition-base),
    border-color var(--transition-base), color var(--transition-base),
    transform var(--transition-base), box-shadow var(--transition-base);
}

:deep(.el-button:not(.is-disabled):hover) {
  transform: translateY(var(--btn-lift-hover));
}

:deep(.el-button:not(.is-disabled):active) {
  transform: translateY(var(--btn-lift-active));
}

:deep(.el-button:focus-visible) {
  box-shadow: var(--btn-focus-ring);
}

:deep(.el-button.is-text) {
  border-color: transparent !important;
}

:deep(.el-button.is-loading) {
  pointer-events: none;
}
</style>
