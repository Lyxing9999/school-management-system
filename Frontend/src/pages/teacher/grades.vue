<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, watch, computed, onBeforeUnmount } from "vue";
import { storeToRefs } from "pinia";
import {
  ElMessage,
  ElMessageBox,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElInput,
  ElForm,
  ElFormItem,
} from "element-plus";

import { teacherService } from "~/api/teacher";
import type { GradeType } from "~/api/types/school.dto";
import type {
  TeacherAddGradeDTO,
  TeacherUpdateGradeScoreDTO,
  TeacherGradePagedDTO,
  GradeEnriched,
} from "~/api/teacher/dto";

import TeacherClassSelect from "~/components/selects/class/TeacherClassSelect.vue";
import TeacherStudentSelect from "~/components/selects/subject/TeacherClassStudentSelect.vue";
import TeacherSubjectSelect from "~/components/selects/subject/TeacherSubjectSelect.vue";

import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";

import type { Field } from "~/components/types/form";
import SmartFormDialog from "~/components/form/SmartFormDialog.vue";

import ActionButtons from "~/components/buttons/ActionButtons.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";

import { useHeaderState } from "~/composables/ui/useHeaderState";
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { reportError } from "~/utils/errors/errors";
import { usePreferencesStore } from "~/stores/preferencesStore";

const teacherApi = teacherService();

/* ---------------------- selection / errors ---------------------- */

const selectedClassId = ref<string | null>(null);
const errorMessage = ref<string | null>(null);
const detailLoadingId = ref<string | null>(null);
const deleteLoadingId = ref<string | null>(null);

const isDetailLoading = (id: string) => detailLoadingId.value === id;
const isDeleteLoading = (id: string) => deleteLoadingId.value === id;

import { buildTeacherGradeColumns } from "~/features/teacher-grade/columns";

const gradeColumns = computed(() =>
  buildTeacherGradeColumns({
    onEdit: openEditGradeDialog,
    onDelete: handleDeleteGrade,
  })
);

/* ---------------------- term dropdown --------------------------- */

type TermShort = "" | "S1" | "S2";

const termOptions: Array<{ label: string; value: Exclude<TermShort, ""> }> = [
  { label: "Semester 1", value: "S1" },
  { label: "Semester 2", value: "S2" },
];

function buildTermFull(short: TermShort, year = new Date().getFullYear()) {
  if (!short) return null;
  return `${year}-${short}`; // "2026-S1"
}

/* ---------------------- header filters -------------------------- */

const filterTerm = ref<TermShort>("");
const filterType = ref<GradeType | "">("");
const filterQuery = ref<string>("");

/* ---------------------- debounce search ------------------------- */

const debouncedQuery = ref<string>("");
let queryTimer: ReturnType<typeof setTimeout> | null = null;
const DEBOUNCE_MS = 350;

watch(
  filterQuery,
  (v) => {
    if (queryTimer) clearTimeout(queryTimer);
    queryTimer = setTimeout(() => {
      debouncedQuery.value = (v || "").trim();
    }, DEBOUNCE_MS);
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  if (queryTimer) clearTimeout(queryTimer);
});

/* ---------------------- preferences page size ------------------- */

const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);
const pageSizeOptions = computed(() => prefs.getAllowedPageSizes());

/* ---------------------- fetch page helper ----------------------- */

function unwrapPaged(
  res: TeacherGradePagedDTO | null | any
): TeacherGradePagedDTO {
  const payload = (res as any)?.data ?? res;
  return payload as TeacherGradePagedDTO;
}

/* ---------------------- pagination hook ------------------------- */

