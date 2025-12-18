<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from "vue";

definePageMeta({ layout: "admin" });

/* ------------------------------------
 * Base components
 * ---------------------------------- */
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import StudentSelect from "~/components/Selects/StudentSelect.vue";
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";

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
  AdminStudentsInClassSelectDTO,
} from "~/api/admin/class/class.dto";

import type { Field } from "~/components/types/form";

/* ------------------------------------
 * Dynamic create form system
 * ---------------------------------- */
import { useDynamicCreateFormReactive } from "~/form-system/useDynamicForm.ts/useAdminForms";

/* ------------------------------------
 * Table columns
 * ---------------------------------- */
import { classColumns } from "~/modules/tables/columns/admin/classColumns";

/* ------------------------------------
 * Pagination composable
 * ---------------------------------- */
import { usePaginatedFetch } from "~/composables/usePaginatedFetch";

/* ------------------------------------
 * Header stats composable
 * ---------------------------------- */
import { useHeaderState } from "~/composables/useHeaderState";

const adminApi = adminService();

/* ===========================
 *  TYPES
 * =========================== */

type ShowDeletedFilter = "all" | "active" | "deleted";

// extend row with computed fields for table display
type AdminClassRow = AdminClassDataDTO & {
  enrolled_count: number;
  subject_count: number;
};

/* ===========================
 *  FILTER STATE
 * =========================== */

const showDeleted = ref<ShowDeletedFilter>("all");

/* ===========================
 *  PAGINATED FETCH
 * =========================== */

const {
  data: classes, // data for SmartTable
  loading: tableLoading,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<AdminClassRow, ShowDeletedFilter>(
  // fetchFn: backend returns all classes; we filter + paginate on client
  async (filter, page, pageSize) => {
    const res: AdminClassListDTO | undefined =
      await adminApi.class.getClasses();

    const rawItems = res?.items ?? [];

    // add enrolled_count and subject_count
    const displayClasses: AdminClassRow[] = rawItems.map((c) => ({
      ...c,
      enrolled_count: c.student_ids?.length ?? 0,
      subject_count: c.subject_ids?.length ?? 0,
    }));

    // filter by deleted state
    const filtered =
      filter === "all"
        ? displayClasses
        : filter === "deleted"
        ? displayClasses.filter((c) => c.deleted)
        : displayClasses.filter((c) => !c.deleted);

    const total = filtered.length;
    const start = (page - 1) * pageSize;
    const items = filtered.slice(start, start + pageSize);

    return { items, total };
  },
  1,
  10,
  showDeleted
);

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
  await openCreateForm();
}

async function handleSaveCreateForm(payload: Partial<AdminCreateClass>) {
  const created = await saveCreateForm(payload);
  if (!created) {
    return;
  }
  await fetchPage(1);
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
const manageRelationsFields = computed<Field<ManageClassRelationsForm>[]>(
  () => [
    {
      key: "student_ids",
      label: "Students",
      component: StudentSelect,
      formItemProps: { label: "Students" },
      componentProps: {
        multiple: true,
        placeholder: "Select students to enroll",
        loading: studentsInClassLoading.value,

        // ✅ IMPORTANT: StudentSelect expects `options` prop
        options: studentSelectPreloaded, // Ref<array> is fine
      },
    },
    {
      key: "teacher_id",
      label: "Teacher",
      component: TeacherSelect,
      formItemProps: { label: "Teacher" },
      componentProps: { placeholder: "Select teacher", clearable: true },
    },
  ]
);

const currentClassForStudents = ref<AdminClassRow | null>(null);
const originalStudentIds = ref<string[]>([]);
const originalTeacherId = ref<string | null>(null);

const detailLoading = ref<Record<string | number, boolean>>({});
const deleteLoading = ref<Record<string | number, boolean>>({});
const saveStudentsLoading = ref(false);
const studentSelectPreloaded = ref<{ value: string; label: string }[]>([]);
const studentsInClassLoading = ref(false);

async function openManageStudentsDialog(row: AdminClassRow) {
  currentClassForStudents.value = row;
  studentSelectPreloaded.value = [];
  manageRelationsForm.value = {
    student_ids: [],
    teacher_id: (row.teacher_id as string | null) ?? null,
  };

  studentsInClassLoading.value = true;
  detailLoading.value[row.id] = true;
  manageStudentsVisible.value = true;

  try {
    const res = await adminApi.class.listStudentsInClass(row.id);

    studentSelectPreloaded.value = res.items ?? [];

    manageRelationsForm.value = {
      student_ids: studentSelectPreloaded.value.map((x) => x.value),
      teacher_id: (row.teacher_id as string | null) ?? null,
    };
  } finally {
    studentsInClassLoading.value = false;
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
    await fetchPage(currentPage.value || 1);
  } catch (err) {
    console.error("Failed to update class", err);
  } finally {
    saveStudentsLoading.value = false;
  }
}

/* ===========================
 *  FETCH + DELETE
 * =========================== */

async function fetchClasses() {
  await fetchPage(currentPage.value || 1);
}

async function handleSoftDelete(row: AdminClassRow) {
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
    await fetchPage(currentPage.value || 1);
  } catch (err: any) {
    if (err === "cancel" || err === "close") return;
    console.error("Soft delete failed", err);
  } finally {
    deleteLoading.value[row.id] = false;
  }
}

/* ===========================
 *  LIFECYCLE & WATCHERS
 * =========================== */

onMounted(() => {
  fetchPage(1);
});

// when filter changes, reset to first page & refetch
watch(showDeleted, () => {
  fetchPage(1);
});

/* ===========================
 *  HEADER STATS
 * =========================== */

const totalClasses = computed(() => totalRows.value ?? 0);

const { headerState: classHeaderStats } = useHeaderState({
  items: [
    {
      key: "classes",
      getValue: () => totalClasses.value,
      singular: "class",
      plural: "classes",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "filter",
      getValue: () => totalClasses.value,
      label: () =>
        showDeleted.value === "all"
          ? "classes (all)"
          : showDeleted.value === "active"
          ? "active classes"
          : "deleted classes",
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
      title="Classes"
      description="Manage class sections, enrolled students and assigned teachers."
      :loading="tableLoading"
      :showRefresh="true"
      :stats="classHeaderStats"
      @refresh="fetchClasses"
    >
      <!-- Filters: status (all / active / deleted) -->
      <template #filters>
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 w-full"
        >
          <!-- Status filter -->
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Status:</span>
            <ElRadioGroup v-model="showDeleted" size="small">
              <ElRadioButton label="all">All</ElRadioButton>
              <ElRadioButton label="active">Active</ElRadioButton>
              <ElRadioButton label="deleted">Deleted</ElRadioButton>
            </ElRadioGroup>
          </div>
        </div>
      </template>

      <!-- Actions: Refresh + Add Class -->
      <template #actions>
        <BaseButton
          plain
          :loading="tableLoading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="fetchClasses"
        >
          Refresh
        </BaseButton>

        <BaseButton type="primary" @click="openCreateDialog">
          Add Class
        </BaseButton>
      </template>
    </OverviewHeader>

    <!-- TABLE -->
    <el-card>
      <SmartTable
        :data="classes"
        :columns="classColumns"
        v-loading="tableLoading"
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
    </el-card>

    <!-- PAGINATION -->
    <el-row v-if="totalRows > 0" justify="end" class="m-4">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="totalRows"
        :page-sizes="[10, 20, 50, 100]"
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

    <!-- CREATE CLASS DIALOG -->

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

    <!-- MANAGE STUDENTS + TEACHER DIALOG -->

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
  </div>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
