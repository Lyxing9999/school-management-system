<script setup lang="ts">
import {
  reactive,
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
  watch,
} from "vue";
import { useRoute, useRouter, navigateTo, useCookie } from "nuxt/app";
import type { FormInstance, FormRules } from "element-plus";
import { storeToRefs } from "pinia";

import BaseButton from "~/components/base/BaseButton.vue";
import NotificationDrawer from "~/components/notifications/NotificationDrawer.vue";

import { useIamService } from "~/api/iam";
import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/api/types/enums/role.enum";

import { useNotificationStore } from "~/stores/notificationStore";
import { usePreferencesStore } from "~/stores/preferencesStore";

import { useTheme } from "~/composables/system/useTheme";
import { useMessage } from "~/composables/common/useMessage";

definePageMeta({ layout: "default" });

/* -------------------------
   Core
------------------------- */
const route = useRoute();
const router = useRouter();
const msg = useMessage();

const authStore = useAuthStore();
const iam = useIamService();

const notifStore = useNotificationStore();
const { unreadCount } = storeToRefs(notifStore);

const prefs = usePreferencesStore();
const { notifAutoRefresh } = storeToRefs(prefs);

const { isDark, toggle: toggleTheme } = useTheme();

/* -------------------------
   Role (Student only)
------------------------- */
const user = computed(() => authStore.user);
const isStudent = computed(() => user.value?.role === Role.STUDENT);

/* -------------------------
   Tabs (Student)
------------------------- */
type TabKey = "account" | "notifications" | "appearance" | "preferences";
const allowedTabs: TabKey[] = [
  "account",
  "notifications",
  "appearance",
  "preferences",
];
const activeTab = ref<TabKey>("account");

watch(
  () => route.query.tab,
  (t) => {
    const tab = String(t ?? "") as TabKey;
    if (allowedTabs.includes(tab)) activeTab.value = tab;
  },
  { immediate: true }
);

watch(activeTab, (t) => {
  router.replace({ query: { ...route.query, tab: t } });
});

/* -------------------------
   Responsive
------------------------- */
const isMobile = ref(false);
let mq: MediaQueryList | null = null;
let onMqChange: ((e: MediaQueryListEvent) => void) | null = null;

onMounted(() => {
  if (!process.client) return;
  mq = window.matchMedia("(max-width: 768px)");
  isMobile.value = mq.matches;
  onMqChange = (e) => (isMobile.value = e.matches);
  mq.addEventListener("change", onMqChange);
});

onBeforeUnmount(() => {
  if (mq && onMqChange) mq.removeEventListener("change", onMqChange);
});

const descCols = computed(() => (isMobile.value ? 1 : 2));

/* -------------------------
   Loading
------------------------- */
const pageLoading = ref(false);

/* -------------------------
   Student profile (read-only)
------------------------- */
const profileRef = ref<FormInstance>();
const profileForm = reactive({ email: "", username: "" });

const profileRules: FormRules = {
  email: [
    { required: true, message: "Email is required", trigger: "blur" },
    { type: "email", message: "Invalid email format", trigger: "blur" },
  ],
  username: [
    { required: true, message: "Username is required", trigger: "blur" },
    { min: 3, message: "Min 3 characters", trigger: "blur" },
    { max: 30, message: "Max 30 characters", trigger: "blur" },
  ],
};

function hydrateProfile() {
  profileForm.email = String(authStore.user?.email ?? "");
  profileForm.username = String(authStore.user?.username ?? "");
}

/* -------------------------
   Student Start Page (COOKIE)
------------------------- */
type StudentHome = "dashboard" | "attendance";

const studentHomeCookie = useCookie<StudentHome | null>("student_home", {
  sameSite: "lax",
  path: "/",
});

const studentHome = ref<StudentHome>("dashboard");

function hydrateStudentHome() {
  studentHome.value =
    studentHomeCookie.value === "attendance" ? "attendance" : "dashboard";
}

