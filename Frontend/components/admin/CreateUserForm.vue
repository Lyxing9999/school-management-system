<script setup lang="ts">
import { reactive, ref } from "vue";
import { useMessage } from "~/composables/common/useMessage";
import { UserService } from "~/services/userService";
import { UserRole } from "~/services/authService";
import { useUserStore } from "~/stores/userStore";
import BaseForm from "~/components/Base/BaseForm.vue";
import type { AxiosInstance } from "axios";
const loading = ref(false);
const $api = useNuxtApp().$api as AxiosInstance;
const userService = new UserService($api);
const { showSuccess, showError } = useMessage();
const userStore = useUserStore();
const form = reactive({
  username: "",
  password: "",
  role: UserRole.Student,
});
const emit = defineEmits(["created"]);
const createUser = async () => {
  loading.value = true;
  try {
    const res = await userService.createUser(form);
    if (res.status === 201 || res.data.success || res.status === 200) {
      showSuccess("User created successfully");
      emit("created");
      form.username = "";
      form.password = "";
      form.role = UserRole.Student;
      await userStore.fetchUsers();
    } else {
      showError(res.data.message || "Failed to create user");
    }
  } catch (err: any) {
    showError(err?.message || "Failed to create user");
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <BaseForm :model="form" :loading="loading" @submit="createUser">
    <el-form-item label="Username">
      <el-input v-model="form.username" />
    </el-form-item>

    <el-form-item label="Password">
      <el-input v-model="form.password" type="password" show-password />
    </el-form-item>

    <el-form-item label="Role">
      <el-select v-model="form.role">
        <el-option :label="'Admin'" :value="UserRole.Admin" />
        <el-option :label="'Teacher'" :value="UserRole.Teacher" />
        <el-option :label="'Student'" :value="UserRole.Student" />
      </el-select>
    </el-form-item>
  </BaseForm>
</template>
<style></style>
