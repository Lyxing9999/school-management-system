<!-- components/layout/BaseFooter.vue -->
<script setup lang="ts">
const year = new Date().getFullYear();

const links = [
  { name: "Privacy Policy", url: "#" },
  { name: "Terms of Service", url: "#" },
];
</script>

<template>
  <div class="app-footer">
    <div class="footer-left">
      <span>© {{ year }} Your School. All rights reserved.</span>

      <span v-for="link in links" :key="link.name" class="footer-link-wrapper">
        <a :href="link.url" class="footer-link">
          {{ link.name }}
        </a>
      </span>
    </div>

    <div class="footer-right">
      <span class="footer-version">v1.0.0</span>
    </div>
  </div>
</template>
