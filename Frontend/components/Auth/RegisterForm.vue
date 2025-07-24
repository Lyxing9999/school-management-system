<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import teacher from "~/assets/icons/svg/teacher.svg";
import student from "~/assets/icons/svg/student.svg";
import admin from "~/assets/icons/svg/admin.svg";
import type { AxiosError } from "axios";
import { UserService } from "~/services/userService";
const userService = new UserService();
const router = useRouter();

const loading = ref(false);
const hover = ref(false);

const form = reactive({
  username: "",
  password: "",
  confirmPassword: "",
  role: "student",
  agree: false,
});
const roles = [
  { label: "Student", value: "student", icon: student },
  { label: "Admin", value: "admin", icon: admin },
  { label: "Teacher", value: "teacher", icon: teacher },
];

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== form.password) {
    callback(new Error("Passwords do not match"));
  } else {
    callback();
  }
};
const register = async () => {
  if (!form.username) {
    ElMessage.warning("Username is required");
    return;
  }
  if (!form.password) {
    ElMessage.warning("Password is required");
    return;
  }
  if (!form.confirmPassword) {
    ElMessage.warning("Please confirm your password");
    return;
  }
  if (!form.role) {
    ElMessage.warning("Please select a role");
    return;
  }
  if (!form.agree) {
    ElMessage.warning("You must agree to the terms");
    return;
  }
  if (form.password !== form.confirmPassword) {
    ElMessage.error("Passwords do not match");
    return;
  }

  loading.value = true;

  try {
    const res = await userService.createUser({
      username: form.username,
      password: form.password,
      role: form.role,
    });

    ElMessage.success(res?.data?.message || "Registration successful!");
    router.push("/auth/login");
  } catch (err) {
    console.error("Registration error:", err);
    const message =
      (err as AxiosError<{ message: string }>)?.response?.data?.message ||
      (err as Error)?.message ||
      "Registration failed";
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};
const rules = {
  username: [
    { required: true, message: "Please input email", trigger: "blur" },
  ],
  password: [
    { required: true, message: "Please input password", trigger: "blur" },
  ],
  confirmPassword: [
    {
      required: true,
      message: "Please confirm your password",
      trigger: "blur",
    },
    { validator: validateConfirmPassword, trigger: "blur" },
  ],
};
</script>

<template>
  <Transition name="fade-slide" appear>
    <div
      class="max-w-md mx-auto mt-16 p-8 rounded-lg shadow-lg bg-white text-center font-inter"
    >
      <el-form
        :model="form"
        class="text-left"
        @submit.prevent="register"
        label-position="top"
      >
        <!-- Username -->
        <el-form-item class="mb-6" label="Username" :rules="rules.username">
          <el-input
            v-model="form.username"
            placeholder="Enter your username"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md"
          />
        </el-form-item>

        <!-- Password -->
        <el-form-item class="mb-6" label="Password" :rules="rules.password">
          <!-- Confirm Password -->
          <el-input
            v-model="form.password"
            placeholder="Enter your password"
            type="password"
            show-password
            autocomplete="new-password"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md"
          />
        </el-form-item>
        <el-form-item
          label="Confirm Password"
          :rules="rules.confirmPassword"
          class="mb-6"
        >
          <el-input
            v-model="form.confirmPassword"
            placeholder="Confirm your password"
            type="password"
            show-password
            autocomplete="new-password"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md"
          />
        </el-form-item>

        <!-- Role -->
        <el-form-item>
          <label
            for="role"
            class="block mb-2 text-sm"
            :style="{ color: 'var(--color-dark)' }"
          >
            Select Role
          </label>
          <el-select
            v-model="form.role"
            placeholder="Select your role"
            class="w-full rounded-md"
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
        <el-form-item class="mb-6">
          <el-checkbox
            class="ml-2"
            v-model="form.agree"
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
