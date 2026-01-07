<script setup lang="ts">
import { ElTag } from "element-plus";

const props = defineProps<{
  value: any;
}>();
</script>

<template>
  <div v-if="Array.isArray(props.value)" class="flex flex-wrap gap-1">
    <el-tag v-for="item in props.value" :key="item" type="info">
      {{ item }}
    </el-tag>
  </div>
  <div v-else>
    {{ props.value }}
  </div>
</template>