function setStudentHome(v: StudentHome) {
  studentHome.value = v;
  studentHomeCookie.value = v;

  msg.showSuccess(
    v === "attendance" ? "Start page: Attendance" : "Start page: Dashboard"
  );
}

/* -------------------------
   Preferences
------------------------- */
const pageSizeOptions = computed<number[]>(() => prefs.getAllowedPageSizes());
const effectivePageSize = computed(() => prefs.getTablePageSize());
const recommendedPageSize = computed(() => prefs.DEFAULT_TABLE_PAGE_SIZE);

function setDefaultPageSize(size: number) {
  prefs.setTablePageSize(size);
  msg.showSuccess(`Default page size: ${prefs.getTablePageSize()}`);
}

function resetDefaultPageSize() {
  prefs.resetTablePageSize();
  msg.showSuccess(`Default page size reset: ${prefs.getTablePageSize()}`);
}

function setNotifAutoRefresh(v: boolean) {
  prefs.setNotifAutoRefresh(v);
}

/* -------------------------
   Notifications
------------------------- */
async function refreshUnread() {
  await notifStore.refreshUnread();
}

function openDrawer() {
  notifStore.toggleDrawer(true);
}

/* -------------------------
   Init
------------------------- */
onMounted(async () => {
  pageLoading.value = !authStore.isReady;

  try {
    if (!authStore.isReady) {
      await iam.auth.me();
    }
    hydrateProfile();
    hydrateStudentHome();
    await refreshUnread();
  } finally {
    pageLoading.value = false;
  }
});

/* -------------------------
   Header actions
------------------------- */
async function logout() {
  await iam.auth.logout();
}

function goDashboard() {
  const home = studentHome.value || "dashboard";
  navigateTo(
    home === "attendance" ? "/student/attendance" : "/student/dashboard"
  );
}
</script>

