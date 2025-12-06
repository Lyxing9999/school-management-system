<!-- components/layout/AppHeader.vue -->
<script setup lang="ts">
import { ref } from "vue";
import { Menu, Bell, Sunny, Moon, ArrowDown } from "@element-plus/icons-vue";
import BaseInputSearch from "~/components/Base/BaseInputSearch.vue";

const searchQuery = ref("");
const isDark = ref(false); // for future real dark mode toggle

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
  <el-header class="app-header">
    <el-row justify="space-between" align="middle" style="height: 100%">
      <!-- Left: sidebar toggle / logo placeholder -->
      <el-col :span="6" class="flex items-center">
        <el-button type="text" class="icon-button mobile-toggle">
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
              :value="5"
              class="notification-badge"
              @click="handleNotificationClick"
            >
              <el-button type="text" class="icon-button">
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
          </el-tooltip>

          <!-- Dark Mode Toggle -->
          <el-tooltip
            :content="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
            placement="bottom"
          >
            <el-button @click="toggleDark" type="text" class="icon-button">
              <el-icon v-if="isDark"><Sunny /></el-icon>
              <el-icon v-else><Moon /></el-icon>
            </el-button>
          </el-tooltip>

          <!-- User Dropdown -->
          <el-dropdown trigger="click" placement="bottom-end">
            <el-button type="text" class="user-dropdown">
              <el-space size="small" alignment="center">
                <el-avatar :size="28" icon="User" />
                <span class="user-name">Admin User</span>
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
  </el-header>
</template>

<style scoped lang="scss">
.app-header {
  height: 64px;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--color-primary-light-6);
  background-color: var(--color-card);
  display: flex;
  align-items: center;
}

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

/* Mobile: move search down if needed (optional) */
@media (max-width: 768px) {
  .app-header {
    padding: 0 1rem;
  }
}
</style>
