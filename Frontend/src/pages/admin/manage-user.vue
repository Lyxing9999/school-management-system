<script setup lang="ts">
import {
  ref,
  computed,
  watch,
  nextTick,
  onMounted,
  onBeforeUnmount,
} from "vue";
import type { Status } from "~/api/types/enums/status.enum";
import { Role } from "~/api/types/enums/role.enum";
import debounce from "lodash-es/debounce";
// --------------------
// Page Meta
// --------------------
definePageMeta({ layout: "admin" });

// --------------------
// Base Components
// --------------------
import ActionButtons from "~/components/Button/ActionButtons.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import StaffModePills from "~/components/filters/StaffModePills.vue";
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

// --------------------
// Services
// --------------------
import { adminService } from "~/api/admin";

/* ----------------------------- types ----------------------------- */
type CreateMode = "STAFF" | "STUDENT";
type EditMode = "STAFF" | "STUDENT";
type StaffMode = "default" | "user" | "staff";

/* --------------------------- state (filters) ---------------------------- */
const q = ref<string>(""); // search
const staffMode = ref<StaffMode>("default"); // tri-state, safe
const selectedRoles = ref<Role[]>([]);

/* --------------------------- derived role options ---------------------------- */
const currentRoleOptions = computed(() => {
  if (staffMode.value === "staff") return roleStaffOptions;
  if (staffMode.value === "user") return roleUserOptions;
  return roleOptions;
});

/* --------------------------- helpers ---------------------------- */
function rolesFromMode(mode: StaffMode): Role[] {
  if (mode === "staff") return roleStaffOptions.map((r) => r.value);
  if (mode === "user") return roleUserOptions.map((r) => r.value);
  return roleOptions.map((r) => r.value);
}

function normalizeSelectedRoles() {
  // Ensure selectedRoles is subset of currentRoleOptions
  const allowed = new Set(currentRoleOptions.value.map((o) => o.value));
  const filtered = selectedRoles.value.filter((r) => allowed.has(r));

  // If empty, default to all allowed roles for that mode
  selectedRoles.value = filtered.length
    ? filtered
    : rolesFromMode(staffMode.value);
}

/* --------------------------- init defaults ---------------------------- */
onMounted(() => {
  // Default to a reasonable initial set (your original behavior)
  // You can change this to rolesFromMode("default") if you want "All roles"
  selectedRoles.value = [
    Role.STUDENT,
    Role.TEACHER,
    Role.ACADEMIC,
    Role.PARENT,
  ];
  normalizeSelectedRoles();
});

/* ---------------------------- create form -------------------------- */
const selectedFormCreate = ref<CreateMode>("STUDENT");
const createFormKey = ref(0);

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

watch(
  () => selectedFormCreate.value,
  () => resetFormData()
);

const handleOpenCreateForm = async () => {
  selectedFormCreate.value = staffMode.value === "staff" ? "STAFF" : "STUDENT";
  createFormKey.value++;
  await openCreateForm();
};

const handleSaveCreateForm = async (payload: Partial<any>) => {
  await saveCreateForm(payload);
  await fetchPage(currentPage.value);
};

const handleCancelCreateForm = () => cancelCreateForm();

/* ---------------------------- edit form -------------------------- */
const selectedFormEdit = ref<EditMode>("STUDENT");
const editFormDataKey = ref("");
const detailLoading = ref<Record<string | number, boolean>>({});

const {
  formDialogVisible: editFormVisible,
  formData: editFormData,
  schema: editFormSchema,
  openForm: openEditForm,
  saveForm: saveEditForm,
  cancelForm: cancelEditForm,
  loading: editFormLoading,
} = useDynamicEditFormReactive(selectedFormEdit);

const handleOpenEditForm = async (row: AdminGetUserItemData) => {
  try {
    detailLoading.value[row.id] = true;

    selectedFormEdit.value = row.role === "student" ? "STUDENT" : "STAFF";

    editFormDataKey.value = row.id?.toString() ?? "new";

    await nextTick();
    await openEditForm(row.id);
  } finally {
    detailLoading.value[row.id] = false;
  }
};

const handleSaveEditForm = (payload: Partial<any>) => saveEditForm(payload);
const handleCancelEditForm = () => cancelEditForm();

/* ---------------------------- inline edit ------------------------ */
const {
  data,
  save,
  cancel,
  remove: removeUser,
  deleteLoading,
  inlineEditLoading,
  autoSave,
  getPreviousValue,
  revertField,
  setData: setInlineData,
} = useInlineEdit<AdminGetUserItemData, AdminUpdateUser>(
  [],
  useInlineEditService("USER")
);

