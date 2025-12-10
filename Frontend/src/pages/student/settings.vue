<script setup lang="ts">
definePageMeta({
  layout: "student",
});

import { ref } from "vue";
const form = ref<Record<string, string>>({});
</script>

<template>
  <div>
    <h2 class="text-2xl font-semibold mb-4">Settings</h2>
    <el-card class="p-6">
      <p>Student settings page.</p>

      <BaseDictInput v-model="form" />
    </el-card>
  </div>
</template>
