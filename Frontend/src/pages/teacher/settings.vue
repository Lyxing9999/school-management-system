<script setup lang="ts">
import {
  reactive,
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
  watch,
} from "vue";
import { useRoute, useRouter, navigateTo } from "nuxt/app";
import type { FormInstance, FormRules } from "element-plus";
import { storeToRefs } from "pinia";

import BaseButton from "~/components/base/BaseButton.vue";
import NotificationDrawer from "~/components/notifications/NotificationDrawer.vue";

import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/api/types/enums/role.enum";

import { useNotificationStore } from "~/stores/notificationStore";
import { usePreferencesStore } from "~/stores/preferencesStore";

import { useTheme } from "~/composables/system/useTheme";
import { useMessage } from "~/composables/common/useMessage";

import type { UpdateMePayload, ChangePasswordForm } from "~/api/iam/iam.dto";

definePageMeta({ layout: "default" });

/* -------------------------
   Core
------------------------- */
const route = useRoute();
const router = useRouter();
const msg = useMessage();

const authStore = useAuthStore();
const { $authService } = useNuxtApp();

const notifStore = useNotificationStore();
const { unreadCount } = storeToRefs(notifStore);

const prefs = usePreferencesStore();
const { notifAutoRefresh } = storeToRefs(prefs);
const { isDark, toggle, setTheme } = useTheme();
function toggleTheme() {
  toggle();
}

/* -------------------------
   Role helpers (Admin / Teacher / Student)
------------------------- */
const user = computed(() => authStore.user);

const isAdmin = computed(() => user.value?.role === Role.ADMIN);
const isTeacher = computed(() => user.value?.role === Role.TEACHER);
const isStudent = computed(() => user.value?.role === Role.STUDENT);

const canEditProfile = computed(() => isAdmin.value || isTeacher.value);
const canChangePw = computed(() => isAdmin.value || isTeacher.value);

const dashboardPath = computed(() => {
  if (isAdmin.value) return "/admin/dashboard";
  if (isTeacher.value) return "/teacher/dashboard";
  return "/student/dashboard";
});

/* -------------------------
   Tabs (clean: no inline-edit for Teacher)
------------------------- */
type TabKey =
  | "account"
  | "security"
  | "notifications"
  | "appearance"
  | "preferences";

const activeTab = ref<TabKey>("account");

watch(
  () => route.query.tab,
  (t) => {
    const tab = String(t ?? "") as TabKey;
    if (
      tab === "account" ||
      tab === "security" ||
      tab === "notifications" ||
      tab === "appearance" ||
      tab === "preferences"
    ) {
      activeTab.value = tab;
    }
  },
  { immediate: true }
);

watch(activeTab, (t) => {
  router.replace({ query: { ...route.query, tab: t } });
});

/* -------------------------
   Responsive: descriptions columns
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
   Loading states
------------------------- */
const pageLoading = ref(false);
const savingProfile = ref(false);
const changingPw = ref(false);

/* -------------------------
   Account form
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

const profileChanged = computed(() => {
  const u = authStore.user;
  if (!u) return false;

  const emailNow = profileForm.email.trim().toLowerCase();
  const emailOld = String(u.email ?? "")
    .trim()
    .toLowerCase();

  const userNow = profileForm.username.trim();
  const userOld = String(u.username ?? "").trim();

  return emailNow !== emailOld || userNow !== userOld;
});

const canSaveProfile = computed(() => {
  if (!canEditProfile.value) return false;
  if (!profileChanged.value) return false;
  return (
    profileForm.email.trim().length > 0 &&
    profileForm.username.trim().length > 0
  );
});

async function saveProfile() {
  if (!canSaveProfile.value || savingProfile.value) return;

  const formEl = profileRef.value;
  if (!formEl) return;

  await formEl.validate(async (valid) => {
    if (!valid) return;

    savingProfile.value = true;
    try {
      const payload: UpdateMePayload = {
        email: profileForm.email.trim().toLowerCase(),
        username: profileForm.username.trim(),
      } as any;

      const updated = await $authService.updateMe(payload);
      if (updated) {
        hydrateProfile();
      }
    } finally {
      savingProfile.value = false;
    }
  });
}

function resetProfile() {
  hydrateProfile();
  profileRef.value?.clearValidate();
}

/* -------------------------
   Password form
------------------------- */
const pwRef = ref<FormInstance>();
const pwForm = reactive<ChangePasswordForm>({
  current_password: "",
  new_password: "",
});

const pwRules: FormRules = {
  current_password: [{ required: true, message: "Required", trigger: "blur" }],
  new_password: [
    { required: true, message: "Required", trigger: "blur" },
    { min: 6, message: "Min 6 characters", trigger: "blur" },
  ],
};

const canChangePassword = computed(() => {
  if (!canChangePw.value) return false;
  const cur = pwForm.current_password.trim();
  const nw = pwForm.new_password.trim();
  return cur.length > 0 && nw.length >= 6 && cur !== nw;
});

