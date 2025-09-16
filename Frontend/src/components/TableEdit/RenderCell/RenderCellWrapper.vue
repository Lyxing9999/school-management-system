<script setup lang="ts">
import { defineProps, isVNode } from "vue";
import type { Component, VNode } from "vue";

const props = defineProps<{
  vnode?: VNode | string;
  component?: Component;
  componentProps?: Record<string, any>;
  value?: any;
}>();
</script>

<template>
  <span v-if="typeof props.vnode === 'string'">{{ props.vnode }}</span>

  <component
    v-else-if="isVNode(props.vnode)"
    :is="props.vnode.type"
    v-bind="props.vnode.props"
  >
    <template #default>
      <slot v-if="props.vnode.children">{{ props.vnode.children }}</slot>
    </template>
  </component>

  <component
    v-else-if="props.component"
    :is="props.component"
    v-bind="props.componentProps"
  />

  <span v-else>{{ props.value ?? "—" }}</span>
</template>