const {
  data: gradeList,
  fetching,
  initialLoading,
  error,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<GradeEnriched, string | null>(
  async (classId, page, size, signal) => {
    if (!classId) return { items: [], total: 0 };

    const term = filterTerm.value || undefined;
    const type = filterType.value || undefined;
    const q = debouncedQuery.value || undefined;
    const sort = "-created_at";

    const res = await teacherApi.teacher.listGradesForClass(
      classId,
      { page, page_size: size, term, type, q, sort },
      { signal, showError: false }
    );

    const payload = unwrapPaged(res);

    return {
      items: payload.items ?? [],
      total: Number(payload.total ?? 0),
    };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: selectedClassId,
  }
);

/* ---------------------- loading states -------------------------- */

const loading = computed(() => initialLoading.value || fetching.value);

/* ---------------------- forms & dialogs ------------------------- */

type AddGradeFormModel = Omit<
  TeacherAddGradeDTO,
  "type" | "term" | "class_id" | "score"
> & {
  type: GradeType | "";
  term: TermShort;
  score: number | null;
};

type EditGradeFormModel = Omit<TeacherUpdateGradeScoreDTO, "score"> & {
  grade_id: string;
  score: number | null;
};

const gradeForm = ref<AddGradeFormModel>({
  student_id: "",
  subject_id: "",
  score: 50,
  type: "",
  term: "",
});

const editGradeForm = ref<EditGradeFormModel>({
  grade_id: "",
  score: null,
});

const addDialogVisible = ref(false);
const addDialogLoading = ref(false);

const editDialogVisible = ref(false);
const editDialogLoading = ref(false);

/* ---------------------- SmartForm fields ------------------------ */

const addGradeFields = computed<Field<AddGradeFormModel>[]>(() => [
  {
    key: "student_id",
    label: "Student",
    component: TeacherStudentSelect,
    componentProps: {
      classId: selectedClassId.value || "",
      reload: true,
      multiple: false,
      placeholder: "Select student",
      disabled: !selectedClassId.value,
    },
  },
  {
    key: "subject_id",
    label: "Subject",
    component: TeacherSubjectSelect,
    componentProps: {
      classId: selectedClassId.value || "",
      placeholder: "Select subject",
      disabled: !selectedClassId.value,
    },
  },
  {
    key: "score",
    label: "Score (0–100)",
    component: ElInputNumber,
    componentProps: { min: 0, max: 100, style: "width: 100%" },
  },
  {
    key: "type",
    label: "Type",
    component: ElSelect,
    childComponent: ElOption,
    childComponentProps: {
      options: [
        { label: "Exam", value: "exam" },
        { label: "Assignment", value: "assignment" },
        { label: "Homework", value: "homework" },
        { label: "Quiz", value: "quiz" },
      ],
      labelKey: "label",
      valueKey: "value",
    },
    componentProps: { placeholder: "Select type", style: "width: 100%" },
  },
  {
    key: "term",
    label: "Term",
    component: ElSelect,
    childComponent: ElOption,
    childComponentProps: {
      options: termOptions,
      labelKey: "label",
      valueKey: "value",
    },
    componentProps: {
      placeholder: "Select term",
      clearable: true,
      style: "width: 100%",
    },
  },
]);

const editGradeFields: Field<EditGradeFormModel>[] = [
  {
    key: "grade_id",
    label: "Grade ID",
    component: ElInput,
    componentProps: { disabled: true },
  },
  {
    key: "score",
    label: "Score (0–100)",
    component: ElInputNumber,
    componentProps: { min: 0, max: 100, style: "width: 100%" },
  },
];

/* ---------------------- derived stats --------------------------- */

const totalGrades = computed(() => totalRows.value);
const hasClassSelected = computed(() => !!selectedClassId.value);
const isFirstLoad = computed(
  () => loading.value && gradeList.value.length === 0
);

const showingText = computed(() => {
  const total = totalRows.value || 0;
  if (!total) return "No records";
  const start = (currentPage.value - 1) * pageSize.value + 1;
  const end = Math.min(currentPage.value * pageSize.value, total);
  return `Showing ${start}-${end} of ${total}`;
});

const averageScore = computed(() => {
  if (!gradeList.value.length) return null;
  const sum = gradeList.value.reduce((acc, g) => acc + Number(g.score ?? 0), 0);
  return Math.round((sum / gradeList.value.length) * 10) / 10;
});

/* ---------------------- load / watch ---------------------------- */

async function resetAndFetch() {
  errorMessage.value = null;
  await fetchPage(1);
  errorMessage.value = error.value?.message ?? null;
}

const loadGrades = async () => {
  errorMessage.value = null;
  await fetchPage(currentPage.value || 1);
  if (error.value)
    errorMessage.value = error.value.message ?? "Failed to load grades.";
};

watch(
  () => selectedClassId.value,
  async (v) => {
    if (!v) {
      errorMessage.value = null;
      return;
    }
    await resetAndFetch();
  }
);

watch([filterTerm, filterType], async () => {
  if (!selectedClassId.value) return;
  await resetAndFetch();
});

watch(debouncedQuery, async () => {
  if (!selectedClassId.value) return;
  await resetAndFetch();
});

/* ---------------------- RESET BUTTON ---------------------------- */

const resetFilters = async () => {
  filterTerm.value = "";
  filterType.value = "";
  filterQuery.value = "";
  debouncedQuery.value = "";

  if (queryTimer) {
    clearTimeout(queryTimer);
    queryTimer = null;
  }

  if (selectedClassId.value) {
    await fetchPage(1);
  }
};

/* ---------------------- add grade ------------------------------- */

const submitAddGrade = async (): Promise<boolean> => {
  const form = gradeForm.value;

  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return false;
  }

  if (
    !form.student_id ||
    !form.subject_id ||
    form.score == null ||
    !form.type
  ) {
    ElMessage.warning("Student, subject, score and type are required.");
    return false;
  }

  try {
    const payload: TeacherAddGradeDTO = {
      student_id: form.student_id,
      subject_id: form.subject_id,
      class_id: selectedClassId.value,
      score: form.score,
      type: form.type as GradeType,
      term: buildTermFull(form.term),
    };

    const dto = await teacherApi.teacher.addGrade(payload, {
      showError: false,
    });

    if (!dto) {
      ElMessage.error("Failed to add grade.");
      return false;
    }

    await fetchPage(1);
    ElMessage.success("Grade added.");
    return true;
  } catch (err: any) {
    reportError(err, "grade.add.submit", "log");
    ElMessage.error("Failed to add grade.");
    return false;
  }
};

