<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { storeToRefs } from "pinia";

definePageMeta({ layout: "default" });

/* ------------------------------------
 * Base components
 * ---------------------------------- */
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import SmartFormDialog from "~/components/form/SmartFormDialog.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import ActionButtons from "~/components/buttons/ActionButtons.vue";
import StudentEnrollmentSelect from "~/components/selects/student/StudentEnrollmentSelect.vue";
import TeacherSelect from "~/components/selects/teacher/TeacherSelect.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";

/* ------------------------------------
 * Element Plus
 * ---------------------------------- */
import { ElMessageBox, ElMessage, ElEmpty, ElAlert } from "element-plus";

/* ------------------------------------
 * Services & types
 * ---------------------------------- */
import { adminService } from "~/api/admin";
import type {
  AdminCreateClass,
  AdminClassDataDTO,
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
 * Pagination composable (NEW API)
 * ---------------------------------- */
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";

/* ------------------------------------
 * Header stats composable
 * ---------------------------------- */
import { useHeaderState } from "~/composables/ui/useHeaderState";

/* ------------------------------------
 * Preferences store (page size)
 * ---------------------------------- */
import { usePreferencesStore } from "~/stores/preferencesStore";

/* ------------------------------------
 * Utils
 * ---------------------------------- */
import { reportError } from "~/utils/errors/errors";

const adminApi = adminService();

/* ===========================
 *  TYPES
 * =========================== */
type AdminClassRow = AdminClassDataDTO & {
  enrolled_count: number;
  subject_count: number;
};

/* ===========================
 *  STORE
 * =========================== */
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

/* ===========================
 *  STATE
 * =========================== */
const searchModel = ref(""); // bound to OverviewHeader search
const dummyFilter = ref(""); // satisfies composable generic

/* ===========================
 *  PAGINATED FETCH (SERVER)
 * =========================== */
const {
  data: classes,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  initialLoading,
  fetching,
  fetchPage,
  goPage,
} = usePaginatedFetch<AdminClassRow, string>(
  async (_unusedFilter, page, size, _signal) => {
    const q = searchModel.value.trim();

    // Backend expected to return { items, total }
    const res = await adminApi.class.getClasses({
      q: q.length ? q : undefined,
      page,
      limit: size,
    });

    return {
      items: (res.items ?? []) as AdminClassRow[],
      total: res.total ?? 0,
    };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: dummyFilter,
  }
);

const tableLoading = computed(() => initialLoading.value || fetching.value);

async function fetchClasses(page = currentPage.value || 1) {
  await fetchPage(page);
}

/* ===========================
 *  SUBJECT OPTIONS (ASYNC)
 * =========================== */
const subjectOptions = ref<{ value: string; label: string }[]>([]);
const subjectOptionsLoading = ref(false);

async function fetchSubjectOptions() {
  if (subjectOptions.value.length > 0) return;

  subjectOptionsLoading.value = true;
  try {
    // If your subject endpoint is paginated, change this to request a big page_size.
    const res: any = await adminApi.subject.getSubjects();
    const items = res?.items ?? res ?? [];
    subjectOptions.value = (items ?? []).map((s: any) => ({
      value: String(s.id),
      label: `${s.name ?? "-"} (${s.code ?? "-"})`,
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

const createFormSchema = computed(() =>
  baseCreateFormSchema.value.map((field) => {
    if (field.key !== "subject_ids") return field;

    return {
      ...field,
      key: field.key,
      componentProps: {
        ...(field.componentProps ?? {}),
        loading: subjectOptionsLoading.value,
      },
      childComponentProps: {
        ...(field.childComponentProps ?? {}),
        options: () => subjectOptions.value,
      },
    } satisfies Field<AdminCreateClass>;
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
  homeroom_teacher_id: string | null;
};

const manageStudentsVisible = ref(false);
const manageRelationsForm = ref<ManageClassRelationsForm>({
  student_ids: [],
  homeroom_teacher_id: null,
});

/** snapshot of server truth when dialog opens */
const manageRelationsInitial = ref<ManageClassRelationsForm | null>(null);

const currentClassForStudents = ref<AdminClassRow | null>(null);

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
      key: "homeroom_teacher_id",
      label: "Teacher",
      component: TeacherSelect,
      formItemProps: { label: "Teacher" },
      componentProps: { placeholder: "Select teacher", clearable: true },
    },
  ]
);

const manageStudentsDialogKey = ref("");

function normalizeTeacherId(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function normalizeStudentIds(ids: unknown): string[] {
  if (!Array.isArray(ids)) return [];
  const cleaned = ids
    .filter((x) => typeof x === "string")
    .map((x) => x.trim())
    .filter(Boolean);

  return Array.from(new Set(cleaned)).sort();
}

function sameStringArrayAsSet(a: string[], b: string[]) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}

async function openManageStudentsDialog(row: AdminClassRow) {
  currentClassForStudents.value = row;
  manageStudentsDialogKey.value = String(row.id);

  studentSelectPreloaded.value = [];
  manageRelationsInitial.value = null;

  manageRelationsForm.value = {
    student_ids: [],
    homeroom_teacher_id: (row.homeroom_teacher_id as string | null) ?? null,
  };

  studentsInClassLoading.value = true;
  detailLoading.value[row.id] = true;

  try {
    const res = await adminApi.class.listStudentsInClass(row.id);
    const preloaded = res?.items ?? [];

    studentSelectPreloaded.value = preloaded;

    manageRelationsForm.value = {
      student_ids: preloaded.map((x: any) => String(x.value)),
      homeroom_teacher_id: (row.homeroom_teacher_id as string | null) ?? null,
    };

    manageRelationsInitial.value = {
      student_ids: [...manageRelationsForm.value.student_ids],
      homeroom_teacher_id: manageRelationsForm.value.homeroom_teacher_id,
    };

    manageStudentsVisible.value = true;
  } catch (err) {
    reportError(err, `class.students.load classId=${row.id}`, "log");
  } finally {
    studentsInClassLoading.value = false;
    detailLoading.value[row.id] = false;
  }
}

function cancelManageStudents() {
  manageStudentsVisible.value = false;
  currentClassForStudents.value = null;
  manageRelationsInitial.value = null;
}

async function saveManageStudents(payload: Partial<ManageClassRelationsForm>) {
  const cls = currentClassForStudents.value;
  if (!cls) return;

  const form: ManageClassRelationsForm = {
    ...manageRelationsForm.value,
    ...payload,
  };

  const classId = cls.id;

  const newTeacher = normalizeTeacherId(form.homeroom_teacher_id);
  const newStudents = normalizeStudentIds(form.student_ids);

  const initial = manageRelationsInitial.value;
  if (initial) {
    const initialTeacher = normalizeTeacherId(initial.homeroom_teacher_id);
    const initialStudents = normalizeStudentIds(initial.student_ids);

    const teacherUnchanged = initialTeacher === newTeacher;
    const studentsUnchanged = sameStringArrayAsSet(
      initialStudents,
      newStudents
    );

    if (teacherUnchanged && studentsUnchanged) {
      ElMessage.info("No changes to save.");
      return;
    }
  }

  saveStudentsLoading.value = true;

  try {
    const result: any = await adminApi.class.updateRelations(classId, {
      student_ids: newStudents,
      homeroom_teacher_id: newTeacher,
    });

    const hasIssues =
      (result.conflicts?.length ?? 0) > 0 ||
      (result.capacity_rejected?.length ?? 0) > 0;

    if (!hasIssues) {
      ElMessage.success(
        `Saved. Added ${result.added.length}, removed ${result.removed.length}.`
      );

      manageRelationsInitial.value = {
        student_ids: [...newStudents],
        homeroom_teacher_id: newTeacher,
      };

      manageStudentsVisible.value = false;
    } else {
      await ElMessageBox.alert(
        [
          `Saved with exceptions:`,
          `- Added: ${result.added.length}`,
          `- Removed: ${result.removed.length}`,
          result.conflicts?.length
            ? `- Conflicts: ${result.conflicts.length}`
            : null,
          result.capacity_rejected?.length
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

      const res = await adminApi.class.listStudentsInClass(classId);
      const preloaded = res?.items ?? [];

      studentSelectPreloaded.value = preloaded;

      manageRelationsForm.value = {
        student_ids: preloaded.map((x: any) => String(x.value)),
        homeroom_teacher_id: result.homeroom_teacher_id ?? null,
      };

      manageRelationsInitial.value = {
        student_ids: [...manageRelationsForm.value.student_ids],
        homeroom_teacher_id: manageRelationsForm.value.homeroom_teacher_id,
      };
    }

    await fetchPage(currentPage.value || 1);
  } finally {
    saveStudentsLoading.value = false;
  }
}

/* ===========================
 *  DELETE
 * =========================== */
async function handleSoftDelete(row: AdminClassRow) {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to soft delete this class?",
      "Warning",
      { confirmButtonText: "Yes", cancelButtonText: "No", type: "warning" }
    );

    deleteLoading.value[row.id] = true;
    await adminApi.class.softDeleteClass(row.id);

    // if you deleted last row on page, go back
    const page = currentPage.value || 1;
    await fetchClasses(page);

    if (page > 1 && (classes.value?.length ?? 0) === 0) {
      await fetchClasses(page - 1);
    }
  } finally {
    deleteLoading.value[row.id] = false;
  }
}

/* ===========================
 *  SEARCH (debounced)
 * =========================== */
let searchTimer: number | null = null;
watch(searchModel, () => {
  if (searchTimer) window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => fetchPage(1), 350);
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
  ],
});

/* ===========================
 *  PAGINATION HANDLERS
 * =========================== */
function handlePageSizeChange(size: number) {
  // composable watches tablePageSize and will fetchPage(1) automatically
  prefs.setTablePageSize(size);
}

/* ===========================
 *  MOUNT
 * =========================== */
onMounted(() => fetchPage(1));
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
      v-model:searchModelValue="searchModel"
      @refresh="() => fetchClasses(currentPage || 1)"
      @reset="
        () => {
          searchModel = '';
          fetchPage(1);
        }
      "
    >
      <template #actions>
        <BaseButton
          plain
          :loading="tableLoading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="() => fetchClasses(currentPage || 1)"
        >
          Refresh
        </BaseButton>

        <BaseButton
          type="primary"
          :disabled="tableLoading"
          @click="openCreateDialog"
        >
          Add Class
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-card>
      <ElAlert
        v-if="tableError"
        type="error"
        :closable="false"
        class="mb-3"
        title="Failed to load classes"
        :description="String(tableError?.message ?? tableError)"
      />

      <SmartTable
        :data="classes"
        :columns="classColumns"
        :loading="tableLoading"
      >
        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            :detailContent="`Manage students in ${row.name}`"
            deleteContent="Delete class"
            @detail="openManageStudentsDialog(row as AdminClassRow)"
            @delete="handleSoftDelete(row as AdminClassRow)"
            :deleteLoading="deleteLoading[row.id] ?? false"
            :detailLoading="detailLoading[row.id] ?? false"
          />
        </template>
      </SmartTable>

      <div v-if="!tableLoading && (classes?.length ?? 0) === 0" class="py-10">
        <ElEmpty description="No classes found" :image-size="110" />
      </div>
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
        @size-change="handlePageSizeChange"
      />
    </el-row>

    <!-- CREATE -->
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

    <!-- MANAGE STUDENTS / TEACHER -->
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
