<!-- ~/pages/teacher/grades/index.vue -->
<script setup lang="ts">
definePageMeta({
  layout: "teacher",
});

import { ref, watch, computed } from "vue";
import {
  ElMessage,
  ElMessageBox,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElInput,
  ElTag,
} from "element-plus";

import { teacherService } from "~/api/teacher";
import type { GradeDTO, GradeType } from "~/api/types/school.dto";

import TeacherClassSelect from "~/components/Selects/TeacherClassSelect.vue";
import TeacherStudentSelect from "~/components/Selects/TeacherClassStudentSelect.vue";
import TeacherSubjectSelect from "~/components/Selects/TeacherSubjectSelect.vue";

import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { Field } from "~/components/types/form";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";

import ActionButtons from "~/components/Button/ActionButtons.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";

import { useHeaderState } from "~/composables/useHeaderState";
import { usePaginatedFetch } from "~/composables/usePaginatedFetch";
import TableCard from "~/components/Cards/TableCard.vue";
const teacherApi = teacherService();

/**
 * Enriched grade from backend:
 * {
 *   id, score, type, term, created_at, ...
 *   student_name, class_name, subject_label, teacher_name
 * }
 */
type GradeEnriched = GradeDTO & {
  student_name?: string;
  class_name?: string;
  subject_label?: string;
  teacher_name?: string;
};

const selectedClassId = ref<string | null>(null);
const errorMessage = ref<string | null>(null);

/* ---------------------- pagination hook ---------------------- */

