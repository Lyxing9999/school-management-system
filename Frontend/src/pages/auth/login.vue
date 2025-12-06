<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import schoolLogo from "~/assets/image/school-logo.jpg";
import googleIcon from "~/assets/icons/svg/google.svg";
import { iamService } from "~/api/iam/index";
import type { UserLoginForm } from "~/api/iam/iam.dto";

const hover = ref(false);
const hoverGoogle = ref(false);
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

// const loginWithGoogle = () => {
//   authService.loginWithGoogle();
// };
</script>

<template>
  <Transition name="fade-slide" appear>
    <div
      class="w-1/2 max-w-md mx-auto mt-16 p-8 rounded-lg text-center shadow-lg font-sans bg-white"
      style="box-shadow: 0 4px 12px var(--card-shadow)"
    >
      <!-- School Logo -->
      <div class="mb-4">
        <img :src="schoolLogo" alt="Logo" class="w-2/3 h-2/3 mx-auto" />
      </div>
      <!-- Login Form -->

      <el-form
        :model="form"
        label-position="top"
        @submit.prevent="submit"
        class="text-left"
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
            :style="
              hover ? 'background-color: var(--color-primary-light); ' : ''
            "
            @mouseover="hover = true"
            @mouseleave="hover = false"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Google Login Button -->
      <el-button
        class="w-full mt-2 flex items-center justify-center gap-2 border rounded-md"
        @click=""
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
