<script lang="ts" setup>
import BaseFooter from "~/components/Base/BaseFooter.vue";

const props = defineProps<{
  title: string;
}>();
</script>

<template>
  <BaseFooter :title="title" />
</template>
