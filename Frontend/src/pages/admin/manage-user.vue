<!-- ~/pages/admin/users/index.vue -->
<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, type Ref } from "vue";
import { ElPagination } from "element-plus";

// --------------------
// Page Meta
// --------------------
definePageMeta({
  layout: "admin",
});

// --------------------
// Base Components
// --------------------
import ActionButtons from "~/components/Button/ActionButtons.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import ErrorBoundary from "~/components/Error/ErrorBoundary.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";

// --------------------
// Composables
// --------------------
import { useDialogDynamicWidth } from "~/composables/useDialogDynamicWidth";
import { usePaginatedFetch } from "~/composables/usePaginatedFetch";
import { useInlineEdit } from "~/composables/useInlineEdit";
import { useHeaderState } from "~/composables/useHeaderState";

// --------------------
// Schemas & Registry
// --------------------
import {
  adminFormRegistryCreate,
  adminFormRegistryEdit,
} from "~/form-system/register/admin";

// --------------------
// Dynamic forms
// --------------------
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
  useInlineEditService,
} from "~/form-system/useDynamicForm.ts/useAdminForms";

// --------------------
// Columns & Constants
// --------------------
import { userColumns } from "~/modules/tables/columns/admin/userColumns";
import {
  roleOptions,
  roleStaffOptions,
  roleUserOptions,
} from "~/utils/constants/roles";

// --------------------
// API & Types
// --------------------
import type {
  AdminGetUserItemData,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";
import { Role } from "~/api/types/enums/role.enum";

// --------------------
// Services
// --------------------
import { adminService } from "~/api/admin";

/* ----------------------------- types ----------------------------- */
type CreateMode = "USER" | "STAFF";
type EditMode = "USER" | "STAFF" | "STUDENT";

/* --------------------------- reactive ---------------------------- */
const isStaffMode = ref<boolean | undefined>(undefined);
const selectedRoles = ref<Role[]>([Role.STUDENT]);
const selectedFormCreate = ref<CreateMode>("USER");
const selectedFormEdit = ref<EditMode>("USER");
const editFormDataKey = ref("");
const createFormKey = ref(0);

/* ---------------------------- create form -------------------------- */
const {
  formDialogVisible: createFormVisible,
  formData: createFormData,
  schema: createFormSchema,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
  openForm: openCreateForm,
  loading: createFormLoading,
  resetFormData,
} = useDynamicCreateFormReactive(selectedFormCreate);

const handleOpenCreateForm = async () => {
  selectedFormCreate.value = isStaffMode.value ? "STAFF" : "USER";
  createFormKey.value++;
  await openCreateForm();
};

const handleSaveCreateForm = async (payload: Partial<any>) => {
  await saveCreateForm(payload);
  await fetchPage(currentPage.value);
};

const handleCancelCreateForm = () => {
  cancelCreateForm();
};

watch(
  () => selectedFormCreate.value,
  () => {
    resetFormData();
  }
);

/* ---------------------------- edit form -------------------------- */
const {
  formDialogVisible: editFormVisible,
  formData: editFormData,
  schema: editFormSchema,
  openForm: openEditForm,
  saveForm: saveEditForm,
  cancelForm: cancelEditForm,
  loading: editFormLoading,
} = useDynamicEditFormReactive(selectedFormEdit);

const detailLoading = ref<Record<string | number, boolean>>({});

const handleOpenEditForm = async (row: AdminGetUserItemData) => {
  try {
    detailLoading.value[row.id] = true;

    selectedFormEdit.value =
      row.role === "student"
        ? "STUDENT"
        : row.role === "academic" || row.role === "teacher"
        ? "STAFF"
        : "USER";

    editFormDataKey.value = row.id?.toString() ?? "new";

    await nextTick();
    await openEditForm(row.id);
  } catch (error) {
    console.error("Failed to open edit form:", error);
  } finally {
    detailLoading.value[row.id] = false;
  }
};

const handleSaveEditForm = (payload: Partial<any>) => {
  saveEditForm(payload);
};

const handleCancelEditForm = () => {
  cancelEditForm();
};

/* ---------------------------- inline edit ------------------------ */
const {
  data,
  save,
  cancel,
  remove: removeUser,
  deleteLoading,
  inlineEditLoading,
  setData,
  autoSave,
  getPreviousValue,
  revertField,
} = useInlineEdit<AdminGetUserItemData, AdminUpdateUser>(
  [],
  useInlineEditService("USER")
);

const adminApiService = adminService();

/* ---------------------------- pagination ------------------------- */
const fetchUsers = async (
  rolesArray: Role[] | Ref<Role[]>,
  page: number,
  pageSize: number
) => {
  const roles = Array.isArray(rolesArray) ? rolesArray : rolesArray.value;
  const res = await adminApiService.user.getUserPage(roles, page, pageSize);

  const items = res?.users ?? [];
  const total = res?.total ?? 0;
  setData(items);

  return {
    items,
    total,
  };
};

const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
} = usePaginatedFetch(fetchUsers, 1, 15, selectedRoles);

