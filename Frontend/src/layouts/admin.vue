<script setup lang="ts">
import { useRoute } from "vue-router";
import BaseHeader from "~/components/layout/BaseHeader.vue";
import BaseFooter from "~/components/layout/BaseFooter.vue";
import BaseSideBar from "~/components/layout/BaseSideBar.vue";
import schoolLogo from "~/assets/image/school-logo.jpg";

const route = useRoute();
</script>

<template>
  <el-container class="app-layout">
    <!-- Sidebar -->
    <el-aside width="240px" class="layout-aside">
      <BaseSideBar :logoSrc="schoolLogo" />
    </el-aside>

    <!-- Main area -->
    <el-container direction="vertical" class="layout-main-container">
      <!-- Header -->
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
  height: 100vh;
}

/* Sidebar */
.layout-aside {
  border-right: 1px solid #e5e7eb;
  background-color: var(--color-card);
}

/* Main container */
.layout-main-container {
  display: flex;
  flex-direction: column;
}

/* Header */
.layout-header {
  padding: 0;
  background-color: var(--color-card);
  border-bottom: 1px solid #e5e7eb;
}

/* Main content area */
.layout-main {
  padding: 16px;
  background-color: var(--color-bg); /* now = light purple */
}

/* Footer */
.layout-footer {
  padding: 8px 16px;
  border-top: 1px solid #e5e7eb;
  background-color: var(--color-card);
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
