<script setup lang="ts">
import { h } from "vue";
import type { InlineEditProps } from "~/components/types/tableEdit";

const props = defineProps<{
  slotName: "append" | "prefix";
  row: Record<string, any>;
  field: string;
  childComponentProps?: InlineEditProps<any, string>["childComponentProps"];
}>();

const content = computed(() => {
  const slotFn = props.childComponentProps?.slots?.[props.slotName];
  if (slotFn) {
    const vnode = slotFn();
    return vnode;
  }
  return null;
});
</script>

<template>
  <span v-if="content">
    <component :is="content" />
  </span>
</template>
