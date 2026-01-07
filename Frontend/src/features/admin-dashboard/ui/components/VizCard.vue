<script setup lang="ts">
import type { EChartsOption } from "echarts";

const props = withDefaults(
  defineProps<{
    title: string;
    loading?: boolean;
    height?: number;
    option?: EChartsOption | null;
    emptyText?: string;
  }>(),
  {
    loading: false,
    height: 260,
    option: null,
    emptyText: "No data available.",
  }
);
</script>

<template>
  <el-card class="app-card viz-card" v-loading="loading">
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div class="font-semibold">{{ title }}</div>
        <slot name="actions" />
      </div>
    </template>

    <!-- Empty state -->
    <div
      v-if="!option"
      class="flex items-center justify-center text-xs text-gray-500"
      :style="{ height: `${height}px` }"
    >
      {{ loading ? "Loading..." : emptyText }}
    </div>

    <!-- Chart (client-only) -->
    <ClientOnly v-else>
      <div class="w-full" :style="{ height: `${height}px` }">
        <VChart :option="option" autoresize class="w-full h-full" />
      </div>

      <template #fallback>
        <div
          class="flex items-center justify-center text-xs text-gray-500"
          :style="{ height: `${height}px` }"
        >
          Loading chart...
        </div>
      </template>
    </ClientOnly>
  </el-card>
</template>
