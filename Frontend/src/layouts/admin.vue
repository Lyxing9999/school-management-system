<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { useRoute } from "vue-router";
import { useMediaQuery } from "@vueuse/core";

import BaseSideBar from "~/components/layout/BaseSideBar.vue";
import BaseHeader from "~/components/layout/BaseHeader.vue";
import BaseFooter from "~/components/layout/BaseFooter.vue";
import schoolLogoLight from "~/assets/image/school-logo-light.png";

const route = useRoute();

/** 768px matches your header toggle breakpoint */
const isMobile = useMediaQuery("(max-width: 768px)");

/**
 * Prevent SSR/client mismatch:
 * we hide the desktop aside until mounted.
 */
const isClientReady = ref(false);

const sidebarOpen = ref(false);

function toggleSidebar() {
  if (!isMobile.value) return;
  sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar() {
  sidebarOpen.value = false;
}

/** Close drawer when switching to desktop */
watch(isMobile, (mobile) => {
  if (!mobile) closeSidebar();
});

/** Close drawer after navigation on mobile */
watch(
  () => route.fullPath,
  async () => {
    if (!isMobile.value) return;
    await nextTick();
    closeSidebar();
  }
);

onMounted(() => {
  isClientReady.value = true;
});
</script>

<template>
  <el-container class="app-layout">
    <!-- Desktop aside (only after client ready to avoid flicker) -->
    <el-aside
      v-if="isClientReady && !isMobile"
      width="240px"
      class="layout-aside"
    >
      <BaseSideBar :logoSrc="schoolLogoLight" />
    </el-aside>

    <!-- Mobile drawer -->
    <el-drawer
      v-if="isClientReady && isMobile"
      v-model="sidebarOpen"
      direction="ltr"
      size="260px"
      :with-header="false"
      append-to-body
      lock-scroll
      destroy-on-close
      class="mobile-sidebar-drawer"
      @closed="sidebarOpen = false"
    >
      <BaseSideBar :logoSrc="schoolLogoLight" />
    </el-drawer>

    <!-- Main -->
    <el-container direction="vertical" class="layout-main-container">
      <el-header v-if="!route.meta.noHeader" class="layout-header">
        <BaseHeader @toggle-sidebar="toggleSidebar" />
      </el-header>

      <el-main :key="route.fullPath" class="layout-main">
        <NuxtPage />
      </el-main>

      <el-footer v-if="!route.meta.noHeader" class="layout-footer">
        <BaseFooter />
      </el-footer>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}

/* Desktop aside shell */
.layout-aside {
  background: transparent;
  border-right: none;
}

/* Header/footer surfaces driven by your system tokens */
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

/* Mobile Drawer */
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
