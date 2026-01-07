<script setup lang="ts">
import { computed, isVNode } from "vue";
import type { Component, VNode } from "vue";

type RenderConfig = {
  component?: Component;
  componentProps?: Record<string, any>;
  value?: any;
};

const props = defineProps<{
  vnode?: VNode | string | RenderConfig;
  component?: Component; // legacy
  componentProps?: Record<string, any>; // legacy
  value?: any;
  // optional: control truncation
  nowrap?: boolean;
}>();

const isObjectConfig = (v: unknown): v is RenderConfig => {
  return !!v && typeof v === "object" && !isVNode(v);
};

const textValue = computed(() => {
  if (typeof props.vnode === "string") return props.vnode;
  if (isObjectConfig(props.vnode)) return String(props.vnode.value ?? "");
  if (props.value != null) return String(props.value);
  return "";
});

// Tooltip via native title when truncated
const titleText = computed(() => (textValue.value ? textValue.value : ""));
</script>

<template>
  <span
    class="smart-cell"
    :class="{ 'smart-cell--nowrap': props.nowrap !== false }"
    :title="titleText"
  >
    <!-- 1) string -->
    <span v-if="typeof props.vnode === 'string'" class="smart-cell__text">
      {{ props.vnode }}
    </span>

    <!-- 2) VNode -->
    <span v-else-if="isVNode(props.vnode)" class="smart-cell__node">
      <component :is="props.vnode" />
    </span>

    <!-- 3) RenderConfig { component, componentProps, value } -->
    <component
      v-else-if="isObjectConfig(props.vnode) && (props.vnode as any).component"
      :is="(props.vnode as any).component"
      v-bind="(props.vnode as any).componentProps"
      class="smart-cell__component"
    >
      <template #default>
        <span class="smart-cell__text">
          {{ (props.vnode as any).value }}
        </span>
      </template>
    </component>

    <!-- 4) legacy direct component -->
    <component
      v-else-if="props.component"
      :is="props.component"
      v-bind="props.componentProps"
      class="smart-cell__component"
    >
      <template #default>
        <span class="smart-cell__text">
          {{ props.value }}
        </span>
      </template>
    </component>

    <!-- fallback -->
    <span v-else class="smart-cell__text">
      {{ (props.vnode as any)?.value ?? props.value ?? "—" }}
    </span>
  </span>
</template>

<style scoped>
.smart-cell {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-width: 0;
}

/* Default: truncate long text (better for table on small screens) */
.smart-cell--nowrap .smart-cell__text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* If you ever set nowrap="false", allow wrapping */
.smart-cell:not(.smart-cell--nowrap) .smart-cell__text {
  white-space: normal;
  overflow-wrap: anywhere;
}

.smart-cell__node,
.smart-cell__component {
  min-width: 0;
  max-width: 100%;
}

/* Khmer font helper (optional) */
:global(.font-kh) {
  font-family: "Noto Sans Khmer", "Khmer OS", system-ui, sans-serif;
}
</style>
