<script setup lang="ts">
import { ref } from "vue";
import { Menu, Bell, Sunny, Moon, ArrowDown } from "@element-plus/icons-vue";
import BaseInputSearch from "~/components/Base/BaseInputSearch.vue";

// -----------------------------
// Reactive State
// -----------------------------
const searchQuery = ref("");
const isDark = ref(false); // Dark mode toggle

// -----------------------------
// Methods
// -----------------------------
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
  <el-header>
    <el-row justify="space-between" align="middle" style="height: 100%">
      <!-- Sidebar Toggle -->
      <el-col :span="6">
        <el-button type="text" class="mobile-toggle">
          <el-icon><Menu /></el-icon>
        </el-button>
      </el-col>

      <!-- Search -->
      <el-col :span="12">
        <BaseInputSearch
          v-model="searchQuery"
          placeholder="Search..."
          clearable
          size="default"
        />
      </el-col>

      <!-- Actions -->
      <el-col :span="6">
        <el-space>
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
              <el-space>
                <el-avatar :size="32" icon="User" />
                <span class="user-name">Admin User</span>
                <el-icon><ArrowDown /></el-icon>
              </el-space>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleProfileClick"
                  >Profile</el-dropdown-item
                >
                <el-dropdown-item divided @click="handleLogoutClick"
                  >Logout</el-dropdown-item
                >
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-space>
      </el-col>
    </el-row>
  </el-header>
</template>

<style scoped lang="scss">
.mobile-toggle {
  margin-left: 0.5rem;
}
.icon-button {
  padding: 0.25rem;
}
.user-dropdown {
  padding: 0.25rem 0.5rem;
}
.notification-badge {
  cursor: pointer;
}
.user-name {
  margin-left: 0.5rem;
}
</style>
