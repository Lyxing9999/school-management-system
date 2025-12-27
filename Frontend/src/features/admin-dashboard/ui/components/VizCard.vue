<script setup lang="ts">
const props = defineProps<{
  title: string;
  loading?: boolean;
  height?: number;
  optionExists?: boolean; // pass !!option
  emptyText?: string;
}>();

const h = props.height ?? 260;
</script>

<template>
  <el-card class="app-card viz-card" v-loading="loading">
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div class="font-semibold">{{ title }}</div>
        <slot name="actions" />
      </div>
    </template>

    <div
      v-if="optionExists === false"
      class="flex items-center justify-center text-xs text-gray-500"
      :style="{ height: `${h}px` }"
    >
      {{ emptyText ?? "No data available." }}
    </div>

    <ClientOnly v-else>
      <div class="w-full" :style="{ height: `${h}px` }">
        <slot />
      </div>

      <template #fallback>
        <div
          class="flex items-center justify-center text-xs text-gray-500"
          :style="{ height: `${h}px` }"
        >
          Loading chart...
        </div>
      </template>
    </ClientOnly>
  </el-card>
</template>