const handleOpenAddDialog = () => {
  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }
  gradeForm.value = {
    student_id: "",
    subject_id: "",
    score: 50,
    type: "",
    term: "",
  };
  addDialogVisible.value = true;
};

const handleSaveAddDialog = async (payload: Partial<AddGradeFormModel>) => {
  gradeForm.value = { ...gradeForm.value, ...payload };
  addDialogLoading.value = true;
  try {
    const ok = await submitAddGrade();
    if (ok) addDialogVisible.value = false;
  } finally {
    addDialogLoading.value = false;
  }
};

const handleCancelAddDialog = () => {
  addDialogVisible.value = false;
};

/* ---------------------- edit grade ------------------------------ */

const openEditGradeDialog = async (row: GradeEnriched) => {
  detailLoadingId.value = row.id;
  try {
    editGradeForm.value = { grade_id: row.id, score: row.score ?? null };
    editDialogVisible.value = true;
  } finally {
    detailLoadingId.value = null;
  }
};

const submitEditGrade = async (): Promise<boolean> => {
  const form = editGradeForm.value;

  if (!form.grade_id) {
    ElMessage.warning("Missing grade ID.");
    return false;
  }
  if (form.score == null) {
    ElMessage.warning("Score is required.");
    return false;
  }

  try {
    const payload: TeacherUpdateGradeScoreDTO = { score: form.score };

    await teacherApi.teacher.updateGradeScore(form.grade_id, payload, {
      showError: false,
    });

    await fetchPage(currentPage.value || 1);
    ElMessage.success("Grade updated.");
    return true;
  } catch (err: any) {
    reportError(err, "grade.edit.submit", "log");
    ElMessage.error("Failed to update grade.");
    return false;
  }
};

