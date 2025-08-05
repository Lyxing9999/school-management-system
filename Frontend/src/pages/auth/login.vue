<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import schoolLogo from "~/assets/image/school_logo.png";
import googleIcon from "~/assets/icons/svg/google.svg";
import { AuthService } from "~/services/authService";
import { useNuxtApp } from "nuxt/app";
import type { UserLoginForm } from "~/types";
import { AuthApi } from "~/api/AuthApi";
import type { AxiosInstance } from "axios";

const hover = ref(false);
const hoverGoogle = ref(false);
const $api = useNuxtApp().$api;
const authApi = new AuthApi($api as AxiosInstance);
const authService = new AuthService(authApi);
const loading = ref(false);

const form: UserLoginForm = reactive({
  username: "",
  password: "",
});

const usernameRules = [
  { required: true, message: "Please enter username", trigger: "blur" },
];
const passwordRules = [
  { required: true, message: "Please enter password", trigger: "blur" },
];

const submit = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning("Please enter username and password");
    return;
  }
  loading.value = true;
  try {
    await authService.login(form);
  } finally {
    loading.value = false;
  }
};

// const loginWithGoogle = () => {
//   authService.loginWithGoogle();
// };
</script>

<template>
  <Transition name="fade-slide" appear>
    <div
      class="max-w-md mx-auto mt-16 p-8 rounded-lg shadow-lg bg-white text-center font-sans"
    >
      <!-- School Logo -->
      <img
        :src="schoolLogo"
        alt="School Logo"
        class="w-40 sm:w-72 mx-auto mb-8 select-none"
      />

      <!-- Login Form -->
      <el-form
        :model="form"
        label-position="top"
        @submit.prevent="submit"
        class="text-left"
      >
        <el-form-item
          label="Username"
          :rules="usernameRules"
          prop="username"
          class="mb-6"
        >
          <el-input
            v-model="form.username"
            placeholder="Username"
            class="rounded-md text-[var(--color-dark)] placeholder:[var(--color-primary-light)]"
            autocomplete="username"
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
            class="rounded-md text-[var(--color-dark)] placeholder:[var(--color-primary-light)]"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            :disabled="loading"
            class="w-full rounded-md font-semibold shadow-md"
            style="
              background-color: var(--color-primary);
              color: var(--color-light);
            "
            @mouseover="hover = true"
            @mouseleave="hover = false"
            :style="
              hover ? 'background-color: var(--color-primary-light);' : ''
            "
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Google Login Button -->
      <el-button
        class="w-full mt-2 flex items-center justify-center gap-2 border rounded-md"
        @click="loginWithGoogle"
        @mouseover="hoverGoogle = true"
        @mouseleave="hoverGoogle = false"
      >
        <img :src="googleIcon" alt="Google Icon" class="w-7 h-7 m-2" />
        <span>Login with Google</span>
      </el-button>

      <!-- Register Link -->
      <p
        class="text-sm text-center mt-4"
        :style="{ color: 'var(--color-dark)' }"
      >
        Don't have an account?
        <RouterLink
          to="/auth/register"
          class="hover:underline"
          :style="{ color: 'var(--color-primary)' }"
        >
          Register here
        </RouterLink>
      </p>
    </div>
  </Transition>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
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
  transform: translateY(-20px);
}
</style>
