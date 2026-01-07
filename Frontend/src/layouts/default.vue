<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute } from "vue-router";

import AppSidebar from "~/components/layouts/AppSidebar.vue";
import AppHeader from "~/components/layouts/AppHeader.vue";
import AppFooter from "~/components/layouts/AppFooter.vue";
import schoolLogoLight from "~/assets/image/school-logo-light.png";

const route = useRoute();

/**
 * Drawer only for mobile. Desktop sidebar is handled by CSS.
 * This avoids SSR guessing.
 */
const sidebarOpen = ref(false);

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar() {
  sidebarOpen.value = false;
}

/** Close drawer after navigation (mobile) */
watch(
  () => route.fullPath,
  () => closeSidebar()
);
</script>

<template>
  <el-container class="app-layout">
    <!-- Desktop aside: CSS handles visibility -->
    <el-aside width="240px" class="layout-aside hidden md:block">
      <AppSidebar :logoSrc="schoolLogoLight" @navigate="closeSidebar" />
    </el-aside>

    <!-- Mobile drawer: client-only (Element Plus drawer depends on DOM) -->
    <ClientOnly>
      <el-drawer
        v-model="sidebarOpen"
        direction="ltr"
        size="260px"
        :with-header="false"
        append-to-body
        lock-scroll
        destroy-on-close
        class="mobile-sidebar-drawer md:hidden"
        @closed="sidebarOpen = false"
      >
        <AppSidebar :logoSrc="schoolLogoLight" @navigate="closeSidebar" />
      </el-drawer>
    </ClientOnly>

    <!-- Main -->
    <el-container direction="vertical" class="layout-main-container">
      <el-header v-if="!route.meta.noHeader" class="layout-header">
        <AppHeader @toggle-sidebar="toggleSidebar" />
      </el-header>

      <el-main :key="route.fullPath" class="layout-main">
        <NuxtPage />
      </el-main>

      <el-footer v-if="!route.meta.noHeader" class="layout-footer">
        <AppFooter />
      </el-footer>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.layout-aside {
  background: transparent;
  border-right: none;
}

.layout-header {
  padding: 0;
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
}

.layout-main {
  padding: 16px;
  background: var(--color-bg);
  flex: 1 1 auto;
  overflow: auto;
}

.layout-footer {
  padding: 8px 16px;
  background: var(--footer-bg);
  border-top: 1px solid var(--footer-border);
}

/* Mobile Drawer theme */
:deep(.mobile-sidebar-drawer .el-drawer) {
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  box-shadow: 0 18px 42px var(--card-shadow);
}

:deep(.mobile-sidebar-drawer .el-drawer__body) {
  padding: 0;
  background: var(--sidebar-bg);
}

:deep(.mobile-sidebar-drawer .el-overlay) {
  background: rgba(0, 0, 0, 0.35);
}
:deep(html[data-theme="dark"] .mobile-sidebar-drawer .el-overlay) {
  background: rgba(0, 0, 0, 0.55);
}
</style>