const handleSaveEditDialog = async (payload: Partial<EditGradeFormModel>) => {
  editGradeForm.value = { ...editGradeForm.value, ...payload };
  editDialogLoading.value = true;
  try {
    const ok = await submitEditGrade();
    if (ok) editDialogVisible.value = false;
  } finally {
    editDialogLoading.value = false;
  }
};

const handleCancelEditDialog = () => {
  editDialogVisible.value = false;
};



/* ---------------------- delete grade (UI only for now) ---------- */
const handleDeleteGrade = async (row: GradeEnriched) => {
  const id = String(row.id);
  deleteLoadingId.value = id;

  try {
    await ElMessageBox.confirm(
      "Are you sure you want to remove this grade?",
      "Confirm",
      {
        type: "warning",
        confirmButtonText: "Yes",
        cancelButtonText: "No",
      }
    );

    const res = await teacherApi.teacher.softDeleteGrade(id, {
      showError: false,
      showSuccess: true,
    });

    if (!res) {
      ElMessage.error("Failed to delete grade.");
      return;
    }

    await fetchPage(currentPage.value || 1);
  } catch (err) {
    // cancel is not an error; ignore
  } finally {
    deleteLoadingId.value = null;
  }
};
/* ---------------------- header stats ---------------------------- */

const canAddGrade = computed(() => !!selectedClassId.value && !loading.value);