async function changePassword() {
  if (!canChangePassword.value || changingPw.value) return;

  const formEl = pwRef.value;
  if (!formEl) return;

  await formEl.validate(async (valid) => {
    if (!valid) return;

    changingPw.value = true;
    try {
      const ok = await $authService.changePassword({
        current_password: pwForm.current_password.trim(),
        new_password: pwForm.new_password.trim(),
      });

      if (!ok) return;

      msg.showSuccess("Password changed. You will be signed out.");
      pwForm.current_password = "";
      pwForm.new_password = "";
      pwRef.value?.clearValidate();
    } finally {
      changingPw.value = false;
    }
  });
}

/* -------------------------
   Preferences
------------------------- */
const pageSizeOptions = computed<number[]>(() => prefs.getAllowedPageSizes());
const effectivePageSize = computed(() => prefs.getTablePageSize());
const recommendedPageSize = computed(() => prefs.DEFAULT_TABLE_PAGE_SIZE);

function setDefaultPageSize(size: number) {
  prefs.setTablePageSize(size);
}
function resetDefaultPageSize() {
  prefs.resetTablePageSize();
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
      await $authService.getMe();
    }
    hydrateProfile();
    await refreshUnread();
  } finally {
    pageLoading.value = false;
  }
});

/* -------------------------
   Header actions
------------------------- */
async function logout() {
  await $authService.logout();
}
function goDashboard() {
  navigateTo(dashboardPath.value);
}
const autoRefreshBadge = computed<boolean>({
  get: () => notifAutoRefresh.value,
  set: (v) => prefs.setNotifAutoRefresh(v),
});
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
                Manage account, security, and preferences.
              </div>
            </div>
          </div>
        </div>

        <div class="settings-header__right">
          <BaseButton plain size="small" @click="goDashboard"
            >Dashboard</BaseButton
          >
          <BaseButton type="danger" plain size="small" @click="logout"
            >Logout</BaseButton
          >
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
                      <el-tag v-if="!canEditProfile" type="warning"
                        >Read-only</el-tag
                      >
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
                      <el-input
                        v-model="profileForm.email"
                        :disabled="!canEditProfile"
                        autocomplete="email"
                      />
                    </el-form-item>

                    <el-form-item label="Username" prop="username">
                      <el-input
                        v-model="profileForm.username"
                        :disabled="!canEditProfile"
                        autocomplete="username"
                      />
                    </el-form-item>

                    <el-form-item label="Status">
                      <el-input :model-value="user?.status ?? ''" disabled />
                    </el-form-item>

                    <el-form-item label="User ID">
                      <el-input :model-value="user?.id ?? ''" disabled />
                    </el-form-item>
                  </div>

                  <div class="card-actions" v-if="canEditProfile">
                    <BaseButton
                      type="primary"
                      size="small"
                      :loading="savingProfile"
                      :disabled="!canSaveProfile || savingProfile"
                      @click="saveProfile"
                    >
                      Save
                    </BaseButton>

                    <BaseButton
                      plain
                      size="small"
                      :disabled="savingProfile"
                      @click="resetProfile"
                    >
                      Reset
                    </BaseButton>
                  </div>

                  <el-alert
                    v-if="canEditProfile && profileChanged"
                    class="mt-4"
                    type="info"
                    show-icon
                    :closable="false"
                    title="You have unsaved changes."
                  />
                </el-form>
              </el-card>

              <!-- Quick -->
              <el-card shadow="never">
                <template #header
                  ><span class="font-medium">Quick</span></template
                >

                <div class="space-y-4 text-sm">
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium">Theme</div>
                      <div class="text-[var(--muted-color)]">
                        {{ isDark ? "Dark" : "Light" }}
                      </div>

                      <BaseButton plain size="small" @click="toggleTheme">
                        Toggle
                      </BaseButton>
                    </div>
                    <BaseButton
                      plain
                      size="small"
                      @click="setTheme(isDark ? 'light' : 'dark')"
                      >Toggle</BaseButton
                    >
                  </div>

                  <el-divider />

                  <div class="space-y-2">
                    <div class="font-medium">Access</div>
                    <el-alert
                      type="info"
                      show-icon
                      :closable="false"
                      title="Your permissions are managed by the school administrator."
                    />
                    <div class="text-[var(--muted-color)]">
                      If you need access to additional features, contact your
                      admin.
                    </div>
                  </div>
                </div>
              </el-card>
            </div>

            <el-card shadow="never" class="mt-4">
              <template #header
                ><span class="font-medium">Details</span></template
              >

              <el-descriptions :column="descCols" border class="mt-2">
                <el-descriptions-item label="Role">{{
                  user?.role
                }}</el-descriptions-item>
                <el-descriptions-item label="Status">{{
                  user?.status
                }}</el-descriptions-item>
                <el-descriptions-item label="Email">{{
                  user?.email
                }}</el-descriptions-item>
                <el-descriptions-item label="Username">{{
                  user?.username
                }}</el-descriptions-item>
              </el-descriptions>

              <div v-if="isStudent" class="mt-3 text-sm hint-text">
                Students can view details but cannot edit account fields.
              </div>

              <div v-else-if="isTeacher" class="mt-3 text-sm hint-text">
                Teachers can update profile and password, and manage
                preferences.
              </div>
            </el-card>
          </el-tab-pane>

          <!-- SECURITY -->
          <el-tab-pane name="security">
            <template #label>
              <span class="tab-label">
                <el-icon><Lock /></el-icon>
                Security
              </span>
            </template>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <el-card shadow="never" class="lg:col-span-2">
                <template #header
                  ><span class="font-medium">Change password</span></template
                >

                <el-form
                  v-if="canChangePw"
                  ref="pwRef"
                  :model="pwForm"
                  :rules="pwRules"
                  label-position="top"
                >
                  <div class="form-grid">
                    <el-form-item
                      label="Current password"
                      prop="current_password"
                    >
                      <el-input
                        v-model="pwForm.current_password"
                        type="password"
                        show-password
                        autocomplete="current-password"
                        placeholder="Enter your current password"
                      />
                    </el-form-item>

                    <el-form-item label="New password" prop="new_password">
                      <el-input
                        v-model="pwForm.new_password"
                        type="password"
                        show-password
                        autocomplete="new-password"
                        placeholder="Enter your new password"
                      />
                    </el-form-item>
                  </div>

                  <div class="card-actions">
                    <BaseButton
                      type="warning"
                      size="small"
                      :loading="changingPw"
                      :disabled="!canChangePassword || changingPw"
                      @click="changePassword"
                    >
                      Change password
                    </BaseButton>
                  </div>

                  <el-alert
                    class="mt-4"
                    type="warning"
                    show-icon
                    :closable="false"
                    title="After changing password, you may be logged out and must sign in again."
                  />
                </el-form>

                <el-alert
                  v-else
                  type="info"
                  show-icon
                  :closable="false"
                  title="Students cannot change password from this panel. Please contact your administrator if you need help."
                />
              </el-card>

              <el-card shadow="never">
                <template #header
                  ><span class="font-medium">Notes</span></template
                >
                <ul class="text-sm space-y-2">
                  <li class="flex gap-2">
                    <el-icon class="mt-[2px]"><WarningFilled /></el-icon>
                    Use at least 6+ characters.
                  </li>
                  <li class="flex gap-2">
                    <el-icon class="mt-[2px]"><WarningFilled /></el-icon>
                    Avoid reusing passwords.
                  </li>
                </ul>
              </el-card>
            </div>
          </el-tab-pane>

          <!-- NOTIFICATIONS -->
          <el-tab-pane name="notifications">
            <template #label>
              <span class="tab-label">
                <el-icon><Bell /></el-icon>
                Notifications
              </span>
            </template>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
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
                    <ElSwitch v-model="autoRefreshBadge" />
                  </div>

                  <el-divider />

                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium">Open drawer</div>
                      <div class="text-sm text-[var(--muted-color)]">
                        Use the bell icon in the header.
                      </div>
                    </div>
                    <el-button size="small" plain @click="openDrawer"
                      >Open</el-button
                    >
                  </div>

                  <el-divider />

                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium">Full page</div>
                      <div class="text-sm text-[var(--muted-color)]">
                        Search, filter, bulk actions.
                      </div>
                    </div>
                    <el-button
                      size="small"
                      type="primary"
                      plain
                      @click="
                        navigateTo(
                          isTeacher
                            ? '/teacher/notifications'
                            : '/admin/notifications'
                        )
                      "
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
              <template #header
                ><span class="font-medium">Theme</span></template
              >

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
                  >Toggle</BaseButton
                >
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
                <template #header
                  ><span class="font-medium">Table defaults</span></template
                >

                <div class="space-y-4">
                  <div class="flex items-start justify-between gap-4">
                    <div class="min-w-0">
                      <div class="font-medium">Default page size</div>
                      <div class="text-sm text-[var(--muted-color)]">
                        Applies to paginated tables. Recommended:
                        <span class="font-medium">{{
                          recommendedPageSize
                        }}</span>
                      </div>

                      <div class="mt-2 flex items-center gap-2">
                        <el-tag type="info"
                          >Current: {{ effectivePageSize }}</el-tag
                        >
                        <el-tag type="success"
                          >Recommended: {{ recommendedPageSize }}</el-tag
                        >
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

                      <el-button plain @click="resetDefaultPageSize"
                        >Reset</el-button
                      >
                    </div>
                  </div>
                </div>
              </el-card>

              <el-card shadow="never">
                <template #header
                  ><span class="font-medium">Help</span></template
                >

                <div class="space-y-3 text-sm">
                  <div class="text-[var(--muted-color)]">
                    If data looks wrong or a save fails, try refreshing and
                    reloading the page.
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
.card-actions {
  margin-bottom: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.hint-text {
  color: var(--muted-color);
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
  .card-actions {
    justify-content: stretch;
  }
  .card-actions :deep(button) {
    width: 100%;
  }
}
</style>
