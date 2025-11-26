<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

definePageMeta({
  layout: "admin",
});

// --------------------
// Base Components
// --------------------
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";

// Element Plus
import { ElInput, ElOption, ElSelect, ElSwitch } from "element-plus";

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

/* ---------------------- grade options ---------------------- */

const gradeOptions = ref(
  Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: `Grade ${i + 1}`,
  }))
);

/* ---------------------- columns ---------------------- */

const subjectColumns = computed(
  () =>
    [
      {
        label: "Name",
        field: "name",
        align: "left",
        minWidth: "100px",
      },
      {
        label: "Code",
        field: "code",
        minWidth: "100px",
      },
      {
        label: "Description",
        field: "description",
        minWidth: "100px",
      },
      {
        label: "Allowed Grades",
        field: "allowed_grade_levels",
        minWidth: "100px",
      },
      {
        label: "Status",
        field: "active",
        align: "center",
        component: ElSwitch,
        componentProps: {
          disabled: true,
        },
        width: "120px",
        inlineEditActive: true,
      },
      {
        label: "Actions",
        slotName: "operation",
        operation: true,
        fixed: "right",
        width: "150",
        align: "center",
      },
    ] as const
);

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

const openCreateDialog = () => {
  createFormData.value = {
    name: "",
    code: "",
    description: "",
    allowed_grade_levels: [],
  };
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
    // merge payload into createFormData just to be safe
    Object.assign(createFormData.value, payload);

    const body: AdminCreateSubjectDTO = {
      name: createFormData.value.name ?? "",
      code: createFormData.value.code ?? "",
      description: createFormData.value.description ?? "",
      allowed_grade_levels: createFormData.value.allowed_grade_levels ?? [],
    };

    await adminApi.subject.createSubject(body);

    await fetchSubjects();
    createDialogVisible.value = false;
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

async function toggleSubjectActive(row: AdminSubjectDataDTO) {
  try {
    if (row.is_active) {
      await adminApi.subject.deactivateSubject(row.id);
    } else {
      await adminApi.subject.activateSubject(row.id);
    }
    await fetchSubjects();
  } catch (err) {
    console.error("Failed to toggle subject active state", err);
  }
}

/* ---------------------- lifecycle ---------------------- */

onMounted(() => {
  fetchSubjects();
});
</script>

<template>
  <el-row class="m-2" justify="space-between">
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
      <template #operation="{ row }">
        <BaseButton
          size="small"
          :type="row.is_active ? 'danger' : 'success'"
          @click="toggleSubjectActive(row)"
        >
          {{ row.is_active ? "Deactivate" : "Activate" }}
        </BaseButton>
      </template>
    </SmartTable>
  </ErrorBoundary>

  <!-- CREATE DIALOG -->
  <ErrorBoundary>
    <SmartFormDialog
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
