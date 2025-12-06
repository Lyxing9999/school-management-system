<script setup lang="ts">
import CambodiaCalendar from "~/components/Calendar/CambodiaCalendar.vue";
definePageMeta({
  layout: "teacher",
});
</script>

<template>
  <el-card class="w-full h-full">
    <CambodiaCalendar />
  </el-card>
</template>