/* ----------------------------- misc ------------------------------ */
const currentRoleOptions = computed(() => {
  if (isStaffMode.value === true) return roleStaffOptions;
  if (isStaffMode.value === false) return roleUserOptions;
  return roleOptions;
});

watch(selectedRoles, () => fetchPage(1), { deep: true });

watch(isStaffMode, (mode) => {
  if (mode === true) {
    selectedFormCreate.value = "STAFF";
    selectedRoles.value = roleStaffOptions.map((r) => r.value);
  } else if (mode === false) {
    selectedFormCreate.value = "USER";
    selectedRoles.value = roleUserOptions.map((r) => r.value);
  } else {
    selectedFormCreate.value = "USER";
    selectedRoles.value = roleOptions.map((r) => r.value);
  }
  fetchPage(1);
});

/* --------------------------- computed -------------------------- */

const schemaCreate = computed(
  () => adminFormRegistryCreate[selectedFormCreate.value].schema ?? []
);
const schemaEdit = computed(
  () => adminFormRegistryEdit[selectedFormEdit.value].schema ?? []
);

const createWidthRef = useDialogDynamicWidth(schemaCreate.value);
const dynamicWidthCreate = computed(() => createWidthRef.value);

const editWidthRef = useDialogDynamicWidth(schemaEdit.value);
const dynamicWidthEdit = computed(() => editWidthRef.value);

/* ----------------------------- create form width ------------------------------ */

const createDialogWidth = computed(() => {
  if (selectedFormCreate.value === "STAFF") return "65%";
  if (selectedFormCreate.value === "USER") return "40%";
  return dynamicWidthCreate.value;
});

/* ----------------------------- edit form width ------------------------------ */

const editDialogWidth = computed(() => {
  if (selectedFormEdit.value === "STAFF") return "60%";
  if (selectedFormEdit.value === "STUDENT") return "70%";
  return dynamicWidthEdit.value;
});

const handleRevertField = (
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) => {
  revertField(row, field);
};

onMounted(() => {
  selectedRoles.value = [
    Role.STUDENT,
    Role.TEACHER,
    Role.ACADEMIC,
    Role.PARENT,
  ];
});

function handleSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  save(row, field as keyof AdminUpdateUser).catch((err) => {
    console.error(err);
  });
}

function handleAutoSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  autoSave(row, field as keyof AdminUpdateUser).catch((err) => {
    console.error(err);
  });
}

/* --------------------------- header stats -------------------------- */
const totalUsers = computed(() => totalRows.value ?? 0);

