<script lang="ts" setup>
import DateRangeSelector from "~/components/Base/DateRangeSelector.vue";
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <el-card class="w-full h-full">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Select Date Range</h2>
      </div>
      <div style="el-primary ">
        <DateRangeSelector />
      </div>
    </el-card>
  </div>
</template>
