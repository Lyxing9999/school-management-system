<script setup lang="ts">
import { ref, computed, onMounted, h, nextTick } from "vue";

definePageMeta({ layout: "admin" });

// Base components
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";
import StudentSelect from "~/components/Selects/StudentSelect.vue";

// Element Plus
import {
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElMessageBox,
  ElMessage,
  ElRadioGroup,
  ElRadioButton,
} from "element-plus";

// Services & types
import { adminService } from "~/api/admin";
import type {
  AdminCreateClassDTO,
  AdminClassDataDTO,
  AdminClassListDTO,
} from "~/api/admin/class/dto";

const adminApi = adminService();
/* ---------------------- table state ---------------------- */

const classes = ref<AdminClassDataDTO[]>([]);
const tableLoading = ref(false);
const showDeleted = ref<"all" | "active" | "deleted">("all");

// decorate with counts
const displayClasses = computed(() =>
  classes.value.map((c) => ({
    ...c,
    student_count: c.student_ids?.length ?? 0,
    subject_count: c.subject_ids?.length ?? 0,
  }))
);

const filteredClasses = computed(() => {
  if (showDeleted.value === "all") return displayClasses.value;
  if (showDeleted.value === "deleted") {
    return displayClasses.value.filter((c) => c.deleted);
  }
  return displayClasses.value.filter((c) => !c.deleted);
});

/* ---------------------- subject options ---------------------- */

const subjectOptions = ref<{ value: string; label: string }[]>([]);
const subjectOptionsLoading = ref(false);

async function fetchSubjectOptions() {
  if (subjectOptions.value.length > 0) return;
  subjectOptionsLoading.value = true;
  try {
    const res = await adminApi.subject.getSubjects();
    const items = res?.items ?? [];
    subjectOptions.value = items.map((s) => ({
      value: s.id,
      label: `${s.name} (${s.code})`,
    }));
  } catch (err) {
    console.error("Failed to load subject options", err);
  } finally {
    subjectOptionsLoading.value = false;
  }
}

/* ---------------------- columns (SmartTable) ---------------------- */

const classColumns = computed(() => [
  {
    label: "Name",
    field: "name",
    align: "left",
    minWidth: "160px",
  },
  {
    label: "Teacher",
    field: "teacher_id",
    align: "left",
    minWidth: "160px",
    render: (row: AdminClassDataDTO) =>
      h("span", row.teacher_name || "No teacher"),
  },
  {
    label: "Students",
    field: "student_ids",
    align: "center",
    width: "110px",
    render: (row: AdminClassDataDTO) =>
      h("span", (row.student_ids?.length ?? 0).toString()),
  },
  {
    label: "Subjects",
    field: "subject_ids",
    align: "center",
    width: "110px",
    render: (row: AdminClassDataDTO) =>
      h("span", (row.subject_ids?.length ?? 0).toString()),
  },
  {
    inlineEditActive: false,
    label: "Max Students",
    field: "max_students",
    align: "center",
    width: "130px",
  },
  {
    label: "Deleted",
    field: "deleted",
    align: "center",
    width: "100px",
    render: (row: AdminClassDataDTO) => h("span", row.deleted ? "Yes" : "No"),
  },
  {
    label: "Actions",
    slotName: "operation",
    operation: true,
    fixed: "right",
    width: "220px",
    align: "center",
  },
]);

/* ---------------------- create form state ---------------------- */
import type { Field } from "~/components/types/form";
const createDialogVisible = ref(false);
const createFormLoading = ref(false);

const createFormData = ref<AdminCreateClassDTO>({
  name: "",
  teacher_id: null,
  subject_ids: [],
  max_students: 30,
});

