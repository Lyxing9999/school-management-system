<script setup lang="ts">
import { defineProps, withDefaults } from "vue";

const defaultClass =
  "el-footer flex justify-between items-center px-4 bg-white border-t h-16";

const props = withDefaults(
  defineProps<{
    footerClass?: string;
  }>(),
  {
    footerClass: defaultClass,
  }
);

const footerClass = props.footerClass;
</script>
<template>
  <el-footer :class="footerClass">
    © 2025 Your Company. All rights reserved.
  </el-footer>
</template>
