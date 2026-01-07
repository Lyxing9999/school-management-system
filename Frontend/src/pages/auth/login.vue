<script setup lang="ts">
import { ref, reactive } from "vue";
import type { FormInstance, FormRules } from "element-plus";
definePageMeta({ layout: false });
import schoolLogo from "~/assets/image/school-logo-light.png";

import { iamService } from "~/api/iam/index";
import type { UserLoginForm } from "~/api/iam/iam.dto";

const authService = iamService().auth;

const loading = ref(false);
const formRef = ref<FormInstance>();

const form = reactive<UserLoginForm>({
  email: "",
  password: "",
});

const rules: FormRules = {
  email: [
    { required: true, message: "Please enter email", trigger: "blur" },
    { type: "email", message: "Invalid email format", trigger: "blur" },
  ],
  password: [
    { required: true, message: "Please enter password", trigger: "blur" },
  ],
};

const submit = async () => {
  if (loading.value) return;

  const ok = await formRef.value?.validate().catch(() => false);
  if (!ok) return;

  loading.value = true;
  try {
    await authService.login(form);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <Transition name="fade-slide" appear>
    <div class="auth-shell">
      <div class="auth-card">
        <!-- Logo -->
        <div class="mb-5">
          <img :src="schoolLogo" alt="Logo" class="auth-logo" />
        </div>

        <!-- Form -->
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="text-left"
          @submit.prevent="submit"
        >
          <el-form-item label="Email" prop="email" class="mb-6">
            <el-input
              v-model="form.email"
              placeholder="Email"
              autocomplete="email"
              class="auth-input"
            />
          </el-form-item>

          <el-form-item label="Password" prop="password" class="mb-3">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="Password"
              autocomplete="current-password"
              show-password
              class="auth-input"
              @keyup.enter="submit"
            />
          </el-form-item>

          <!-- Forgot password -->
          <div class="flex items-center justify-end mb-6">
            <RouterLink to="/auth/reset-password" class="auth-link text-sm">
              Forgot password?
            </RouterLink>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              :disabled="loading"
              class="auth-primary-btn w-full"
            >
              Login
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.auth-shell {
  min-height: calc(100vh - var(--header-height, 0px));
  display: grid;
  place-items: center;
  padding: 24px;
  background: var(--color-bg);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 28px;
  border-radius: 14px;
  background: var(--color-card);
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 30px var(--card-shadow);
  color: var(--text-color);
}

.auth-logo {
  display: block;
  width: 72%;
  max-width: 260px;
  margin: 0 auto;
}

.auth-primary-btn {
  border-radius: 10px;
  font-weight: 650;
  background: var(--color-primary);
  color: var(--color-light);
  border: 1px solid color-mix(in srgb, var(--color-primary) 80%, transparent);
  box-shadow: 0 10px 18px
    color-mix(in srgb, var(--color-primary) 18%, transparent);
  transition: transform var(--transition-base),
    background var(--transition-base);
}

.auth-primary-btn:hover {
  background: var(--color-primary-light);
  transform: translateY(-0.5px);
}

.auth-primary-btn:active {
  transform: translateY(0px);
}

.auth-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.auth-link:hover {
  text-decoration: underline;
}

/* Animation */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-16px);
}
.fade-slide-enter-to {
  opacity: 1;
  transform: translateY(0);
}
.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-16px);
}
</style>