const {
  data: gradeList,
  loading,
  error,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<GradeEnriched, string | null>(
  async (classId, page, pageSize, signal) => {
    if (!classId) {
      return { items: [], total: 0 };
    }

    const res = await teacherApi.teacher.listGradesForClass(classId, {
      page,
      page_size: pageSize,
      signal,
      showError: false,
    });

    // PRE mode: backend returns all items, we slice on frontend
    const allItems = (res?.items ?? []) as GradeEnriched[];
    const total = res?.total ?? allItems.length;

    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const pageItems = allItems.slice(start, end);

    return {
      items: pageItems,
      total,
    };

    // LATER (real backend pagination):
    // return {
    //   items: (res?.items ?? []) as GradeEnriched[],
    //   total: res?.total ?? res?.items?.length ?? 0,
    // };
  },
  1,
  10,
  selectedClassId
);

/* ---------------------- forms & dialogs ---------------------- */

type GradeFormModel = {
  student_id: string;
  subject_id: string;
  score: number | null;
  type: GradeType | "";
  term: string;
};

type EditGradeFormModel = {
  grade_id: string;
  score: number | null;
};

const gradeForm = ref<GradeFormModel>({
  student_id: "",
  subject_id: "",
  score: 50,
  type: "" as GradeType | "",
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

/* ---------------------- table columns ------------------------ */

const gradeColumns: ColumnConfig<GradeEnriched>[] = [
  {
    key: "student_name",
    label: "Student",
    field: "student_name",
  },
  {
    key: "subject_label",
    label: "Subject",
    field: "subject_label",
  },
  {
    key: "score",
    label: "Score",
    field: "score",
    render: (row: GradeEnriched) => {
      const score = Number(row.score ?? 0);

      let type: "success" | "warning" | "danger" | "info" = "info";
      if (score >= 90) type = "success";
      else if (score >= 70) type = "warning";
      else type = "danger";

      return {
        component: ElTag,
        componentProps: {
          type,
          effect: "plain",
          size: "small",
        },
        value: `${score} / 100`,
      };
    },
  },
  {
    key: "type",
    label: "Type",
    field: "type",
    render: (row: GradeEnriched) => {
      const t = row.type;

      const map: Record<
        string,
        { type: "success" | "warning" | "danger" | "info"; label: string }
      > = {
        exam: { type: "success", label: "Exam" },
        assignment: { type: "warning", label: "Assignment" },
        homework: { type: "info", label: "Homework" },
        quiz: { type: "warning", label: "Quiz" },
      };

      const config = map[t] ?? { type: "info", label: t || "N/A" };

      return {
        component: ElTag,
        componentProps: {
          type: config.type,
          effect: "plain",
          size: "small",
        },
        value: config.label,
      };
    },
  },
  {
    key: "term",
    label: "Term",
    field: "term",
  },
  {
    field: "created_at",
    label: "Created At",
    inlineEditActive: true,
    minWidth: "160px",
    component: ElInput,
    componentProps: {
      style: "width: 100%",

      readonly: true,
      disabled: true,
    },
  },
  {
    label: "Actions",
    slotName: "operation",
    operation: true,
    fixed: "right",
    width: "250",
    align: "center",
  },
];

/* ---------------------- SmartForm fields --------------------- */

const addGradeFields = computed<Field<GradeFormModel>[]>(() => [
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
    componentProps: {
      min: 0,
      max: 100,
      style: "width: 100%",
    },
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
    componentProps: {
      placeholder: "Select type",
      style: "width: 100%",
    },
  },
  {
    key: "term",
    label: "Term",
    component: ElInput,
    componentProps: {
      placeholder: "e.g. 2024-S1",
    },
  },
]);

const editGradeFields: Field<EditGradeFormModel>[] = [
  {
    key: "grade_id",
    label: "Grade ID",
    component: ElInput,
    componentProps: {
      disabled: true,
    },
  },
  {
    key: "score",
    label: "Score (0–100)",
    component: ElInputNumber,
    componentProps: {
      min: 0,
      max: 100,
      style: "width: 100%",
    },
  },
];

/* ---------------------- derived stats ------------------------ */

const totalGrades = computed(() => totalRows.value);

const averageScore = computed(() => {
  if (!gradeList.value.length) return null;
  const sum = gradeList.value.reduce((acc, g) => acc + Number(g.score ?? 0), 0);
  return Math.round((sum / gradeList.value.length) * 10) / 10;
});

/* ---------------------- load / watch ------------------------- */

const loadGrades = async () => {
  errorMessage.value = null;
  await fetchPage(currentPage.value || 1);
  if (error.value) {
    errorMessage.value = error.value.message ?? "Failed to load grades.";
  }
};

watch(
  () => selectedClassId.value,
  async () => {
    if (!selectedClassId.value) {
      gradeList.value = [];
      return;
    }
    await fetchPage(1);
    if (error.value) {
      errorMessage.value = error.value.message ?? "Failed to load grades.";
    } else {
      errorMessage.value = null;
    }
  }
);

/* ---------------------- add grade ---------------------------- */

const submitAddGrade = async () => {
  const form = gradeForm.value;

  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }

  if (
    !form.student_id ||
    !form.subject_id ||
    form.score == null ||
    !form.type
  ) {
    ElMessage.warning("Student, subject, score and type are required.");
    return;
  }

  try {
    const dto = await teacherApi.teacher.addGrade(
      {
        student_id: form.student_id,
        subject_id: form.subject_id,
        class_id: selectedClassId.value,
        score: form.score,
        type: form.type as GradeType,
        term: form.term || undefined,
      },
      { showError: false }
    );

    if (!dto) {
      ElMessage.error("Failed to add grade.");
      return;
    }

    await loadGrades();
    ElMessage.success("Grade added.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to add grade.");
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
    type: "" as GradeType | "",
    term: "",
  };
  addDialogVisible.value = true;
};

const handleSaveAddDialog = async (payload: Partial<GradeFormModel>) => {
  gradeForm.value = { ...gradeForm.value, ...payload };
  addDialogLoading.value = true;
  try {
    await submitAddGrade();
    addDialogVisible.value = false;
  } finally {
    addDialogLoading.value = false;
  }
};

const handleCancelAddDialog = () => {
  addDialogVisible.value = false;
};

/* ---------------------- edit grade --------------------------- */

const openEditGradeDialog = (row: GradeEnriched) => {
  editGradeForm.value = {
    grade_id: row.id,
    score: row.score,
  };
  editDialogVisible.value = true;
};

const submitEditGrade = async () => {
  const form = editGradeForm.value;

  if (!form.grade_id) {
    ElMessage.warning("Missing grade ID.");
    return;
  }
  if (form.score == null) {
    ElMessage.warning("Score is required.");
    return;
  }

  try {
    await teacherApi.teacher.updateGradeScore(
      form.grade_id,
      { score: form.score },
      { showError: false }
    );

    await loadGrades();
  } catch (err: any) {}
};

const handleSaveEditDialog = async (payload: Partial<EditGradeFormModel>) => {
  editGradeForm.value = { ...editGradeForm.value, ...payload };
  editDialogLoading.value = true;
  try {
    await submitEditGrade();
    editDialogVisible.value = false;
  } finally {
    editDialogLoading.value = false;
  }
};

const handleCancelEditDialog = () => {
  editDialogVisible.value = false;
};

/* ---------------------- delete grade (future API) ------------ */

const handleDeleteGrade = async (row: GradeEnriched) => {
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

    // TODO: when backend delete is ready:
    // await teacherApi.teacher.deleteGrade(row.id, { showError: false });

    gradeList.value = gradeList.value.filter((g) => g.id !== row.id);

    ElMessage.success("Grade removed.");
  } catch {
    // user cancelled
  }
};

