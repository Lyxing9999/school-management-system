<!-- components/layout/AppFooter.vue -->
<script setup lang="ts">
const year = new Date().getFullYear();

const links = [
  { name: "Privacy Policy", url: "#" },
  { name: "Terms of Service", url: "#" },
];
</script>

<template>
  <el-footer class="app-footer">
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
  </el-footer>
</template>

<style scoped lang="scss">
.app-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 56px;
  border-top: 1px solid var(--color-primary-light-6);
  background-color: var(--color-card);
  font-size: 12px;
  color: #6b7280; 
}

.footer-left,
.footer-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-link {
  color: #6b7280;
  text-decoration: none;
  font-size: 12px;
  transition: color var(--transition-base);
}

.footer-link:hover {
  color: var(--color-primary);
  text-decoration: underline;
}

.footer-version {
  padding: 2px 8px;
  border-radius: 9999px;
  background-color: var(--color-primary-light-8);
  color: var(--color-primary);
  font-weight: 500;
}

/* Mobile: stack content */
@media (max-width: 640px) {
  .app-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    padding: 0.5rem 1rem;
    height: auto;
  }

  .footer-right {
    align-self: flex-end;
  }
}
</style>
