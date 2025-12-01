<script setup lang="ts">
definePageMeta({
  layout: "teacher",
});
</script>

<template>
  <div class="p-4 space-y-4">
    <h1 class="text-xl font-semibold">Notifications</h1>
    <p class="text-xs text-gray-500 mb-4">
      This is a placeholder. Later you can show system messages, schedule
      changes, or announcements here.
    </p>

    <el-empty description="No notifications yet" />
  </div>
</template>