/* ---------------------- header stats via composable ----------- */

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
          : `Average score: ${averageScore.value}`,
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});

/* ---------------------- pagination handlers ------------------ */

const handlePageChange = (page: number) => {
  goPage(page);
};

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  fetchPage(1);
};
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- HEADER -->
    <OverviewHeader
      title="Grades"
      description="Record and review student grades for the selected class."
      :loading="loading"
      :stats="headerState"
      :showRefresh="false"
    >
      <!-- Left-side filters -->
      <template #filters>
        <div class="flex flex-wrap items-center gap-3">
          <div
            class="flex items-center gap-2 px-3 py-1.5 rounded-full border shadow-sm"
            style="
              background: var(--color-card);
              border-color: var(--color-primary-light-7);
            "
          >
            <span
              class="text-xs font-medium"
              style="color: var(--color-primary)"
            >
              Class:
            </span>

            <TeacherClassSelect
              v-model="selectedClassId"
              placeholder="Select class"
              style="min-width: 220px"
              class="header-class-select"
            />
          </div>
        </div>
      </template>
      <!-- Right-side actions -->
      <template #actions>
        <BaseButton
          plain
          :loading="loading"
          :disabled="!selectedClassId || loading"
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
      </template>
    </OverviewHeader>

    <!-- ERROR -->
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

    <!-- TABLE CARD -->
    <TableCard
      title="Grade list"
      description="Each row represents one grade item (exam or assignment)."
      :rightText="`Showing ${gradeList.length} / ${totalGrades} records`"
    >
      <SmartTable
        :data="gradeList"
        :columns="gradeColumns"
        :loading="loading"
        :smartProps="{
          border: true,
          size: 'small',
          'highlight-current-row': true,
        }"
      >
        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            :detailContent="`Edit ${
              row.type.charAt(0).toUpperCase() + row.type.slice(1)
            }`"
            :deleteContent="`Remove ${
              row.type.charAt(0).toUpperCase() + row.type.slice(1)
            }`"
            @detail="openEditGradeDialog(row)"
            @delete="handleDeleteGrade(row)"
          />
        </template>
        <!-- Pagination -->
        <div v-if="totalRows > 0" class="mt-4 flex justify-end">
          <el-pagination
            background
            layout="prev, pager, next, jumper, sizes, total"
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRows"
            @current-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>
      </SmartTable>
    </TableCard>

    <!-- ADD GRADE DIALOG -->
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

    <!-- EDIT GRADE DIALOG -->
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
