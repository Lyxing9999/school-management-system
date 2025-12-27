<script setup lang="ts">
defineProps<{ label: string; value: string | number }>();
</script>

<template>
  <el-card class="app-card kpi-card">
    <div class="card-title">{{ label }}</div>
    <div class="text-2xl font-semibold mt-1">{{ value }}</div>
  </el-card>
</template>
