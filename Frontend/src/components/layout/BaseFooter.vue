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

<style scoped lang="scss">
.app-layout {
  min-height: 100vh;
}

/* no change */
.layout-aside {
  background-color: transparent;
  border-right: none;
}

.layout-main-container {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-width: 0; /* <<< add this */
}

.layout-header {
  padding: 0;
  background-color: var(--color-card);
  border-bottom: 1px solid #e5e7eb;
}

.layout-main {
  padding: 16px;
  background-color: var(--color-bg);
  flex: 1 1 auto;
  overflow: auto;
  min-width: 0; /* <<< add this too (safe in nested flex) */
}

.layout-footer {
  padding: 8px 16px;
  border-top: 1px solid #e5e7eb;
  background-color: var(--color-card);
}
</style>
