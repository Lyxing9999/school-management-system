<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useNuxtApp } from "#app";

import AppSidebar from "~/components/layouts/AppSidebar.vue";
import AppHeader from "~/components/layouts/AppHeader.vue";
import AppFooter from "~/components/layouts/AppFooter.vue";
import schoolLogoLight from "~/assets/image/school-logo-light.jpg";

const route = useRoute();
const router = useRouter();
const nuxtApp = useNuxtApp();

// ─── Loading skeleton state ────────────────────────────────────────────────
// Starts true so skeleton shows immediately on first load.
const pageLoading = ref(true);
let loadingTimeout: ReturnType<typeof setTimeout> | null = null;
// Track router guard cleanup
let removeAfterEach: (() => void) | null = null;

/** Arm the 5-second fallback — skeleton NEVER hangs forever. */
function armFallbackTimeout() {
  if (loadingTimeout) clearTimeout(loadingTimeout);
  loadingTimeout = setTimeout(() => {
    pageLoading.value = false;
    loadingTimeout = null;
  }, 5000);
}

/** Unconditionally finish loading and cancel any pending fallback. */
function finishLoading() {
  pageLoading.value = false;
  if (loadingTimeout) {
    clearTimeout(loadingTimeout);
    loadingTimeout = null;
  }
}

// ─── Nuxt page hooks (registered at top-level, not inside onMounted) ──────
// This ensures they capture the very first page:finish / page:error that Nuxt
// emits during SSR hydration, which fires BEFORE onMounted runs.
//
// ROOT CAUSE OF INFINITE LOADING: Nuxt fires page:error instead of
// page:finish when a page component throws during its setup() (e.g. an API
// call that crashes during SSR). Without listening to page:error, the skeleton
// stays forever until the fallback timeout fires.
const unHookPageStart = nuxtApp.hook("page:start", () => {
  pageLoading.value = true;
  armFallbackTimeout();
});

// page:finish fires on successful navigation completion.
const unHookPageFinish = nuxtApp.hook("page:finish", finishLoading);

// page:error fires when the page component throws during setup/render.
// This is the missing hook that was causing infinite loading on SSR errors.
const unHookPageError = nuxtApp.hook("page:loading:end", finishLoading);

// Arm fallback immediately for the very first page load.
armFallbackTimeout();

// ─── Sidebar / mobile state ────────────────────────────────────────────────
const MOBILE_BREAKPOINT = 768;
const sidebarOpen = ref(false);
const sidebarCollapsed = ref(false);

function toggleSidebar() {
  if (!process.client) return;
  if (window.innerWidth < MOBILE_BREAKPOINT) {
    sidebarOpen.value = !sidebarOpen.value;
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }
}

function closeSidebar() {
  sidebarOpen.value = false;
}

function syncSidebarStateByViewport() {
  if (!process.client) return;
  if (window.innerWidth < MOBILE_BREAKPOINT) {
    sidebarCollapsed.value = false;
  } else {
    sidebarOpen.value = false;
  }
}

onMounted(() => {
  if (!process.client) return;

  syncSidebarStateByViewport();
  window.addEventListener("resize", syncSidebarStateByViewport, {
    passive: true,
  });

  // ── Safety net #1: hide skeleton after first DOM paint ──────────────────
  // On the client-side hydration path, page:finish may have already fired
  // before this layout mounted. Use nextTick to hide skeleton if it wasn't
  // already hidden by the hooks above.
  nextTick(() => {
    // Only auto-finish on the very first mount, NOT during navigations
    // (navigations will be handled by page:finish / afterEach below).
    if (pageLoading.value) {
      // Give Nuxt one more tick to fire page:finish first.
      setTimeout(finishLoading, 300);
    }
  });

  // ── Safety net #2: vue-router afterEach ─────────────────────────────────
  // afterEach fires after EVERY navigation (success OR error), independently
  // of Nuxt's page hooks. This catches cases where page:finish is swallowed.
  removeAfterEach = router.afterEach(() => {
    // Small delay so Nuxt's own page:finish can run first if it's going to.
    setTimeout(finishLoading, 100);
  });
});

