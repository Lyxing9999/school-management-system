<script setup lang="ts">
defineProps<{ title: string; loading?: boolean }>();
</script>

<template>
  <el-card class="app-card viz-card" v-loading="loading">
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div class="font-semibold">{{ title }}</div>
        <slot name="actions" />
      </div>
    </template>

    <slot />
  </el-card>
</template>