const classFormFields: Field<AdminCreateClassDTO>[] = [
  {
    key: "name",
    label: "Class Name",
    component: ElInput,
    formItemProps: {
      required: true,
      prop: "name",
      label: "Class Name",
    },
    componentProps: {
      placeholder: "Class name (e.g. Grade 7A)",
      clearable: true,
    },
  },
  {
    key: "teacher_id",
    label: "Teacher",
    component: TeacherSelect,
    formItemProps: {
      required: false,
      prop: "teacher_id",
      label: "Teacher",
    },
    componentProps: {
      placeholder: "Optional teacher",
      clearable: true,
    },
  },
  {
    key: "max_students",
    label: "Max Students",
    component: ElInputNumber,
    formItemProps: {
      required: false,
      prop: "max_students",
      label: "Max Students",
    },
    componentProps: {
      min: 1,
      max: 100,
      placeholder: "Optional max students",
    },
  },
  {
    key: "subject_ids",
    label: "Subjects",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      required: false,
      prop: "subject_ids",
      label: "Subjects",
    },
    componentProps: {
      multiple: true,
      filterable: true,
      clearable: true,
      placeholder: "Select subjects",
      loading: subjectOptionsLoading.value,
    },
    childComponentProps: {
      options: () => subjectOptions.value,
      valueKey: "value",
      labelKey: "label",
    },
  },
];

const createDialogWidth = computed(() => "50%");

/* ---------------------- manage students & teacher dialog ---------------------- */

const manageStudentsVisible = ref(false);
const currentClassForStudents = ref<AdminClassDataDTO | null>(null);

const originalStudentIds = ref<string[]>([]);
const selectedStudentIds = ref<string[]>([]);
const selectedTeacherId = ref<string | null>(null);

const detailLoading = ref<Record<string | number, boolean>>({});
const deleteLoading = ref<Record<string | number, boolean>>({});
const saveStudentsLoading = ref(false);

async function openManageStudentsDialog(row: AdminClassDataDTO) {
  detailLoading.value[row.id] = true;
  try {
    currentClassForStudents.value = row;

    originalStudentIds.value = [...(row.student_ids ?? [])];
    selectedStudentIds.value = [...(row.student_ids ?? [])];

    selectedTeacherId.value = (row.teacher_id as string | null) ?? null;

    await nextTick();
    manageStudentsVisible.value = true;
  } finally {
    detailLoading.value[row.id] = false;
  }
}

function cancelManageStudents() {
  manageStudentsVisible.value = false;
}

/**
 * Save both students and teacher changes in one click.
 */
async function saveManageStudents() {
  const cls = currentClassForStudents.value;
  if (!cls) return;

  saveStudentsLoading.value = true;

  const classId = cls.id;
  const oldStudentSet = new Set(originalStudentIds.value);
  const newStudentSet = new Set(selectedStudentIds.value);

  const toAdd: string[] = [];
  const toRemove: string[] = [];

  for (const id of newStudentSet) {
    if (!oldStudentSet.has(id)) toAdd.push(id);
  }
  for (const id of oldStudentSet) {
    if (!newStudentSet.has(id)) toRemove.push(id);
  }

  const oldTeacherId = (cls.teacher_id as string | null) ?? null;
  const newTeacherId = selectedTeacherId.value ?? null;
  const teacherChanged = oldTeacherId !== newTeacherId;

  try {
    // update students
    for (const sid of toAdd) {
      await adminApi.class.enrollStudent(classId, sid);
    }
    for (const sid of toRemove) {
      await adminApi.class.unenrollStudent(classId, sid);
    }

    // update teacher if changed
    if (teacherChanged) {
      if (newTeacherId === null) {
        await adminApi.class.unassignClassTeacher(classId);
      } else {
        await adminApi.class.assignClassTeacher(classId, newTeacherId!);
      }
    }

    manageStudentsVisible.value = false;
    await fetchClasses();
  } catch (err) {
    console.error("Failed to update class", err);
    ElMessage.error("Failed to update class");
  } finally {
    saveStudentsLoading.value = false;
  }
}

/* ---------------------- fetch classes ---------------------- */

async function fetchClasses() {
  tableLoading.value = true;
  try {
    const res: AdminClassListDTO | undefined =
      await adminApi.class.getClasses();
    classes.value = res?.items ?? [];
  } catch (err) {
    console.error("Failed to fetch classes", err);
  } finally {
    tableLoading.value = false;
  }
}

/* ---------------------- create class actions ---------------------- */

async function openCreateDialog() {
  createFormData.value = {
    name: "",
    teacher_id: null,
    subject_ids: [],
    max_students: 30,
  };
  await fetchSubjectOptions();
  createDialogVisible.value = true;
}