<template>
  <div class="settings-page" v-loading="pageLoading && !authStore.isReady">
    <div class="settings-container space-y-6">
      <!-- Header -->
      <div class="settings-header">
        <div class="settings-header__left">
          <div class="flex items-center gap-2">
            <el-icon><Setting /></el-icon>
            <div class="min-w-0">
              <div class="text-lg font-semibold">Settings</div>
              <div class="text-sm text-[var(--muted-color)]">
                Student account and basic preferences.
              </div>
            </div>
          </div>
        </div>

        <div class="settings-header__right">
          <BaseButton plain size="small" @click="goDashboard">
            Dashboard
          </BaseButton>
          <BaseButton type="danger" plain size="small" @click="logout">
            Logout
          </BaseButton>
        </div>
      </div>

      <el-card class="app-card">
        <el-tabs v-model="activeTab" class="settings-tabs">
          <!-- ACCOUNT -->
          <el-tab-pane name="account">
            <template #label>
              <span class="tab-label">
                <el-icon><UserIcon /></el-icon>
                Account
              </span>
            </template>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <el-card shadow="never" class="lg:col-span-2">
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-medium">Profile</span>
                    <div class="flex items-center gap-2">
                      <el-tag type="info">{{ user?.role }}</el-tag>
                      <el-tag type="warning">Read-only</el-tag>
                    </div>
                  </div>
                </template>

                <el-form
                  ref="profileRef"
                  :model="profileForm"
                  :rules="profileRules"
                  label-position="top"
                >
                  <div class="form-grid">
                    <el-form-item label="Email" prop="email">
                      <el-input v-model="profileForm.email" disabled />
                    </el-form-item>

                    <el-form-item label="Username" prop="username">
                      <el-input v-model="profileForm.username" disabled />
                    </el-form-item>

                    <el-form-item label="Status">
                      <el-input :model-value="user?.status ?? ''" disabled />
                    </el-form-item>

                    <el-form-item label="User ID">
                      <el-input :model-value="user?.id ?? ''" disabled />
                    </el-form-item>
                  </div>

                  <el-alert
                    class="mt-4"
                    type="info"
                    show-icon
                    :closable="false"
                    title="Students cannot edit account fields here. Contact your administrator if details are incorrect."
                  />
                </el-form>
              </el-card>

              <!-- Quick -->
              <el-card shadow="never">
                <template #header>
                  <span class="font-medium">Quick</span>
                </template>

                <div class="space-y-4 text-sm">
                  <!-- Theme -->
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium">Theme</div>
                      <div class="text-[var(--muted-color)]">
                        {{ isDark ? "Dark" : "Light" }}
                      </div>
                    </div>
                    <BaseButton plain size="small" @click="toggleTheme()">
                      Toggle
                    </BaseButton>
                  </div>

                  <el-divider />

                  <!-- Start Page -->
                  <div>
                    <div class="font-medium">Start page</div>
                    <div class="text-[var(--muted-color)] mt-1">
                      {{
                        studentHome === "attendance"
                          ? "Open Attendance first"
                          : "Open Dashboard first"
                      }}
                    </div>

                    <div class="mt-2 flex gap-2">
                      <el-button
                        size="small"
                        :type="
                          studentHome === 'dashboard' ? 'primary' : 'default'
                        "
                        @click="setStudentHome('dashboard')"
                      >
                        Dashboard
                      </el-button>

                      <el-button
                        size="small"
                        :type="
                          studentHome === 'attendance' ? 'primary' : 'default'
                        "
                        @click="setStudentHome('attendance')"
                      >
                        Attendance
                      </el-button>
                    </div>
                  </div>

                  <el-divider />

                  <!-- Access note -->
                  <div class="space-y-2">
                    <div class="font-medium">Access</div>
                    <el-alert
                      type="info"
                      show-icon
                      :closable="false"
                      title="Your account is managed by the school."
                    />
                    <div class="text-[var(--muted-color)] m-2">
                      If you need changes, contact your admin.
                    </div>
                  </div>
                </div>
              </el-card>
            </div>

            <el-card shadow="never" class="mt-4">
              <template #header>
                <span class="font-medium">Details</span>
              </template>

              <el-descriptions :column="descCols" border class="mt-2">
                <el-descriptions-item label="Role">
                  {{ user?.role }}
                </el-descriptions-item>
                <el-descriptions-item label="Status">
                  {{ user?.status }}
                </el-descriptions-item>
                <el-descriptions-item label="Email">
                  {{ user?.email }}
                </el-descriptions-item>
                <el-descriptions-item label="Username">
                  {{ user?.username }}
                </el-descriptions-item>
              </el-descriptions>

              <div v-if="isStudent" class="mt-3 text-sm hint-text">
                Students can change theme and basic preferences. Account fields
                are managed by the school.
              </div>
            </el-card>
          </el-tab-pane>

          <!-- NOTIFICATIONS -->
          <el-tab-pane name="notifications">
            <template #label>
              <span class="tab-label">
                <el-icon><Bell /></el-icon>
                Notifications
              </span>
            </template>

            <!-- IMPORTANT: items-start prevents equal-height stretching -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 items-start">
              <el-card shadow="never" class="lg:col-span-2">
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-medium">Unread badge</span>
                    <el-tag v-if="Number(unreadCount) > 0" type="danger">
                      {{ Number(unreadCount) }} unread
                    </el-tag>
                  </div>
                </template>

                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium">Auto-refresh badge</div>
                      <div class="text-sm text-[var(--muted-color)]">
                        Keeps the header badge updated.
                      </div>
                    </div>

                    <el-switch
                      :model-value="notifAutoRefresh"
                      @update:model-value="
                        (val) => setNotifAutoRefresh(Boolean(val))
                      "
                    />
                  </div>

                  <el-divider />

                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium">Open drawer</div>
                      <div class="text-sm text-[var(--muted-color)]">
                        Use the bell icon in the header.
                      </div>
                    </div>
                    <el-button size="small" plain @click="openDrawer">
                      Open
                    </el-button>
                  </div>

                  <el-divider />

                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium">Full page</div>
                      <div class="text-sm text-[var(--muted-color)]">
                        View your notifications list.
                      </div>
                    </div>
                    <el-button
                      size="small"
                      type="primary"
                      plain
                      @click="navigateTo('/student/notifications')"
                    >
                      Open
                    </el-button>
                  </div>
                </div>
              </el-card>

              <el-card shadow="never" class="self-start">
                <template #header>
                  <span class="font-medium">Actions</span>
                </template>

                <div class="space-y-2">
                  <div>
                    <el-button class="action-btn" plain @click="refreshUnread">
                      Refresh unread
                    </el-button>
                  </div>
                  <div>
                    <el-button class="action-btn" plain @click="openDrawer">
                      Open drawer
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>

            <NotificationDrawer />
          </el-tab-pane>

          <!-- APPEARANCE -->
          <el-tab-pane name="appearance">
            <template #label>
              <span class="tab-label">
                <el-icon><Brush /></el-icon>
                Appearance
              </span>
            </template>

            <el-card shadow="never">
              <template #header>
                <span class="font-medium">Theme</span>
              </template>

              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm font-medium">Mode</div>
                  <div class="text-sm text-[var(--muted-color)] mt-1">
                    {{ isDark ? "Dark theme enabled" : "Light theme enabled" }}
                  </div>
                </div>

                <BaseButton
                  type="primary"
                  plain
                  size="small"
                  @click="toggleTheme()"
                >
                  Toggle
                </BaseButton>
              </div>
            </el-card>
          </el-tab-pane>

          <!-- PREFERENCES -->
          <el-tab-pane name="preferences">
            <template #label>
              <span class="tab-label">
                <el-icon><Setting /></el-icon>
                Preferences
              </span>
            </template>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <el-card shadow="never" class="lg:col-span-2">
                <template #header>
                  <span class="font-medium">Table defaults</span>
                </template>

                <div class="space-y-4">
                  <div class="flex items-start justify-between gap-4">
                    <div class="min-w-0">
                      <div class="font-medium">Default page size</div>
                      <div class="text-sm text-[var(--muted-color)]">
                        Recommended:
                        <span class="font-medium">
                          {{ recommendedPageSize }}
                        </span>
                      </div>

                      <div class="mt-2 flex items-center gap-2">
                        <el-tag type="info">
                          Current: {{ effectivePageSize }}
                        </el-tag>
                        <el-tag type="success">
                          Recommended: {{ recommendedPageSize }}
                        </el-tag>
                      </div>
                    </div>

                    <div class="flex items-center gap-2">
                      <el-select
                        class="w-[160px]"
                        :model-value="effectivePageSize"
                        @update:model-value="setDefaultPageSize"
                      >
                        <el-option
                          v-for="s in pageSizeOptions"
                          :key="s"
                          :label="String(s)"
                          :value="s"
                        />
                      </el-select>

                      <el-button plain @click="resetDefaultPageSize">
                        Reset
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-card>

              <el-card shadow="never">
                <template #header>
                  <span class="font-medium">Help</span>
                </template>

                <div class="space-y-3 text-sm">
                  <div class="text-[var(--muted-color)]">
                    If data looks wrong, try refreshing and reloading the page.
                  </div>

                  <el-alert
                    type="warning"
                    show-icon
                    :closable="false"
                    title="If the issue persists, contact your administrator."
                  />
                </div>
              </el-card>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 16px;
}
.settings-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
.settings-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.settings-header__right {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
}
.hint-text {
  color: var(--muted-color);
}

/* Actions buttons: equal width + equal height + no wrap */
.action-btn {
  width: 100% !important;
  height: 40px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .settings-header {
    flex-direction: column;
    align-items: stretch;
  }
  .settings-header__right {
    justify-content: flex-end;
  }
}
</style>