const adminApiService = adminService();

/* ---------------------------- pagination / fetch ------------------------- */
/**
 * NOTE: Your current API call doesn't accept q / staffMode. For now:
 * - We fetch by roles (server-side)
 * - We apply q as client-side filter (optional; remove if you add server-side search)
 *
 * If you have an endpoint that supports q/staffMode, replace this with:
 * getUserPage({ roles, q, isStaff, page, pageSize })
 */
const filters = computed(() => ({
  roles: selectedRoles.value,
  q: q.value,
}));

const fetchUsers = async (
  filter: { roles: Role[]; q: string },
  page: number,
  pageSize: number,
  signal?: AbortSignal
) => {
  const res = await adminApiService.user.getUserPage(
    filter.roles,
    page,
    pageSize,
    filter.q,
    signal
  );

  const items = res?.users ?? [];
  const total = res?.total ?? 0;

  setInlineData(items);
  return { items, total };
};
const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
  setPageSize,
} = usePaginatedFetch(fetchUsers, 1, 15, filters);
/* --------------------------- single watcher: filters -> refresh -------------------------- */
const debouncedFetch = debounce(() => fetchPage(1), 300);
const syncingRolesFromMode = ref(false);
// Mode / roles: fetch immediately (no debounce)
watch(
  () => staffMode.value,
  async (mode, prevMode) => {
    if (mode === prevMode) return;

    // keep your create-form mode behavior
    selectedFormCreate.value = mode === "staff" ? "STAFF" : "STUDENT";

    // ✅ Force roles based on mode
    syncingRolesFromMode.value = true;
    selectedRoles.value = rolesFromMode(mode); // default => ALL roles
    await nextTick();
    syncingRolesFromMode.value = false;

    // fetch immediately
    debouncedFetch.cancel();
    await fetchPage(1);
  }
);

watch(
  selectedRoles,
  async () => {
    // avoid double fetch caused by the mode watcher setting selectedRoles
    if (syncingRolesFromMode.value) return;

    debouncedFetch.cancel();
    await fetchPage(1);
  },
  { deep: true }
);

// Search stays debounced
watch(
  () => q.value,
  () => debouncedFetch()
);
/* --------------------------- reset -------------------------- */
const isDirty = computed(() => {
  const defaultRoles = rolesFromMode(staffMode.value);
  const sameRoles =
    selectedRoles.value.length === defaultRoles.length &&
    selectedRoles.value.every((r) => defaultRoles.includes(r));

  return q.value.trim() !== "" || staffMode.value !== "default" || !sameRoles;
});

function resetAll() {
  q.value = "";
  staffMode.value = "default";
  selectedRoles.value = rolesFromMode("default");
}

/* --------------------------- computed: dialog widths -------------------------- */
const schemaCreate = computed(
  () => adminFormRegistryCreate[selectedFormCreate.value].schema ?? []
);
const schemaEdit = computed(
  () => adminFormRegistryEdit[selectedFormEdit.value].schema ?? []
);

const createWidthRef = useDialogDynamicWidth(schemaCreate.value);
const editWidthRef = useDialogDynamicWidth(schemaEdit.value);

const createDialogWidth = computed(() => {
  if (selectedFormCreate.value === "STAFF") return "65%";
  if (selectedFormCreate.value === "STUDENT") return "80%";
  return createWidthRef.value;
});

const editDialogWidth = computed(() => {
  if (selectedFormEdit.value === "STAFF") return "60%";
  if (selectedFormEdit.value === "STUDENT") return "70%";
  return editWidthRef.value;
});

/* --------------------------- save wrappers -------------------------- */
function handleSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  save(row, field as keyof AdminUpdateUser).catch(() => {});
}

function handleAutoSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  autoSave(row, field as keyof AdminUpdateUser).catch(() => {});
}

function handleRevertField(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  revertField(row, field);
}

/* --------------------------- status edit -------------------------- */
const editingStatusRowId = ref<string | null>(null);
const statusDraft = ref<"active" | "inactive" | "suspended">("active");
const statusSaving = ref<Record<string, boolean>>({});

const statusTagType = (s?: string) => {
  if (s === "active") return "success";
  if (s === "inactive") return "warning";
  if (s === "suspended") return "danger";
  return "info";
};

function formatStatusLabel(status: string) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

const startEditStatus = (row: any) => {
  if (row.deleted) return;
  editingStatusRowId.value = row.id;
  statusDraft.value = (row.status ?? "active") as any;
};

