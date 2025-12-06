<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

definePageMeta({
  layout: "admin",
});

// --------------------
// Base Components
// --------------------
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";

// Element Plus
import { ElMessage, ElRadioGroup, ElRadioButton, ElSwitch } from "element-plus";

// --------------------
// Services & Types
// --------------------
import { adminService } from "~/api/admin";
import type {
  AdminSubjectDataDTO,
  AdminSubjectListDTO,
  AdminCreateSubject,
} from "~/api/admin/subject/subject.dto";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { Field } from "~/components/types/form";

// For grade labels in table
import { gradeOptions } from "~/modules/forms/admin/subject/subject.schema";

// Dynamic form system
import { useDynamicCreateFormReactive } from "~/form-system/useDynamicForm.ts/useAdminForms";

const adminApi = adminService();

/* ---------------------- table state ---------------------- */

const subjects = ref<AdminSubjectDataDTO[]>([]);
const tableLoading = ref(false);

const activeFilter = ref<"all" | "active" | "inactive">("all");

const filteredSubjects = computed(() => {
  if (activeFilter.value === "all") return subjects.value;
  if (activeFilter.value === "active") {
    return subjects.value.filter((s) => s.is_active);
  }
  return subjects.value.filter((s) => !s.is_active);
});

/* ---------------------- table columns for SmartTable ---------------------- */

const subjectColumns = computed<ColumnConfig<AdminSubjectDataDTO>[]>(() => [
  {
    field: "name",
    label: "Name",
    minWidth: 140,
  },
  {
    field: "code",
    label: "Code",
    minWidth: 120,
  },
  {
    field: "description",
    label: "Description",
    minWidth: 180,
    useSlots: true,
    slotName: "description",
  },
  {
    field: "allowed_grade_levels",
    label: "Allowed Grades",
    minWidth: 160,
    useSlots: true,
    slotName: "allowedGrades",
  },
  {
    field: "is_active",
    label: "Status",
    align: "center",
    operation: true, // use #operation slot
  },
]);

/* ---------------------- grade options display helper ---------------------- */

function formatAllowedGrades(levels?: number[]) {
  if (!levels || !levels.length) return "-";
  return levels
    .map(
      (lvl) =>
        gradeOptions.value.find((g) => g.value === lvl)?.label || `Grade ${lvl}`
    )
    .join(", ");
}

/* ---------------------- CREATE FORM (dynamic) ---------------------- */

// IMPORTANT: correct mode key must match your registry ("SUBJECT")
const createMode = ref<"SUBJECT">("SUBJECT");

const {
  formDialogVisible: createFormVisible,
  formData: createFormData,
  schema: baseCreateFormSchema,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
  openForm: openCreateForm,
  loading: createFormLoading,
} = useDynamicCreateFormReactive(createMode);

const createDialogWidth = computed(() => "40%");
const createDialogKey = ref(0);

async function openCreateDialog() {
  // This will init formData using getSubjectFormData() from registry
  createDialogKey.value++;
  await openCreateForm();
}

async function handleSaveCreateForm(payload: Partial<AdminCreateSubject>) {
  await saveCreateForm(payload);
  await fetchSubjects();
}

function handleCancelCreateForm() {
  cancelCreateForm();
}

/* ---------------------- actions: fetch + toggle ---------------------- */

async function fetchSubjects() {
  tableLoading.value = true;
  try {
    const res: AdminSubjectListDTO | undefined =
      await adminApi.subject.getSubjects();
    subjects.value = res?.items ?? [];
  } catch (err) {
    console.error("Failed to fetch subjects", err);
  } finally {
    tableLoading.value = false;
  }
}

const statusLoading = ref<Record<string, boolean>>({});

async function toggleSubjectActive(row: AdminSubjectDataDTO) {
  const id = row.id;
  const previous = row.is_active;

  statusLoading.value[id] = true;

  try {
    if (row.is_active) {
      await adminApi.subject.activateSubject(id);
    } else {
      await adminApi.subject.deactivateSubject(id);
    }
    await fetchSubjects();
  } catch (err) {
    console.error("Failed to toggle subject active state", err);
    row.is_active = previous;
  } finally {
    statusLoading.value[id] = false;
  }
}

/* ---------------------- lifecycle ---------------------- */

onMounted(() => {
  fetchSubjects();
});
</script>

<template>
  <el-row justify="space-between" class="m-4">
    <el-col :span="12">
      <BaseButton type="default" :loading="tableLoading" @click="fetchSubjects">
        Refresh
      </BaseButton>

      <BaseButton type="primary" class="ml-2" @click="openCreateDialog">
        Add Subject
      </BaseButton>
    </el-col>

    <el-col :span="12" class="text-right">
      <el-radio-group v-model="activeFilter">
        <el-radio-button label="all">All</el-radio-button>
        <el-radio-button label="active">Active</el-radio-button>
        <el-radio-button label="inactive">Inactive</el-radio-button>
      </el-radio-group>
    </el-col>
  </el-row>

  <ErrorBoundary>
    <SmartTable
      :data="filteredSubjects"
      :columns="subjectColumns"
      :loading="tableLoading"
    >
      <!-- Description column -->
      <template #description="{ row }">
        <div class="description-cell">
          <span
            v-if="row.description"
            class="description-text"
            :title="row.description"
          >
            {{ row.description }}
          </span>

          <span v-else class="description-empty">
            <span>No description</span>
          </span>
        </div>
      </template>

      <!-- Allowed Grades column -->
      <template #allowedGrades="{ row }">
        <span>{{ formatAllowedGrades(row.allowed_grade_levels) }}</span>
      </template>

      <!-- Status / operation column -->
      <template #operation="{ row }">
        <ElSwitch
          v-model="row.is_active"
          :loading="statusLoading[row.id]"
          @change="() => toggleSubjectActive(row)"
        />
      </template>
    </SmartTable>
  </ErrorBoundary>

  <!-- CREATE SUBJECT DIALOG (SmartFormDialog + form-system) -->
  <ErrorBoundary>
    <SmartFormDialog
      :key="createDialogKey"
      v-model:visible="createFormVisible"
      v-model="createFormData"
      :fields="baseCreateFormSchema"
      title="Add Subject"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createDialogWidth"
    />
  </ErrorBoundary>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}

.description-cell {
  display: flex;
  align-items: center;
  max-width: 260px;
}

.description-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.description-empty {
  font-size: 12px;
  color: #9ca3af;
  font-style: italic;
}
</style>
