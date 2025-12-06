<!-- ~/pages/teacher/grades/index.vue -->
<script setup lang="ts">
import { ref, watch, computed } from "vue";
import {
  ElMessage,
  ElMessageBox,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElInput,
  ElTag,
  ElDatePicker,
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

import ErrorBoundary from "~/components/error/ErrorBoundary.vue";

definePageMeta({
  layout: "teacher",
});

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
const gradeList = ref<GradeEnriched[]>([]);
const loading = ref(false);
const errorMessage = ref<string | null>(null);

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
    component: ElDatePicker,
    componentProps: {
      style: "width: '100%'",
      readonly: true,
      disabled: true,
      format: "DD-MM-YYYY HH:mm:ss",
      type: "datetime",
      valueFormat: "YYYY-MM-DD HH:mm:ss",
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
      valueKey: "id",
      labelKey: "username",
      multiple: false,
      placeholder: "Select student",
    },
  },
  {
    key: "subject_id",
    label: "Subject",
    component: TeacherSubjectSelect,
    componentProps: {
      classId: selectedClassId.value || "",
      placeholder: "Select subject",
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

const totalGrades = computed(() => gradeList.value.length);

const averageScore = computed(() => {
  if (!gradeList.value.length) return null;
  const sum = gradeList.value.reduce((acc, g) => acc + Number(g.score ?? 0), 0);
  return Math.round((sum / gradeList.value.length) * 10) / 10;
});

/* ---------------------- load grades -------------------------- */

const loadGrades = async () => {
  if (!selectedClassId.value) {
    gradeList.value = [];
    return;
  }

  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await teacherApi.teacher.listGradesForClass(
      selectedClassId.value,
      { showError: false }
    );

    if (!res) {
      errorMessage.value = "Failed to load grades.";
      gradeList.value = [];
      return;
    }

    gradeList.value = (res.items ?? []) as GradeEnriched[];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load grades.";
  } finally {
    loading.value = false;
  }
};

watch(
  () => selectedClassId.value,
  () => {
    loadGrades();
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
    ElMessage.success("Grade updated.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to update grade.");
  }
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
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- Header (consistent gradient style) -->
    <div
      class="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-[var(--color-primary-light-9)] to-[var(--color-primary-light-9)] border border-[color:var(--color-primary-light-9)] shadow-sm rounded-2xl p-5"
    >
      <div class="space-y-2">
        <h1
          class="text-2xl font-bold flex items-center gap-2 text-[color:var(--color-dark)]"
        >
          Grades
        </h1>
        <p class="text-sm text-[color:var(--color-primary-light-1)]">
          Record and review student grades for the selected class.
        </p>

        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Class:</span>
            <TeacherClassSelect
              v-model="selectedClassId"
              placeholder="Select class"
              style="min-width: 220px"
            />
          </div>

          <div class="flex flex-wrap items-center gap-2 text-xs">
            <span
              v-if="totalGrades"
              class="inline-flex items-center gap-1 rounded-full bg-[var(--color-primary-light-8)] text-[color:var(--color-primary)] px-3 py-0.5 border border-[var(--color-primary-light-5)]"
            >
              <span
                class="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]"
              />
              {{ totalGrades }}
              {{ totalGrades === 1 ? "grade" : "grades" }}
            </span>

            <span
              v-if="averageScore !== null"
              class="inline-flex items-center gap-1 rounded-full bg-white text-gray-700 px-3 py-0.5 border border-gray-200"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Avg score:
              <span class="font-medium">{{ averageScore }}</span>
            </span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2 justify-end">
        <BaseButton
          plain
          :loading="loading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="loadGrades"
        >
          Refresh
        </BaseButton>
        <BaseButton
          type="primary"
          :disabled="!selectedClassId"
          :loading="loading"
          @click="handleOpenAddDialog"
        >
          Add grade
        </BaseButton>
      </div>
    </div>

    <!-- Error -->
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

    <!-- Table card -->
    <el-card
      shadow="never"
      :body-style="{ padding: '20px' }"
      class="rounded-2xl border border-gray-200/60 shadow-sm bg-white"
    >
      <template #header>
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
        >
          <div>
            <div class="text-base font-semibold text-gray-800">Grade list</div>
            <p class="text-xs text-gray-500">
              Each row represents one grade item (exam or assignment).
            </p>
          </div>
        </div>
      </template>

      <ErrorBoundary>
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
        </SmartTable>
      </ErrorBoundary>

      <div v-if="!loading && !gradeList.length" class="py-10">
        <el-empty
          :description="
            selectedClassId
              ? 'No grades for this class yet'
              : 'Select a class to see grades'
          "
          :image-size="120"
        >
          <template #extra>
            <p class="text-sm text-gray-500 max-w-md mx-auto">
              {{
                selectedClassId
                  ? "Use the Add grade button to create the first record."
                  : "Choose a class from the top to load its grades."
              }}
            </p>
          </template>
        </el-empty>
      </div>
    </el-card>

    <!-- Add Grade Dialog -->
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

    <!-- Edit Grade Dialog (score only) -->
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
/* Table looks a bit smoother */
:deep(.el-table) {
  border-radius: 0.75rem;
}

/* Score tags stay readable on hover */
:deep(.el-tag) {
  font-size: 12px;
}
</style>
