<script setup lang="ts">
import { ElSelect, ElOption } from "element-plus";

defineProps<{
  modelValue: string[]; // the prop
  options: string[];
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string[]): void;
}>();
</script>

<template>
  <el-select
    multiple
    filterable
    :model-value="modelValue"
    @update:model-value="(val) => emit('update:modelValue', val)"
  >
    <el-option v-for="s in options" :key="s" :label="s" :value="s" />
  </el-select>
</template>