const cancelEditStatus = () => {
  editingStatusRowId.value = null;
};

const saveStatus = async (row: any, nextStatus: Status) => {
  const prev = (row.status ?? "active") as Status;
  if (prev === nextStatus) return cancelEditStatus();

  statusSaving.value[row.id] = true;
  row.status = nextStatus;

  try {
    await adminApiService.user.setUserStatus(row.id, nextStatus);
  } catch (e) {
    row.status = prev;
  } finally {
    statusSaving.value[row.id] = false;
    cancelEditStatus();
  }
};

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
      :show-search="true"
      v-model:searchModelValue="q"
      search-placeholder="Search by username or email..."
      :show-reset="true"
      :reset-disabled="!isDirty"
      @refresh="() => fetchPage(currentPage)"
      @reset="resetAll"
    >
      <template #filters>
        <el-row :gutter="12" align="middle" class="w-full">
          <!-- Left: Mode -->
          <el-col :span="12" justify="start">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 whitespace-nowrap">Mode:</span>
              <StaffModePills v-model="staffMode" :disabled="fetchLoading" />
            </div>
          </el-col>

          <!-- Right: Roles (force to the far right on sm+) -->
          <el-col :span="12">
            <div
              class="flex items-center gap-2 justify-start sm:justify-end w-full"
            >
              <span class="text-xs text-gray-500 whitespace-nowrap"
                >Roles:</span
              >

              <el-select
                v-model="selectedRoles"
                multiple
                filterable
                clearable
                placeholder="Select roles"
                class="w-full sm:w-[360px]"
              >
                <el-option
                  v-for="opt in currentRoleOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </div>
          </el-col>
        </el-row>
      </template>

      <template #actions>
        <BaseButton
          plain
          :loading="fetchLoading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="fetchPage(currentPage)"
        >
          Refresh
        </BaseButton>

        <BaseButton type="primary" @click="handleOpenCreateForm">
          Add {{ staffMode === "staff" ? "Staff" : "Student" }}
        </BaseButton>
      </template>
    </OverviewHeader>

    <!-- TABLE -->
    <el-card>
      <SmartTable
        :data="data"
        :columns="userColumns"
        :loading="fetchLoading"
        @save="handleSaveWrapper"
        @cancel="cancel"
        @auto-save="handleAutoSaveWrapper"
      >
        <template #status="{ row }">
          <div class="flex items-center gap-2">
            <el-tooltip
              content="Click to change status"
              placement="top"
              :show-after="200"
            >
              <div class="status-slot">
                <transition name="fade-scale" mode="out-in">
                  <el-tag
                    v-if="editingStatusRowId !== row.id"
                    :key="`view-${row.id}`"
                    :type="statusTagType(row.status ?? 'active')"
                    effect="light"
                    round
                    class="status-pill cursor-pointer select-none"
                    @click="startEditStatus(row)"
                  >
                    {{ formatStatusLabel(row.status ?? "active") }}
                  </el-tag>

                  <el-select
                    v-else
                    :key="`edit-${row.id}`"
                    v-model="statusDraft"
                    size="small"
                    class="status-select"
                    @change="(val) => saveStatus(row, val)"
                    @keydown.esc.prevent="cancelEditStatus()"
                    @visible-change="
                      (open) => {
                        if (!open) cancelEditStatus();
                      }
                    "
                  >
                    <el-option label="Active" value="active" />
                    <el-option label="Inactive" value="inactive" />
                    <el-option label="Suspended" value="suspended" />
                  </el-select>
                </transition>
              </div>
            </el-tooltip>
          </div>
        </template>

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
    </el-card>

    <!-- PAGINATION -->
    <el-row v-if="totalRows > 0" justify="end" class="mt-6">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="totalRows"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="goPage"
        @size-change="(size: number) => setPageSize(size)"
      />
    </el-row>

    <!-- CREATE DIALOG -->
    <SmartFormDialog
      :key="`${selectedFormCreate}-${createFormKey}`"
      v-model:visible="createFormVisible"
      v-model="createFormData"
      :fields="createFormSchema"
      :title="`Add ${staffMode === 'staff' ? 'Staff' : 'User'}`"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createDialogWidth"
    />

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
.status-slot {
  width: 100px;
  display: inline-flex;
  align-items: center;
}
.status-pill {
  height: 28px;
  line-height: 28px;
  padding: 0 10px;
  border-radius: 9999px;
}
.status-select {
  width: 100px;
}
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: opacity 140ms ease, transform 160ms ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: translateY(2px) scale(0.98);
}
</style>
