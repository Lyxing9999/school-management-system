<script setup lang="ts">
import { defineProps } from "vue";
import type { VNode } from "vue";

const props = defineProps<{ vnode: VNode }>();
</script>

<template>
  <div>
    <component :is="{ render: () => props.vnode }" />
  </div>
</template>
