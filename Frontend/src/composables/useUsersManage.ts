// composables/useUsersManage.ts
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "~/src/stores/userStore";
import { UserService } from "~/src/services/userService";
import { unflatten } from "~/src/utils/unflatten";
import { UserStoreError } from "~/src/errors/UserStoreError";
import type { AxiosInstance } from "axios";

export function useUsersManage() {
  const userStore = useUserStore();
  const $api = useNuxtApp().$api as AxiosInstance;
  const userService = new UserService($api as AxiosInstance);
  const { showSuccess, showError, showInfo } = useMessage();

  const showDialog = ref(false);
  const showCreateUserDialog = ref(false);
  const userDetails = ref<RawUserDetail | null>(null);
  const dialogLoading = ref(false);
  const dialogKey = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);
  const hasDraft = ref(false);
  const saveId = ref<string | null>(null);
  const handleRole = ref<Role | null>(null);
  const editing = ref<{
    id: string | null;
    field: CreateUserFormFields | null;
  }>({
    id: null,
    field: null,
  });
  type RawUserDetail = {
    role: Role;
    data: any;
  };
  const originalValue = ref<{ username?: string; email?: string }>({});

  // Computed users from store
  const users = computed(() => userStore.users);

  // Role-based fields
  const roleFields = computed(() => {
    if (handleRole.value === Role.TEACHER) return teacherFields;
    if (handleRole.value === Role.STUDENT) return studentFields;
    return adminFields;
  });

  const userInfo = computed(() => {
    if (!userDetails.value) return null;
    console.log("this is userInfo from composable", userDetails.value.data);
    return userDetails.value.data;
  });

  // Load users on mounted
  onMounted(async () => {
    await userStore.fetchUsers();
  });

  // Cancel inline edit: revert changes
  function cancelEdit(row: any, field: CreateUserFormFields) {
    if (field === CreateUserFormFields.Username) {
      row.username = originalValue.value.username ?? row.username;
    } else if (field === CreateUserFormFields.Email) {
      row.email = originalValue.value.email ?? row.email;
    }
    editing.value = { id: null, field: null };
  }

  // Delete user
  async function handleDelete(user: User) {
    try {
      await userService.deleteUser(user._id);
      showSuccess("User deleted successfully");
      await userStore.fetchUsers();
    } catch (error) {
      if (error instanceof UserStoreError) {
        showError(error.message);
      } else {
        showError((error as any)?.message || "Failed to delete user");
      }
    }
  }

  // Submit inline edit
  async function submitInlineEdit(row: any, field: string) {
    try {
      await userService.updateUser(row._id, {
        username: row.username,
        email: row.email,
      });
      editing.value = { id: null, field: null };
      showSuccess("User updated successfully");
      await userStore.fetchUsers();
    } catch {
      showError("Failed to save inline edit");
    }
  }

  // Build update object for patch API (unflatten nested keys)
  function buildRoleUpdate(key: string, value: any) {
    const flatObj = { [key]: value };
    return unflatten(flatObj);
  }

  // Open user detail dialog and fetch details
  async function handleDetail(id: string) {
    try {
      saveId.value = null;
      dialogLoading.value = true;
      showDialog.value = false;
      dialogKey.value++;
      userDetails.value = null;
      const res = await userService.getUserDetails(id);
      handleRole.value = res.role as Role;
      userDetails.value = res as RawUserDetail;
      showDialog.value = true;
      saveId.value = id;
    } catch {
      showError("Failed to fetch user details");
    } finally {
      dialogLoading.value = false;
    }
  }

  // Submit inline edit inside detail dialog
  async function handleInlineEditSubmitDialog(val: any, key: string) {
    if (!userInfo.value) return;
    const userId = saveId.value;
    if (!userId) {
      showError("User ID is not found");
      return;
    }
    try {
      const result = await userStore.updateUserPatch(
        userId,
        buildRoleUpdate(key, val)
      );
      if (result) {
        showSuccess("User updated successfully");
        await userStore.fetchUsers();
      } else {
        showError("Failed to update user");
      }
    } catch (error) {
      if (error instanceof UserStoreError) {
        showError(error.message);
      } else {
        showError("Failed to update user");
      }
    }

    try {
      const res = await userService.getUserDetails(saveId.value as string);
      userDetails.value = res as RawUserDetail;
      console.log("this is res", res);
      await userStore.fetchUsers();
    } catch {
      showError("Failed to fetch user details");
    }
  }

  // Save attendance (student only)
  function onAttendanceSave(
    updatedAttendance: Record<string, AttendanceStatus>
  ) {
    handleInlineEditSubmitDialog(
      updatedAttendance,
      "student_info.attendance_record"
    );
  }

  // Open create user dialog
  const showCreateUserForm = () => {
    showCreateUserDialog.value = true;
  };

  const cancelEditDetail = (key: string) => {
    console.log("cancelEditDetail", key);
  };
  const attendance = computed({
    get(): Record<string, AttendanceStatus> {
      if (
        userDetails.value?.role === Role.STUDENT &&
        userDetails.value.data?.student_info
      ) {
        return userDetails.value.data.student_info.attendance_record ?? {};
      }
      return {};
    },
    set(newVal: Record<string, AttendanceStatus>) {
      if (
        userDetails.value?.role === Role.STUDENT &&
        userDetails.value.data?.student_info
      ) {
        userDetails.value.data.student_info.attendance_record = newVal;
      }
    },
  });

  return {
    showDialog,
    showCreateUserDialog,
    userDetails,
    dialogLoading,
    dialogKey,
    currentPage,
    pageSize,
    hasDraft,
    saveId,
    editing,
    originalValue,
    users,
    roleFields,
    userInfo,
    attendance,
    handleRole,
    cancelEdit,
    handleDelete,
    submitInlineEdit,
    handleDetail,
    handleInlineEditSubmitDialog,
    onAttendanceSave,
    showCreateUserForm,
    cancelEditDetail,
    showInfo,
    showError,
  };
}
