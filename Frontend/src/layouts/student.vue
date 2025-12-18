<!-- layouts/default.vue or app layout -->
<script setup lang="ts">
import { useRoute } from "vue-router";
import BaseFooter from "~/components/layout/BaseFooter.vue";
import BaseHeader from "~/components/layout/BaseHeader.vue";
import BaseSideBar from "~/components/layout/BaseSideBar.vue";
import schoolLogoLight from "~/assets/image/school-logo-light.png";

const route = useRoute();
</script>

<template>
  <el-container class="app-layout">
    <!-- Sidebar -->
    <el-aside width="240px" class="layout-aside">
      <BaseSideBar :logoSrc="schoolLogoLight" />
    </el-aside>

    <!-- Main area -->
    <el-container direction="vertical" class="layout-main-container">
      <!-- Header shell -->
      <el-header v-if="!route.meta.noHeader" class="layout-header">
        <BaseHeader />
      </el-header>

      <!-- Content -->
      <Transition name="page" mode="out-in">
        <el-main :key="route.fullPath" class="layout-main">
          <NuxtPage />
        </el-main>
      </Transition>

      <!-- Footer -->
      <el-footer v-if="!route.meta.noHeader" class="layout-footer">
        <BaseFooter />
      </el-footer>
    </el-container>
  </el-container>
</template>

<style lang="scss">
.app-layout {
  min-height: 100vh;
}

/* Outer aside – BaseSideBar handles visuals */
.layout-aside {
  background-color: transparent;
  border-right: none;
}

.layout-main-container {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
}

/* Header shell */
.layout-header {
  padding: 0;
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
}

/* Content */
.layout-main {
  padding: 16px;
  background: var(--color-bg);
  flex: 1 1 auto;
  overflow: auto;
}

/* Footer */
.layout-footer {
  padding: 8px 16px;
  background: var(--footer-bg);
  border-top: 1px solid var(--footer-border);
}

/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