const { headerState: userHeaderStats } = useHeaderState({
  items: [
    {
      key: "users",
      getValue: () => totalUsers.value,
      singular: "user",
      plural: "users",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "roles",
      getValue: () => selectedRoles.value.length,
      singular: "role",
      plural: "roles",
      suffix: "selected",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- OVERVIEW HEADER -->
    <OverviewHeader
      title="Users"
      description="Manage all users, roles and staff accounts."
      :loading="fetchLoading"
      :showRefresh="true"
      :stats="userHeaderStats"
      @refresh="() => fetchPage(currentPage)"
    >
      <!-- Filters: mode + roles -->
      <template #filters>
        <div class="flex flex-col gap-2 w-full">
          <div
            class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
          >
            <!-- Left: Staff/User mode -->
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500">Mode:</span>
              <el-radio-group v-model="isStaffMode" size="small">
                <el-radio :value="undefined">Default</el-radio>
                <el-radio :value="false">User</el-radio>
                <el-radio :value="true">Staff</el-radio>
              </el-radio-group>
            </div>

            <!-- Right: Role multi-select -->
            <div class="flex items-center gap-2 sm:justify-end">
              <span class="text-xs text-gray-500">Roles:</span>
              <el-select
                v-model="selectedRoles"
                multiple
                filterable
                clearable
                placeholder="Select roles"
                style="min-width: 260px; max-width: 320px"
                class="header-roles-select"
              >
                <el-option
                  v-for="opt in currentRoleOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </div>
          </div>
        </div>
      </template>

      <!-- Actions: Refresh + Add -->
      <template #actions>
        <BaseButton
          plain
          :loading="fetchLoading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="fetchPage(currentPage)"
        >
          Refresh
        </BaseButton>

        <BaseButton
          v-if="isStaffMode !== undefined"
          type="primary"
          @click="handleOpenCreateForm"
        >
          Add {{ isStaffMode ? "Staff" : "User" }}
        </BaseButton>
      </template>
    </OverviewHeader>

    <!-- TABLE + INLINE EDIT -->
    <ErrorBoundary>
      <el-card>
        <template #default>
          <SmartTable
            :data="data"
            :columns="userColumns"
            :loading="fetchLoading"
            @save="handleSaveWrapper"
            @cancel="cancel"
            @auto-save="handleAutoSaveWrapper"
          >
            <template #operation="{ row }">
              <ActionButtons
                :rowId="row.id"
                :role="row.role"
                :detailContent="`Edit ${
                  row.role.charAt(0).toUpperCase() + row.role.slice(1)
                } details`"
                :deleteContent="`Delete ${
                  row.role.charAt(0).toUpperCase() + row.role.slice(1)
                }`"
                :detailLoading="
                  inlineEditLoading[row.id] ?? detailLoading[row.id] ?? false
                "
                :deleteLoading="
                  inlineEditLoading[row.id] ?? deleteLoading[row.id] ?? false
                "
                @detail="handleOpenEditForm(row)"
                @delete="removeUser(row)"
              />
            </template>

            <template #controlsSlot="{ row, field }">
              <el-tooltip
                :content="`Previous: ${getPreviousValue(row, field)}`"
                placement="top"
              >
                <el-icon
                  class="cursor-pointer"
                  @click="handleRevertField(row, field)"
                >
                  <Refresh />
                </el-icon>
              </el-tooltip>
            </template>
          </SmartTable>
        </template>
      </el-card>
    </ErrorBoundary>

    <!-- PAGINATION -->
    <ErrorBoundary>
      <el-row v-if="totalRows > 0" justify="end" class="mt-6">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalRows"
          :page-sizes="[10, 15, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="goPage"
          @size-change="
            (size: number) => {
              pageSize = size;
              fetchPage(1);
            }
          "
        />
      </el-row>
    </ErrorBoundary>

    <!-- CREATE DIALOG -->
    <ErrorBoundary>
      <SmartFormDialog
        :key="`${selectedFormCreate}-${createFormKey}`"
        v-model:visible="createFormVisible"
        v-model="createFormData"
        :fields="createFormSchema"
        :title="`Add ${isStaffMode ? 'Staff' : 'User'}`"
        :loading="createFormLoading"
        @save="handleSaveCreateForm"
        @cancel="handleCancelCreateForm"
        :useElForm="true"
        :width="createDialogWidth"
      />
    </ErrorBoundary>

    <!-- EDIT DIALOG -->
    <SmartFormDialog
      :key="`${selectedFormEdit}-${editFormDataKey}`"
      v-model:visible="editFormVisible"
      v-model="editFormData"
      :fields="editFormSchema"
      title="Edit"
      :loading="editFormLoading"
      @save="handleSaveEditForm"
      @cancel="handleCancelEditForm"
      :useElForm="true"
      :width="editDialogWidth"
    />
  </div>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
