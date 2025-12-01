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

// Element Plus components used in script
import { ElInput, ElOption, ElSelect } from "element-plus";

// --------------------
// Services & Types
// --------------------
import { adminService } from "~/api/admin";
import type {
  AdminSubjectDataDTO,
  AdminSubjectListDTO,
  AdminCreateSubjectDTO,
} from "~/api/admin/subject/dto";
import type { Field } from "~/components/types/form";
import type { ColumnConfig } from "~/components/types/tableEdit";

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
    width: 130,
    align: "center",
    operation: true, // will use #operation slot
  },
]);

/* ---------------------- grade options ---------------------- */

const gradeOptions = ref(
  Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: `Grade ${i + 1}`,
  }))
);

function formatAllowedGrades(levels?: number[]) {
  if (!levels || !levels.length) return "-";
  return levels
    .map(
      (lvl) =>
        gradeOptions.value.find((g) => g.value === lvl)?.label || `Grade ${lvl}`
    )
    .join(", ");
}

/* ---------------------- form fields (SmartFormDialog) ---------------------- */

const subjectFormFields = computed<Field<AdminCreateSubjectDTO>[]>(() => [
  {
    key: "name",
    label: "Name",
    component: ElInput,
    formItemProps: {
      prop: "name",
      label: "Name",
      rules: [
        {
          required: true,
          message: "Name is required",
          trigger: ["blur", "change"],
        },
      ],
    },
    componentProps: {
      placeholder: "Subject name (e.g. Mathematics)",
      clearable: true,
    },
  },
  {
    key: "code",
    label: "Code",
    component: ElInput,
    formItemProps: {
      prop: "code",
      label: "Code",
      rules: [
        {
          required: true,
          message: "Code is required",
          trigger: ["blur", "change"],
        },
      ],
    },
    componentProps: {
      placeholder: "Unique subject code (e.g. MATH101)",
      clearable: true,
    },
  },
  {
    key: "description",
    label: "Description",
    component: ElInput,
    formItemProps: {
      prop: "description",
      label: "Description",
    },
    componentProps: {
      type: "textarea",
      placeholder: "Short description",
      rows: 3,
    },
  },
  {
    key: "allowed_grade_levels",
    label: "Allowed Grade Levels",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      prop: "allowed_grade_levels",
      label: "Allowed Grade Levels",
    },
    componentProps: {
      multiple: true,
      filterable: true,
      clearable: true,
      placeholder: "Select grade levels",
    },
    childComponentProps: {
      options: () => gradeOptions.value,
      valueKey: "value",
      labelKey: "label",
    },
  },
]);

const createDialogWidth = computed(() => "40%");

/* ---------------------- create form state (local) ---------------------- */

const createDialogVisible = ref(false);
const createFormLoading = ref(false);

const createFormData = ref<Partial<AdminCreateSubjectDTO>>({
  name: "",
  code: "",
  description: "",
  allowed_grade_levels: [],
});
const dialogKey = ref(0);

const openCreateDialog = () => {
  createFormData.value = {
    name: "",
    code: "",
    description: "",
    allowed_grade_levels: [],
  };
  dialogKey.value++;
  createDialogVisible.value = true;
};

const handleCancelCreateForm = () => {
  createDialogVisible.value = false;
};

/**
 * This gets the payload emitted from SmartFormDialog,
 * but we also have v-model="createFormData", so they are in sync.
 */
const handleSaveCreateForm = async (
  payload: Partial<AdminCreateSubjectDTO>
) => {
  createFormLoading.value = true;
  try {
    Object.assign(createFormData.value, payload);

    const body: AdminCreateSubjectDTO = {
      name: createFormData.value.name ?? "",
      code: createFormData.value.code ?? "",
      description: createFormData.value.description ?? "",
      allowed_grade_levels: createFormData.value.allowed_grade_levels ?? [],
    };

    await adminApi.subject.createSubject(body);

    await fetchSubjects();
    createFormData.value = {
      name: "",
      code: "",
      description: "",
      allowed_grade_levels: [],
    };
    createDialogVisible.value = false;
    dialogKey.value++;
  } catch (err) {
    console.error("Failed to create subject:", err);
  } finally {
    createFormLoading.value = false;
  }
};

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

/* ---------------------- basic row actions (stubs for now) ---------------------- */

const handleEditSubject = (row: AdminSubjectDataDTO) => {
  console.log("Edit subject (not implemented yet):", row);
};

const handleDeleteSubject = async (row: AdminSubjectDataDTO) => {
  console.log("Delete subject (not implemented yet):", row);
  // Example:
  // await adminApi.subject.deleteSubject(row.id);
  // await fetchSubjects();
};

/* ---------------------- lifecycle ---------------------- */

onMounted(() => {
  fetchSubjects();
});
</script>

<template>
  <el-row justify="space-between">
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
      :smart-props="{ border: true, stripe: true, class: 'm-2 m m-5' }"
    >
      <!-- Description column -->
      <template #description="{ row }">
        <span>{{ row.description || "-" }}</span>
      </template>

      <!-- Allowed Grades column -->
      <template #allowedGrades="{ row }">
        <span>{{ formatAllowedGrades(row.allowed_grade_levels) }}</span>
      </template>

      <!-- Status / operation column -->
      <template #operation="{ row }">
        <el-switch
          v-model="row.is_active"
          :loading="statusLoading[row.id]"
          @change="() => toggleSubjectActive(row)"
        />
      </template>
    </SmartTable>
  </ErrorBoundary>

  <!-- CREATE DIALOG -->
  <ErrorBoundary>
    <SmartFormDialog
      :key="dialogKey"
      v-model:visible="createDialogVisible"
      v-model="createFormData"
      :fields="subjectFormFields"
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
</style>
