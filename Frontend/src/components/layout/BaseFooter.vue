<script setup lang="ts">
// Footer classes
const footerClass =
  "el-footer flex justify-between items-center px-6 py-3 border-t h-16 text-sm text-gray-500";

// Hardcoded links
const links = [
  { name: "Privacy Policy", url: "#" },
  { name: "Terms of Service", url: "#" },
];
</script>

<template>
  <el-footer :class="footerClass">
    <div class="flex items-center gap-4">
      <span>© 2025 Your Company. All rights reserved.</span>
      <span v-for="link in links" :key="link.name">
        <a :href="link.url" class="hover:underline">{{ link.name }}</a>
      </span>
    </div>

    <div class="flex items-center gap-3">
      <span class="ml-2">v1.0.0</span>
    </div>
  </el-footer>
</template>

<style scoped lang="scss"></style>