onBeforeUnmount(() => {
  if (!process.client) return;

  // 1. Remove window listeners
  window.removeEventListener("resize", syncSidebarStateByViewport);

  // 2. Cancel any pending fallback timeout
  if (loadingTimeout) {
    clearTimeout(loadingTimeout);
    loadingTimeout = null;
  }

  // 3. Remove router guard
  removeAfterEach?.();
  removeAfterEach = null;

  // 4. Unregister all Nuxt hooks (prevents ghost-firing after unmount)
  unHookPageStart();
  unHookPageFinish();
  unHookPageError();
});

/** Close mobile drawer on route change */
watch(
  () => route.fullPath,
  () => closeSidebar(),
);
</script>

<template>
  <el-container class="app-layout">
    <!-- Sidebar: desktop only -->
    <el-aside
      v-if="!sidebarCollapsed"
      width="240px"
      class="layout-aside desktop-only"
      tabindex="0"
    >
      <AppSidebar
        :logoSrc="schoolLogoLight"
        :collapsed="sidebarCollapsed"
        @navigate="closeSidebar"
      />
    </el-aside>

    <!-- Mobile drawer popup -->
    <el-drawer
      v-model="sidebarOpen"
      direction="ltr"
      size="240px"
      :with-header="false"
      class="mobile-sidebar-drawer mobile-only"
      @close="closeSidebar"
    >
      <AppSidebar
        :logoSrc="schoolLogoLight"
        :collapsed="false"
        @navigate="closeSidebar"
      />
    </el-drawer>

    <!-- Main -->
    <el-container
      direction="vertical"
      :class="['layout-main-container', { 'sidebar-hidden': sidebarCollapsed }]"
    >
      <!-- Header can be hidden per-page using route.meta.noHeader -->
      <el-header v-if="!route.meta.noHeader" class="layout-header">
        <AppHeader
          :sidebar-collapsed="sidebarCollapsed"
          @toggle-sidebar="toggleSidebar"
        />
      </el-header>

      <el-main :key="route.fullPath" class="layout-main">
        <el-skeleton :loading="pageLoading" animated>
          <template #template>
            <el-skeleton-item
              variant="text"
              style="width: 100%; height: 40px; margin-bottom: 16px"
            />
            <el-skeleton-item
              variant="rect"
              style="width: 100%; height: 200px; margin-bottom: 16px"
            />
            <el-skeleton-item
              variant="text"
              style="width: 80%; height: 20px; margin-bottom: 8px"
            />
            <el-skeleton-item
              variant="text"
              style="width: 60%; height: 20px; margin-bottom: 8px"
            />
            <el-skeleton-item
              variant="rect"
              style="width: 100%; height: 150px"
            />
          </template>
          <NuxtPage />
        </el-skeleton>
      </el-main>

      <el-footer v-if="!route.meta.noHeader" class="layout-footer">
        <AppFooter />
      </el-footer>
    </el-container>
  </el-container>
</template>

<style scoped>
/* ── layout.css handles background/border/padding via tokens ──
   This block only owns: positioning, animation, mobile state */

.layout-aside {
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  width: 240px;
  transform: translateX(0);
  opacity: 1;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s;
}

/* Auto-hide on collapse (desktop) */
.layout-aside:not(:hover):not(:focus-within).is-collapsed {
  transform: translateX(-220px);
  opacity: 0.1;
  pointer-events: none;
}

/* Desktop-only / mobile-only utilities */
.desktop-only {
  display: block;
}
.mobile-only {
  display: none;
}

@media (max-width: 768px) {
  .layout-aside {
    display: none !important;
  }
  .desktop-only {
    display: none !important;
  }
  .mobile-only {
    display: block !important;
  }
}

/* Mobile drawer: theme via real tokens */
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

/* Main container shifts right to clear the fixed sidebar */
.layout-main-container {
  margin-left: 240px;
  transition: margin-left 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.layout-main-container.sidebar-hidden {
  margin-left: 0;
}
@media (max-width: 768px) {
  .layout-main-container {
    margin-left: 0 !important;
  }
}
</style>
