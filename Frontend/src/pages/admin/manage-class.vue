<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";

definePageMeta({ layout: "admin" });

/* ------------------------------------
 * Base components
 * ---------------------------------- */
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import StudentEnrollmentSelect from "~/components/Selects/StudentEnrollmentSelect.vue";
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

/* ------------------------------------
 * Utils
 * ---------------------------------- */
import { reportError } from "~/utils/errors";

const adminApi = adminService();

/* ===========================
 *  TYPES
 * =========================== */

type ShowDeletedFilter = "all" | "active" | "deleted";

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
  data: classes,
  loading: tableLoading,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<AdminClassRow, ShowDeletedFilter>(
  async (filter, page, pageSize) => {
    const res: AdminClassListDTO | undefined =
      await adminApi.class.getClasses();
    const rawItems = res?.items ?? [];

    // Prefer backend enrolled_count; fallback only if your DTO still includes student_ids
    const displayClasses: AdminClassRow[] = rawItems.map((c: any) => ({
      ...(c as AdminClassDataDTO),
      enrolled_count:
        typeof c.enrolled_count === "number"
          ? c.enrolled_count
          : c.student_ids?.length ?? 0,
      subject_count: c.subject_ids?.length ?? 0,
    }));

    const filtered =
      filter === "all"
        ? displayClasses
        : filter === "deleted"
        ? displayClasses.filter((c: any) => c.deleted)
        : displayClasses.filter((c: any) => !c.deleted);

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
    reportError(err, "subjectOptions.fetch", "log");
    ElMessage.error("Failed to load subjects.");
  } finally {
    subjectOptionsLoading.value = false;
  }
}

/* ===========================
 *  CREATE CLASS (DYNAMIC FORM)
 * =========================== */

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
  if (!created) return;
  ElMessage.success("Class created.");
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

const currentClassForStudents = ref<AdminClassRow | null>(null);

const originalStudentIds = ref<string[]>([]);
const originalTeacherId = ref<string | null>(null);

const detailLoading = ref<Record<string | number, boolean>>({});
const deleteLoading = ref<Record<string | number, boolean>>({});
const saveStudentsLoading = ref(false);

const studentSelectPreloaded = ref<{ value: string; label: string }[]>([]);
const studentsInClassLoading = ref(false);

const manageRelationsFields = computed<Field<ManageClassRelationsForm>[]>(
  () => [
    {
      key: "student_ids",
      label: "Students",
      component: StudentEnrollmentSelect,
      formItemProps: { label: "Students" },
      componentProps: {
        classId: currentClassForStudents.value?.id ?? "",
        multiple: true,
        placeholder: "Select students to enroll",
        preloadedOptions: studentSelectPreloaded.value,
        loading: studentsInClassLoading.value,
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
const manageStudentsDialogKey = ref("");
async function openManageStudentsDialog(row: AdminClassRow) {
  currentClassForStudents.value = row;
  manageStudentsDialogKey.value = row.id;
  studentSelectPreloaded.value = [];
  manageRelationsForm.value = {
    student_ids: [],
    teacher_id: (row.teacher_id as string | null) ?? null,
  };
  originalStudentIds.value = [];
  originalTeacherId.value = (row.teacher_id as string | null) ?? null;

  studentsInClassLoading.value = true;
  detailLoading.value[row.id] = true;

  try {
    const res = await adminApi.class.listStudentsInClass(row.id);
    const preloaded = res?.items ?? [];

    studentSelectPreloaded.value = preloaded;

    const loadedStudentIds = preloaded.map((x) => x.value);
    const loadedTeacherId = (row.teacher_id as string | null) ?? null;

    manageRelationsForm.value = {
      student_ids: loadedStudentIds,
      teacher_id: loadedTeacherId,
    };

    originalStudentIds.value = [...loadedStudentIds];
    originalTeacherId.value = loadedTeacherId;
    manageStudentsVisible.value = true;
  } catch (err) {
    reportError(err, `class.students.load classId=${row.id}`, "log");
    ElMessage.error("Failed to load students in this class.");
  } finally {
    studentsInClassLoading.value = false;
    detailLoading.value[row.id] = false;
  }
}
function cancelManageStudents() {
  manageStudentsVisible.value = false;
  currentClassForStudents.value = null;
}

// helper: normalize teacher_id from select ("" -> null)
function normalizeTeacherId(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}
async function saveManageStudents(payload: Partial<ManageClassRelationsForm>) {
  const cls = currentClassForStudents.value;
  if (!cls) return;

  const form: ManageClassRelationsForm = {
    ...manageRelationsForm.value,
    ...payload,
  };

  const classId = cls.id;
  const newStudents = form.student_ids ?? [];
  const newTeacher = normalizeTeacherId(form.teacher_id);

  saveStudentsLoading.value = true;

  try {
    const result = await adminApi.class.updateRelations(classId, {
      student_ids: newStudents,
      teacher_id: newTeacher,
    });

    const hasIssues =
      result.conflicts.length > 0 || result.capacity_rejected.length > 0;

    if (!hasIssues) {
      ElMessage.success(
        `Saved. Added ${result.added.length}, removed ${result.removed.length}.`
      );
      manageStudentsVisible.value = false;
    } else {
      await ElMessageBox.alert(
        [
          `Saved with exceptions:`,
          `- Added: ${result.added.length}`,
          `- Removed: ${result.removed.length}`,
          result.conflicts.length
            ? `- Conflicts: ${result.conflicts.length}`
            : null,
          result.capacity_rejected.length
            ? `- Capacity rejected: ${result.capacity_rejected.length}`
            : null,
          "",
          "Reloading server truth into the selector.",
        ]
          .filter(Boolean)
          .join("\n"),
        "Some changes were not applied",
        { type: "warning" }
      );

      // Reload server truth
      const res = await adminApi.class.listStudentsInClass(classId);
      const preloaded = res?.items ?? [];
      studentSelectPreloaded.value = preloaded;

      const loadedStudentIds = preloaded.map((x: any) => x.value);
      manageRelationsForm.value = {
        student_ids: loadedStudentIds,
        teacher_id: result.teacher_id,
      };

      originalStudentIds.value = [...loadedStudentIds];
      originalTeacherId.value = result.teacher_id;
    }

    await fetchPage(currentPage.value || 1);
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
      { confirmButtonText: "Yes", cancelButtonText: "No", type: "warning" }
    );

    deleteLoading.value[row.id] = true;
    await adminApi.class.softDeleteClass(row.id);
    await fetchPage(currentPage.value || 1);
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

const searchModel = ref("");
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="Classes"
      description="Manage class sections, enrolled students and assigned teachers."
      :loading="tableLoading"
      :showRefresh="true"
      :showReset="true"
      :showSearch="true"
      :stats="classHeaderStats"
      @refresh="fetchClasses"
      v-model:searchModelValue="searchModel"
      @update:searchModelValue="(v) => emit('update:searchModelValue', v)"
    >
      <template #filters>
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 w-full"
        >
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

    <SmartFormDialog
      :key="manageStudentsDialogKey"
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
