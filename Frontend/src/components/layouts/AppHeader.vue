<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, watch } from "vue";
import { navigateTo } from "nuxt/app";
import {
  Menu,
  Bell,
  Sunny,
  Moon,
  ArrowDown,
  User as UserIcon,
  Setting,
  SwitchButton,
} from "@element-plus/icons-vue";

import { useAuthStore } from "~/stores/authStore";
import { iamService } from "~/api/iam";
import { useNotificationStore } from "~/stores/notificationStore";
import NotificationDrawer from "~/components/notifications/NotificationDrawer.vue";
import { storeToRefs } from "pinia";
import { useTheme } from "~/composables/system/useTheme";
import { Role } from "~/api/types/enums/role.enum";
import { ROUTES } from "~/constants/routes";
import { usePreferencesStore } from "~/stores/preferencesStore";

const emit = defineEmits<{ (e: "toggle-sidebar"): void }>();

const authStore = useAuthStore();
const iam = iamService();

const notif = useNotificationStore();
const { unreadCount } = storeToRefs(notif);

const prefs = usePreferencesStore();
const { notifAutoRefresh } = storeToRefs(prefs);

const { isDark, toggle } = useTheme();

const displayName = computed(
  () => authStore.user?.username || (authStore.isReady ? "User" : "Loading...")
);

const settingsRoute = computed(() => {
  const role = authStore.user?.role;
  switch (role) {
    case Role.ADMIN:
      return ROUTES.ADMIN.SETTINGS;
    case Role.TEACHER:
      return ROUTES.TEACHER.SETTINGS;
    case Role.STUDENT:
      return ROUTES.STUDENT.SETTINGS;
    default:
      return "/auth/login";
  }
});

const handleNotificationClick = () => notif.toggleDrawer(true);

const handleSettingsClick = async () =>
  navigateTo({ path: settingsRoute.value, query: { tab: "account" } });

const handleLogoutClick = async () => {
  await iam.auth.logout();
};


let timer: number | null = null;

async function refreshUnreadSafe() {
  try {
    await notif.refreshUnread();
  } catch {

  }
}

function startPolling() {
  stopPolling();
  timer = window.setInterval(refreshUnreadSafe, 15000);
}

function stopPolling() {
  if (timer) {
    window.clearInterval(timer);
    timer = null;
  }
}

function onVisibility() {
  if (!document.hidden) refreshUnreadSafe();
}

onMounted(async () => {
  await refreshUnreadSafe();


  window.addEventListener("focus", refreshUnreadSafe);
  document.addEventListener("visibilitychange", onVisibility);

  if (notifAutoRefresh.value) startPolling();
});

onBeforeUnmount(() => {
  stopPolling();
  window.removeEventListener("focus", refreshUnreadSafe);
  document.removeEventListener("visibilitychange", onVisibility);
});

watch(
  notifAutoRefresh,
  (v) => {
    if (v) startPolling();
    else stopPolling();
  },
  { immediate: false }
);
</script>

<template>
  <div class="header-inner">
    <div class="header-left">
      <el-button
        type="text"
        class="icon-button mobile-toggle"
        aria-label="Toggle sidebar"
        @click="emit('toggle-sidebar')"
      >
        <el-icon><Menu /></el-icon>
      </el-button>
    </div>

    <div class="header-center" />

    <div class="header-right">
      <el-space size="small" alignment="center" class="header-actions">
        <el-tooltip content="Notifications" placement="bottom">
          <el-badge
            :value="Number(unreadCount)"
            :hidden="Number(unreadCount) <= 0"
            :max="99"
          >
            <el-button
              type="text"
              class="icon-button"
              @click="handleNotificationClick"
            >
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
        </el-tooltip>

        <el-tooltip
          :content="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          placement="bottom"
        >
          <el-button type="text" class="icon-button" @click="toggle()">
            <el-icon v-if="isDark"><Sunny /></el-icon>
            <el-icon v-else><Moon /></el-icon>
          </el-button>
        </el-tooltip>

        <el-dropdown trigger="click" placement="bottom-end">
          <el-button type="text" class="user-dropdown">
            <el-space size="small" alignment="center">
              <el-avatar :size="28"><UserIcon /></el-avatar>
              <span class="user-name">{{ displayName }}</span>
              <el-icon class="chev"><ArrowDown /></el-icon>
            </el-space>
          </el-button>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleSettingsClick">
                <el-icon><Setting /></el-icon>
                Settings
              </el-dropdown-item>

              <el-dropdown-item divided @click="handleLogoutClick">
                <el-icon><SwitchButton /></el-icon>
                Logout
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-space>
    </div>

    <NotificationDrawer />
  </div>
</template>
