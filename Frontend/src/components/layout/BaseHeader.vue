<!-- components/Layout/BaseHeader.vue -->
<script setup lang="ts">
import { ref, computed } from "vue";
import {
  Menu,
  Bell,
  Sunny,
  Moon,
  ArrowDown,
  User as UserIcon,
} from "@element-plus/icons-vue";
import BaseInputSearch from "~/components/Base/BaseInputSearch.vue";
import { useAuthStore } from "~/stores/authStore";

const emit = defineEmits<{
  (e: "toggle-sidebar"): void;
}>();

const authStore = useAuthStore();

const searchQuery = ref("");
const isDark = ref(false);
const unreadNotifications = ref(5);

const displayName = computed(() => authStore.user?.username ?? "Admin User");

const toggleDark = () => {
  isDark.value = !isDark.value;
};

const handleNotificationClick = () => {
  console.log("Notification clicked");
};

const handleProfileClick = () => {
  console.log("Profile clicked");
};

const handleLogoutClick = () => {
  console.log("Logout clicked");
};
</script>

<template>
  <!-- No <header> tag, just this inner container for EL header -->
  <div class="header-inner">
    <el-row justify="space-between" align="middle" style="height: 100%">
      <!-- Left: sidebar toggle -->
      <el-col :span="6" class="flex items-center">
        <el-button
          type="text"
          class="icon-button mobile-toggle"
          @click="emit('toggle-sidebar')"
        >
          <el-icon><Menu /></el-icon>
        </el-button>
      </el-col>

      <!-- Middle: search -->
      <el-col :span="12" class="flex justify-center">
        <BaseInputSearch
          v-model="searchQuery"
          placeholder="Search..."
          clearable
          size="default"
          class="max-w-xl w-full"
        />
      </el-col>

      <!-- Right: actions -->
      <el-col :span="6" class="flex justify-end">
        <el-space size="small" alignment="center">
          <!-- Notifications -->
          <el-tooltip content="Notifications" placement="bottom">
            <el-badge
              :value="unreadNotifications"
              class="notification-badge"
              :hidden="unreadNotifications === 0"
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

          <!-- Dark mode -->
          <el-tooltip
            :content="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
            placement="bottom"
          >
            <el-button @click="toggleDark" type="text" class="icon-button">
              <el-icon v-if="isDark"><Sunny /></el-icon>
              <el-icon v-else><Moon /></el-icon>
            </el-button>
          </el-tooltip>

          <!-- User dropdown -->
          <el-dropdown trigger="click" placement="bottom-end">
            <el-button type="text" class="user-dropdown">
              <el-space size="small" alignment="center">
                <el-avatar :size="28">
                  <UserIcon />
                </el-avatar>
                <span class="user-name">{{ displayName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </el-space>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleProfileClick">
                  Profile
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogoutClick">
                  Logout
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-space>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.header-inner {
  width: 100%; /* full header width */
  height: 64px; /* full header height lives here */
  box-sizing: border-box;
  padding: 0 1.5rem;

  display: flex;
  align-items: center; /* vertically center row inside the 64px */
}

/* Buttons/icons */
.icon-button {
  padding: 4px;
  color: #4b5563;
}

.icon-button:hover {
  color: var(--color-primary);
}

.mobile-toggle {
  margin-left: 0.25rem;
}

/* User dropdown chip */
.user-dropdown {
  padding: 2px 8px;
  border-radius: 9999px;
  background-color: var(--color-primary-light-9);
}

.user-dropdown:hover {
  background-color: var(--color-primary-light-7);
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.notification-badge {
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .header-inner {
    padding: 0 1rem;
  }
}
</style>
