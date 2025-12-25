<script setup lang="ts">
import { isVNode } from "vue";
import type { Component, VNode } from "vue";

type RenderConfig = {
  component?: Component;
  componentProps?: Record<string, any>;
  value?: any;
};

const props = defineProps<{
  // Can be:
  // - string
  // - VNode
  // - RenderConfig { component, componentProps, value }
  vnode?: VNode | string | RenderConfig;
  component?: Component; // legacy / direct usage
  componentProps?: Record<string, any>; // legacy / direct usage
  value?: any;
}>();

const isObjectConfig = (v: unknown): v is RenderConfig => {
  return !!v && typeof v === "object" && !isVNode(v);
};
</script>

<template>
  <!-- 1) Simple string -->
  <span v-if="typeof props.vnode === 'string'">
    {{ props.vnode }}
  </span>

  <!-- 2) Real VNode -->
  <component
    v-else-if="isVNode(props.vnode)"
    :is="(props.vnode as VNode).type"
    v-bind="(props.vnode as VNode).props"
  >
    <template #default>
      <slot v-if="(props.vnode as VNode).children">
        {{ (props.vnode as VNode).children }}
      </slot>
    </template>
  </component>

  <component
    v-else-if="isObjectConfig(props.vnode) && (props.vnode as any).component"
    :is="(props.vnode as any).component"
    v-bind="(props.vnode as any).componentProps"
  >
    <template #default>
      {{ (props.vnode as any).value }}
    </template>
  </component>

  <component
    v-else-if="props.component"
    :is="props.component"
    v-bind="props.componentProps"
  >
    <template #default>
      {{ props.value }}
    </template>
  </component>

  <span v-else>
    {{ (props.vnode as any)?.value ?? props.value ?? "—" }}
  </span>
</template>
