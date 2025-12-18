<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";

import schoolLogo from "~/assets/image/school-logo-light.png";
import googleIcon from "~/assets/icons/svg/google.svg";

import { iamService } from "~/api/iam/index";
import type { UserLoginForm } from "~/api/iam/iam.dto";

const authService = iamService().auth;
const loading = ref(false);

const form: UserLoginForm = reactive({
  email: "",
  password: "",
});

const emailRules = [
  { required: true, message: "Please enter email", trigger: "blur" },
];
const passwordRules = [
  { required: true, message: "Please enter password", trigger: "blur" },
];

const submit = async () => {
  if (!form.email || !form.password) {
    ElMessage.warning("Please enter email and password");
    return;
  }

  loading.value = true;
  try {
    await authService.login(form);
  } finally {
    loading.value = false;
  }
};

// const loginWithGoogle = () => authService.loginWithGoogle();
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
          :model="form"
          label-position="top"
          class="text-left"
          @submit.prevent="submit"
        >
          <el-form-item
            label="Email"
            :rules="emailRules"
            prop="email"
            class="mb-6"
          >
            <el-input
              v-model="form.email"
              placeholder="Email"
              autocomplete="email"
              class="auth-input"
            />
          </el-form-item>

          <el-form-item
            label="Password"
            :rules="passwordRules"
            prop="password"
            class="mb-6"
          >
            <el-input
              v-model="form.password"
              type="password"
              placeholder="Password"
              autocomplete="current-password"
              show-password
              class="auth-input"
            />
          </el-form-item>

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

        <!-- Google -->
        <el-button
          class="auth-google-btn w-full mt-2"
          :disabled="loading"
          @click=""
        >
          <img :src="googleIcon" alt="Google Icon" class="w-6 h-6" />
          <span>Login with Google</span>
        </el-button>

        <!-- Register -->
        <p class="auth-footer mt-4">
          Don't have an account?
          <RouterLink to="/auth/register" class="auth-link"
            >Register here</RouterLink
          >
        </p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Page background alignment with your tokens */
.auth-shell {
  min-height: calc(100vh - var(--header-height, 0px));
  display: grid;
  place-items: center;
  padding: 24px;
  background: var(--color-bg);
}

/* Card uses theme surface + border + shadow tokens */
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

/* Primary button - only uses your tokens */
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

/* Google button: neutral surface with theme border + hover bg */
.auth-google-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;

  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--color-card) 92%, var(--color-bg) 8%);
  color: var(--text-color);
  transition: background var(--transition-base),
    border-color var(--transition-base), transform var(--transition-base);
}

.auth-google-btn:hover {
  background: var(--hover-bg);
  border-color: color-mix(
    in srgb,
    var(--border-color) 55%,
    var(--color-primary) 45%
  );
  transform: translateY(-0.5px);
}

.auth-google-btn:active {
  transform: translateY(0px);
}

.auth-footer {
  font-size: 0.875rem;
  color: var(--muted-color);
  text-align: center;
}

.auth-link {
  margin-left: 6px;
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