const { headerState } = useHeaderState({
  items: [
    {
      key: "total",
      getValue: () => totalGrades.value,
      singular: "grade",
      plural: "grades",
      variant: "primary",
      hideWhenZero: true,
    },
    {
      key: "avg",
      getValue: () => averageScore.value ?? 0,
      label: () =>
        averageScore.value === null
          ? undefined
          : `Average score (this page): ${averageScore.value}`,
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});

/* ---------------------- pagination handlers --------------------- */

const handlePageChange = (page: number) => {
  goPage(page);
};

const handlePageSizeChange = async (size: number) => {
  prefs.setTablePageSize(size);
  const next = prefs.getTablePageSize();
  pageSize.value = next;
  await fetchPage(1);
};
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="Grades"
      description="Record and review student grades for the selected class."
      :loading="loading"
      :stats="headerState"
      :showRefresh="false"
    >
      <template #filters>
        <!-- Responsive Element Plus filter form -->
        <el-form class="filters-form" label-position="top">
          <el-row :gutter="12">
            <!-- Class -->
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="Class">
                <TeacherClassSelect
                  v-model="selectedClassId"
                  placeholder="Select class"
                  class="w-full"
                />
              </el-form-item>
            </el-col>

            <!-- Term -->
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="Term">
                <el-select
                  v-model="filterTerm"
                  clearable
                  placeholder="All"
                  class="w-full"
                  :disabled="!hasClassSelected"
                >
                  <el-option
                    v-for="opt in termOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- Type -->
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="Type">
                <el-select
                  v-model="filterType"
                  clearable
                  placeholder="All"
                  class="w-full"
                  :disabled="!hasClassSelected"
                >
                  <el-option label="Exam" value="exam" />
                  <el-option label="Assignment" value="assignment" />
                  <el-option label="Homework" value="homework" />
                  <el-option label="Quiz" value="quiz" />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- Search -->
            <el-col :xs="24" :sm="12" :md="12" :lg="6">
              <el-form-item label="Search">
                <el-input
                  v-model="filterQuery"
                  clearable
                  placeholder="Student, subject, term..."
                  class="w-full"
                  :disabled="!hasClassSelected"
                />
              </el-form-item>
            </el-col>

            <!-- Reset button (aligns nicely as a column) -->
            <el-col :xs="24" :sm="12" :md="6" :lg="4">
              <el-form-item label=" ">
                <BaseButton
                  plain
                  class="w-full !border-[color:var(--border-color)] !text-[color:var(--text-color)] hover:!bg-[var(--hover-bg)]"
                  :disabled="!hasClassSelected || loading"
                  @click="resetFilters"
                >
                  Reset
                </BaseButton>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </template>

      <template #actions>
        <div class="flex flex-wrap gap-2 justify-end">
          <BaseButton
            plain
            :loading="loading"
            :disabled="!hasClassSelected || loading"
            class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
            @click="loadGrades"
          >
            Refresh
          </BaseButton>

          <BaseButton
            type="primary"
            :disabled="!canAddGrade"
            :loading="loading"
            @click="handleOpenAddDialog"
          >
            Add grade
          </BaseButton>
        </div>
      </template>
    </OverviewHeader>

    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="rounded-xl border border-red-200/60 shadow-sm"
        @close="errorMessage = null"
      />
    </transition>

    <el-card v-if="isFirstLoad" shadow="never" class="rounded-xl">
      <el-skeleton animated :rows="7" />
    </el-card>

    <el-empty
      v-else-if="!hasClassSelected && !loading"
      description="Select a class to view grades."
      class="bg-white rounded-xl border"
    />

    <el-empty
      v-else-if="hasClassSelected && !loading && gradeList.length === 0"
      description="No grades recorded yet."
      class="bg-white rounded-xl border"
    />

    <TableCard
      v-else
      title="Grade list"
      description="Each row represents one grade item (exam, assignment, quiz, etc.)."
      :rightText="showingText"
    >
      <SmartTable :data="gradeList" :columns="gradeColumns" :loading="loading">
        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            :detailContent="`Edit ${String(row.type || 'grade')}`"
            :deleteContent="`Remove ${String(row.type || 'grade')}`"
            :detailLoading="isDetailLoading(row.id)"
            :deleteLoading="isDeleteLoading(row.id)"
            @detail="() => openEditGradeDialog(row)"
            @delete="() => handleDeleteGrade(row)"
          />
        </template>
      </SmartTable>

      <div v-if="totalRows > 0" class="mt-4 flex justify-end overflow-x-auto">
        <el-pagination
          background
          layout="prev, pager, next, jumper, sizes, total"
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="pageSizeOptions"
          :total="totalRows"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </TableCard>

    <SmartFormDialog
      v-model:visible="addDialogVisible"
      v-model="gradeForm"
      :fields="addGradeFields"
      title="Add grade"
      :loading="addDialogLoading"
      :width="'600px'"
      @save="handleSaveAddDialog"
      @cancel="handleCancelAddDialog"
    />

    <SmartFormDialog
      v-model:visible="editDialogVisible"
      v-model="editGradeForm"
      :fields="editGradeFields"
      title="Edit grade"
      :loading="editDialogLoading"
      :width="'500px'"
      @save="handleSaveEditDialog"
      @cancel="handleCancelEditDialog"
    />
  </div>
</template>

<style scoped>
/* default desktop/tablet inline layout */
.filters-form :deep(.el-form-item) {
  margin-bottom: 0;
}

/* Make each item a consistent width on desktop */
.filter-item {
  min-width: 220px;
}

/* Mobile: stacked filters, full width */
@media (max-width: 767px) {
  .filters-form {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
    align-items: start;
  }

  .filters-form :deep(.el-form-item) {
    margin-right: 0;
    margin-bottom: 0;
    width: 100%;
  }

  .filters-form :deep(.el-form-item__label) {
    /* nicer on mobile (above input) */
    display: block;
    width: 100%;
    padding: 0 0 4px 0;
    text-align: left;
    line-height: 1.1rem;
  }

  .filters-form :deep(.el-form-item__content) {
    width: 100%;
  }

  /* ensure selects/inputs expand */
  .filters-form :deep(.el-input),
  .filters-form :deep(.el-select) {
    width: 100%;
  }

  .filter-item {
    min-width: 0;
  }

  .filter-actions {
    width: 100%;
  }
}
</style>
