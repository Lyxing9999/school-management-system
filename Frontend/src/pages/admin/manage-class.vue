<script setup lang="ts">
import { ref, computed, onMounted, h, nextTick } from "vue";

definePageMeta({ layout: "admin" });

/* ------------------------------------
 * Base components
 * ---------------------------------- */
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import StudentSelect from "~/components/Selects/StudentSelect.vue";
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";

/* ------------------------------------
 * Element Plus
 * ---------------------------------- */
import {
  ElMessageBox,
  ElMessage,
  ElRadioGroup,
  ElRadioButton,
} from "element-plus";

/* ------------------------------------
 * Services & types
 * ---------------------------------- */
import { adminService } from "~/api/admin";
import type {
  AdminCreateClass,
  AdminClassDataDTO,
  AdminClassListDTO,
} from "~/api/admin/class/class.dto";

import type { Field } from "~/components/types/form";

/* ------------------------------------
 * Dynamic create form system
 * ---------------------------------- */
import { useDynamicCreateFormReactive } from "~/form-system/useDynamicForm.ts/useAdminForms";

const adminApi = adminService();

/* ===========================
 *  TABLE STATE
 * =========================== */
import { classColumns } from "~/modules/tables/columns/admin/classColumns";
const classes = ref<AdminClassDataDTO[]>([]);
const tableLoading = ref(false);
const showDeleted = ref<"all" | "active" | "deleted">("all");

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

/* ===========================
 *  SUBJECT OPTIONS (ASYNC)
 * =========================== */

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

/* ===========================
 *  CREATE CLASS (DYNAMIC FORM)
 * =========================== */

// Only CLASS mode on this page
const createMode = ref<"CLASS">("CLASS");

const {
  formDialogVisible: createFormVisible,
  formData: createFormData,
  schema: baseCreateFormSchema,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
  openForm: openCreateForm,
  loading: createFormLoading,
} = useDynamicCreateFormReactive(createMode);

// Inject loading + options into the `subject_ids` field
const createFormSchema = computed<Field<AdminCreateClass>[]>(() =>
  baseCreateFormSchema.value.map((field) => {
    if (field.key !== "subject_ids") return field;

    return {
      ...field,
      componentProps: {
        ...(field.componentProps ?? {}),
        loading: subjectOptionsLoading.value,
      },
      childComponentProps: {
        ...(field.childComponentProps ?? {}),
        options: () => subjectOptions.value,
      },
    };
  })
);

const createFormDialogWidth = computed(() => "50%");

async function openCreateDialog() {
  await fetchSubjectOptions();
  await openCreateForm(); // uses registry formData() to init
}

async function handleSaveCreateForm(payload: Partial<AdminCreateClass>) {
  try {
    await saveCreateForm(payload); // registry service().create
    cancelCreateForm();
    await fetchClasses();
  } catch (err) {
    console.error("Failed to create class", err);
    ElMessage.error("Failed to create class");
  }
}

function handleCancelCreateForm() {
  cancelCreateForm();
}

/* ===========================
 *  MANAGE STUDENTS & TEACHER
 * =========================== */

type ManageClassRelationsForm = {
  student_ids: string[];
  teacher_id: string | null;
};

const manageStudentsVisible = ref(false);
const manageRelationsForm = ref<ManageClassRelationsForm>({
  student_ids: [],
  teacher_id: null,
});

const manageRelationsFields: Field<ManageClassRelationsForm>[] = [
  {
    key: "student_ids",
    label: "Students",
    component: StudentSelect,
    formItemProps: {
      label: "Students",
    },
    componentProps: {
      multiple: true,
      placeholder: "Select students to enroll",
    },
  },
  {
    key: "teacher_id",
    label: "Teacher",
    component: TeacherSelect,
    formItemProps: {
      label: "Teacher",
    },
    componentProps: {
      placeholder: "Select teacher",
      clearable: true,
    },
  },
];

const currentClassForStudents = ref<AdminClassDataDTO | null>(null);
const originalStudentIds = ref<string[]>([]);
const originalTeacherId = ref<string | null>(null);

const detailLoading = ref<Record<string | number, boolean>>({});
const deleteLoading = ref<Record<string | number, boolean>>({});
const saveStudentsLoading = ref(false);

async function openManageStudentsDialog(row: AdminClassDataDTO) {
  detailLoading.value[row.id] = true;
  try {
    currentClassForStudents.value = row;

    const students = row.student_ids ?? [];
    const teacher = (row.teacher_id as string | null) ?? null;

    originalStudentIds.value = [...students];
    originalTeacherId.value = teacher;

    manageRelationsForm.value = {
      student_ids: [...students],
      teacher_id: teacher,
    };

    await nextTick();
    manageStudentsVisible.value = true;
  } finally {
    detailLoading.value[row.id] = false;
  }
}

function cancelManageStudents() {
  manageStudentsVisible.value = false;
}

async function saveManageStudents(payload: Partial<ManageClassRelationsForm>) {
  const cls = currentClassForStudents.value;
  if (!cls) return;

  const form: ManageClassRelationsForm = {
    ...manageRelationsForm.value,
    ...payload,
  };

  const newStudents = form.student_ids ?? [];
  const newTeacher = form.teacher_id ?? null;

  saveStudentsLoading.value = true;

  const classId = cls.id;
  const oldStudentSet = new Set(originalStudentIds.value);
  const newStudentSet = new Set(newStudents);

  const toAdd: string[] = [];
  const toRemove: string[] = [];

  for (const id of newStudentSet) {
    if (!oldStudentSet.has(id)) toAdd.push(id);
  }
  for (const id of oldStudentSet) {
    if (!newStudentSet.has(id)) toRemove.push(id);
  }

  const oldTeacherId = originalTeacherId.value;
  const teacherChanged = oldTeacherId !== newTeacher;

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
      if (newTeacher === null) {
        await adminApi.class.unassignClassTeacher(classId);
      } else {
        await adminApi.class.assignClassTeacher(classId, newTeacher);
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

/* ===========================
 *  FETCH + DELETE
 * =========================== */

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

/* ===========================
 *  LIFECYCLE
 * =========================== */

onMounted(() => {
  fetchClasses();
  // optional: prefetch subjects
  // fetchSubjectOptions();
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

  <!-- CREATE CLASS DIALOG (form-system) -->
  <ErrorBoundary>
    <SmartFormDialog
      v-model:visible="createFormVisible"
      v-model="createFormData"
      :fields="createFormSchema"
      title="Add Class"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createFormDialogWidth"
    />
  </ErrorBoundary>

  <!-- MANAGE STUDENTS + TEACHER DIALOG (SmartFormDialog) -->
  <ErrorBoundary>
    <SmartFormDialog
      v-model:visible="manageStudentsVisible"
      v-model="manageRelationsForm"
      :fields="manageRelationsFields"
      :title="`Manage Class${
        currentClassForStudents ? ' - ' + currentClassForStudents.name : ''
      }`"
      :loading="saveStudentsLoading"
      :width="'40%'"
      @save="saveManageStudents"
      @cancel="cancelManageStudents"
      :useElForm="true"
    />
  </ErrorBoundary>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
