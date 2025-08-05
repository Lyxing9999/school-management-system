<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import student from "~/assets/icons/svg/student.svg";
import { useNuxtApp } from "nuxt/app";
import { AuthApi } from "~/api/AuthApi";
import type { AxiosInstance } from "axios";
import type { UserRegisterForm } from "~/types";
import { AuthService } from "~/services/authService";

const $api = useNuxtApp().$api;
const authApi = new AuthApi($api as AxiosInstance);
const authService = new AuthService(authApi);

const loading = ref(false);
const hover = ref(false);
const registerFormRef = ref();
const fieldErrors = ref<Record<string, string>>({});

const form = reactive({
  username: "",
  password: "",
  confirmPassword: "",
  role: "student",
  agree: false,
});
const roles = [
  { label: "Student", value: "student", icon: student },
  // { label: "Admin", value: "admin", icon: admin },
  // { label: "Teacher", value: "teacher", icon: teacher },
];

const clearFieldError = (field: string) => {
  fieldErrors.value[field] = "";
};

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== form.password) {
    callback(new Error("Passwords do not match"));
  } else {
    callback();
  }
};

const validatePasswordLength = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error("Please input password"));
  } else if (value.length < 6) {
    callback(new Error("Password must be at least 6 characters"));
  } else if (value.length > 50) {
    callback(new Error("Password must be at most 50 characters"));
  } else {
    callback();
  }
};

const userRegister = async () => {
  if (!registerFormRef.value) return;

  registerFormRef.value.validate(async (valid: boolean) => {
    if (!valid) {
      ElMessage.warning("Please fix the errors in the form.");
      return;
    }
    loading.value = true;
    const formData: UserRegisterForm = {
      username: form.username,
      password: form.password,
    };
    await authService.register(formData);
    loading.value = false;
  });
};

const rules = {
  username: [
    { required: true, message: "Please input username", trigger: "blur" },
  ],
  password: [
    { validator: validatePasswordLength, trigger: ["blur", "change"] },
  ],
  confirmPassword: [
    {
      required: true,
      message: "Please confirm your password",
      trigger: "blur",
    },
    { validator: validateConfirmPassword, trigger: "blur" },
  ],
  role: [
    { required: true, message: "Please select a role", trigger: "change" },
  ],
  agree: [
    {
      type: "boolean" as const,
      required: true,
      validator: (_rule: any, value: boolean, callback: any) => {
        if (!value) {
          callback(new Error("You must agree to the terms"));
        } else {
          callback();
        }
      },
      trigger: "change",
    },
  ],
};
</script>

<template>
  <Transition name="fade-slide" appear>
    <div
      class="max-w-md mx-auto mt-16 p-8 rounded-lg shadow-lg bg-white text-center font-inter"
    >
      <el-form
        ref="registerFormRef"
        :model="form"
        :rules="rules"
        class="text-left"
        @submit.prevent="userRegister"
        label-position="top"
      >
        <!-- Username -->
        <el-form-item
          class="mb-6"
          label="Username"
          prop="username"
          :error="fieldErrors.username"
        >
          <el-input
            v-model="form.username"
            placeholder="Enter your username"
            @input="clearFieldError('username')"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md"
          />
        </el-form-item>

        <!-- Password -->
        <el-form-item
          class="mb-6"
          label="Password"
          prop="password"
          :error="fieldErrors.password"
        >
          <el-input
            v-model="form.password"
            placeholder="Enter your password"
            type="password"
            show-password
            autocomplete="new-password"
            @input="clearFieldError('password')"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md"
          />
        </el-form-item>

        <!-- Confirm Password -->
        <el-form-item
          label="Confirm Password"
          prop="confirmPassword"
          class="mb-6"
          :error="fieldErrors.confirmPassword"
        >
          <el-input
            v-model="form.confirmPassword"
            placeholder="Confirm your password"
            type="password"
            show-password
            autocomplete="new-password"
            @input="clearFieldError('confirmPassword')"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md"
          />
        </el-form-item>

        <!-- Role -->
        <el-form-item prop="role" :error="fieldErrors.role">
          <label
            for="role"
            class="block mb-2 text-sm"
            :style="{ color: 'var(--color-dark)' }"
            >Select Role</label
          >
          <el-select
            v-model="form.role"
            placeholder="Select your role"
            class="w-full rounded-md"
            @change="clearFieldError('role')"
          >
            <template #prefix>
              <img
                v-if="form.role"
                :src="roles.find((r) => r.value === form.role)?.icon"
                alt=""
                class="inline-block w-5 h-5 mr-2"
              />
            </template>
            <el-option
              v-for="role in roles"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            >
              <template #default>
                <img
                  :src="role.icon"
                  alt=""
                  class="inline-block w-5 h-5 mr-2"
                />
                {{ role.label }}
              </template>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- Checkbox -->
        <el-form-item prop="agree" class="mb-6" :error="fieldErrors.agree">
          <el-checkbox
            class="ml-2"
            v-model="form.agree"
            @change="clearFieldError('agree')"
            :style="{ color: 'var(--color-dark)' }"
          >
            I agree to the
            <RouterLink
              to="/terms"
              class="hover:underline"
              :style="{ color: 'var(--color-primary)' }"
            >
              Terms and Conditions
            </RouterLink>
          </el-checkbox>
        </el-form-item>

        <!-- Submit -->
        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="w-full rounded-md font-semibold shadow-md"
            style="
              background-color: var(--color-primary);
              color: var(--color-light);
            "
            @mouseover="hover = true"
            @mouseleave="hover = false"
            :style="
              hover ? 'background-color: var(--color-primary-light); ' : ''
            "
          >
            Register
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Already Registered -->
      <p
        class="mt-4 text-center text-sm"
        :style="{ color: 'var(--color-dark)' }"
      >
        Already have an account?
        <RouterLink
          to="/auth/login"
          class="hover:underline"
          :style="{ color: 'var(--color-primary)' }"
        >
          Login here
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
  transform: translateY(20px);
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
  transform: translateY(20px);
}
</style>