async function handleSaveCreateForm(payload: Partial<AdminCreateClassDTO>) {
  createFormLoading.value = true;
  try {
    const dataToSend: AdminCreateClassDTO = {
      name: payload.name ?? createFormData.value.name,
      teacher_id: payload.teacher_id ?? createFormData.value.teacher_id ?? null,
      subject_ids:
        (payload.subject_ids as string[]) ??
        createFormData.value.subject_ids ??
        [],
      max_students:
        payload.max_students ?? createFormData.value.max_students ?? null,
    };

    await adminApi.class.createClass(dataToSend);
    createDialogVisible.value = false;
    await fetchClasses();
  } catch (err) {
    console.error("Failed to create class", err);
    ElMessage.error("Failed to create class");
  } finally {
    createFormLoading.value = false;
  }
}

function handleCancelCreateForm() {
  createDialogVisible.value = false;
}

/* ---------------------- soft delete class ---------------------- */

async function handleSoftDelete(row: AdminClassDataDTO) {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to soft delete this class?",
      "Warning",
      {
        confirmButtonText: "Yes",
        cancelButtonText: "No",
        type: "warning",
      }
    );

    deleteLoading.value[row.id] = true;
    await adminApi.class.softDeleteClass(row.id);
    await fetchClasses();
  } catch (err: any) {
    if (err === "cancel" || err === "close") return;
    console.error("Soft delete failed", err);
  } finally {
    deleteLoading.value[row.id] = false;
  }
}

/* ---------------------- lifecycle ---------------------- */

onMounted(() => {
  fetchClasses();
});
</script>

<template>
  <el-row class="m-2" justify="space-between">
    <el-col :span="12">
      <BaseButton type="default" :loading="tableLoading" @click="fetchClasses">
        Refresh
      </BaseButton>

      <BaseButton type="primary" class="ml-2" @click="openCreateDialog">
        Add Class
      </BaseButton>
    </el-col>

    <el-col :span="12" class="text-right">
      <ElRadioGroup v-model="showDeleted">
        <ElRadioButton label="all">All</ElRadioButton>
        <ElRadioButton label="active">Active</ElRadioButton>
        <ElRadioButton label="deleted">Deleted</ElRadioButton>
      </ElRadioGroup>
    </el-col>
  </el-row>

  <ErrorBoundary>
    <SmartTable
      :data="filteredClasses"
      :columns="classColumns"
      :loading="tableLoading"
    >
      <template #operation="{ row }">
        <ActionButtons
          :rowId="row.id"
          :detailContent="`Manage students in ${row.name}`"
          deleteContent="Delete class"
          @detail="openManageStudentsDialog(row)"
          @delete="handleSoftDelete(row)"
          :deleteLoading="deleteLoading[row.id] ?? false"
          :detailLoading="detailLoading[row.id] ?? false"
        />
      </template>
    </SmartTable>
  </ErrorBoundary>

  <!-- CREATE CLASS DIALOG -->
  <ErrorBoundary>
    <SmartFormDialog
      v-model:visible="createDialogVisible"
      v-model="createFormData"
      :fields="classFormFields"
      title="Add Class"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createDialogWidth"
    />
  </ErrorBoundary>

  <!-- MANAGE STUDENTS + TEACHER DIALOG -->
  <ErrorBoundary>
    <el-dialog
      v-model="manageStudentsVisible"
      :title="`Manage Class${
        currentClassForStudents ? ' - ' + currentClassForStudents.name : ''
      }`"
      width="40%"
    >
      <div class="mb-4 space-y-4">
        <div>
          <p class="text-xs text-gray-500 mb-1">Students</p>
          <StudentSelect
            v-model="selectedStudentIds"
            multiple
            placeholder="Select students to enroll"
          />
        </div>

        <div>
          <p class="text-xs text-gray-500 mb-1">Teacher</p>
          <TeacherSelect
            v-model="selectedTeacherId"
            placeholder="Select teacher"
            clearable
          />
        </div>
      </div>

      <template #footer>
        <BaseButton @click="cancelManageStudents">Cancel</BaseButton>
        <BaseButton
          type="primary"
          class="ml-2"
          :loading="saveStudentsLoading"
          @click="saveManageStudents"
        >
          Save
        </BaseButton>
      </template>
    </el-dialog>
  </ErrorBoundary>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
