<script setup lang="ts">
definePageMeta({
  layout: "admin",
});
import BaseDictInput from "~/components/admin/AdminAttendanceDict.vue";
import { ref } from "vue";
const form = ref<Record<string, string>>({});
</script>

<template>
  <div>
    <h2 class="text-2xl font-semibold mb-4">Dashboard</h2>
    <el-card class="p-6">
      <p>Welcome to the Admin Dashboard!</p>

      <BaseDictInput v-model="form" />
    </el-card>
  </div>
</template>
