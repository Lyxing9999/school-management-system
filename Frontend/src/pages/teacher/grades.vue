<script setup lang="ts">
import { ref, watch } from "vue";
import { teacherService } from "~/api/teacher";
import TeacherClassSelect from "~/components/Selects/TeacherClassSelect.vue";
import TeacherStudentSelect from "~/components/Selects/TeacherStudentSelect.vue";
import TeacherSubjectSelect from "~/components/Selects/TeacherSubjectSelect.vue";
import type { GradeDTO, GradeType } from "~/api/types/school.dto";
import { ElMessage } from "element-plus";

definePageMeta({
  layout: "teacher",
});

const teacherApi = teacherService();

const selectedClassId = ref<string | null>(null);
const gradeList = ref<GradeDTO[]>([]);
const loading = ref(false);
const errorMessage = ref<string | null>(null);

const gradeForm = ref<{
  student_id: string;
  subject_id: string;
  score: number | null;
  type: GradeType | "";
  term: string;
}>({
  student_id: "",
  subject_id: "",
  score: 50,
  type: "" as GradeType | "",
  term: "",
});

const updateScoreForm = ref<{
  grade_id: string;
  score: number | null;
}>({
  grade_id: "",
  score: null,
});

const changeTypeForm = ref<{
  grade_id: string;
  type: GradeType | "";
}>({
  grade_id: "",
  type: "" as GradeType | "",
});

const loadGrades = async () => {
  if (!selectedClassId.value) {
    gradeList.value = [];
    return;
  }
  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await teacherApi.teacher.listGradesForClass(
      selectedClassId.value
    );
    gradeList.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load grades.";
    ElMessage.error(errorMessage.value);
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
    const dto = await teacherApi.teacher.addGrade({
      student_id: form.student_id,
      subject_id: form.subject_id,
      class_id: selectedClassId.value,
      score: form.score,
      type: form.type as GradeType,
      term: form.term || undefined,
    });

    gradeList.value.unshift(dto);
    ElMessage.success("Grade added.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to add grade.");
  }
};

const submitUpdateScore = async () => {
  const form = updateScoreForm.value;
  if (!form.grade_id || form.score == null) {
    ElMessage.warning("Grade ID and new score are required.");
    return;
  }

  try {
    const dto = await teacherApi.teacher.updateGradeScore(form.grade_id, {
      score: form.score,
    });
    const idx = gradeList.value.findIndex((g) => g.id === dto.id);
    if (idx !== -1) gradeList.value[idx] = dto;
    ElMessage.success("Score updated.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to update score.");
  }
};

const submitChangeGradeType = async () => {
  const form = changeTypeForm.value;
  if (!form.grade_id || !form.type) {
    ElMessage.warning("Grade ID and type are required.");
    return;
  }

  try {
    const dto = await teacherApi.teacher.changeGradeType(form.grade_id, {
      type: form.type as GradeType,
    });
    const idx = gradeList.value.findIndex((g) => g.id === dto.id);
    if (idx !== -1) gradeList.value[idx] = dto;
    ElMessage.success("Grade type updated.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to update type.");
  }
};
</script>

<template>
  <div class="p-4 space-y-6">
    <el-row justify="space-between" align="middle">
      <el-col :span="12">
        <h1 class="text-xl font-semibold mb-2">Grades</h1>

        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">Class:</span>
          <TeacherClassSelect
            v-model="selectedClassId"
            placeholder="Select class"
            style="min-width: 220px"
          />
        </div>
      </el-col>

      <el-col :span="12" class="text-right">
        <el-button type="primary" :loading="loading" @click="loadGrades">
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mt-2"
    />

    <el-skeleton v-if="loading" :rows="4" animated />

    <el-row v-else :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover">
          <template #header>
            <span class="font-semibold">Add grade</span>
          </template>

          <el-form :model="gradeForm" label-width="110px" size="small">
            <el-form-item label="Student">
              <TeacherStudentSelect
                v-model="gradeForm.student_id"
                :class-id="selectedClassId || ''"
                :reload="true"
                value-key="id"
                label-key="username"
                :multiple="false"
                placeholder="Select student"
              />
            </el-form-item>

            <el-form-item label="Subject">
              <TeacherSubjectSelect
                v-model="gradeForm.subject_id"
                :class-id="selectedClassId || ''"
                placeholder="Select subject"
              />
            </el-form-item>

            <el-form-item label="Score (0–100)">
              <el-input-number
                v-model="gradeForm.score"
                :min="0"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="Type">
              <el-select v-model="gradeForm.type" placeholder="Select type">
                <el-option label="Exam" value="exam" />
                <el-option label="Assignment" value="assignment" />
              </el-select>
            </el-form-item>

            <el-form-item label="Term">
              <el-input v-model="gradeForm.term" placeholder="e.g. 2024-S1" />
            </el-form-item>

            <el-form-item>
              <el-button type="success" @click="submitAddGrade">
                Save grade
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="mb-4">
          <template #header>
            <span class="font-semibold">Update grade</span>
          </template>

          <el-row :gutter="12">
            <el-col :span="24" :md="12">
              <el-form :model="updateScoreForm" label-width="95px" size="small">
                <el-form-item label="Grade ID">
                  <el-input
                    v-model="updateScoreForm.grade_id"
                    placeholder="grade ObjectId"
                  />
                </el-form-item>
                <el-form-item label="New score">
                  <el-input-number
                    v-model="updateScoreForm.score"
                    :min="0"
                    :max="100"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="submitUpdateScore">
                    Update score
                  </el-button>
                </el-form-item>
              </el-form>
            </el-col>

            <el-col :span="24" :md="12">
              <el-form :model="changeTypeForm" label-width="95px" size="small">
                <el-form-item label="Grade ID">
                  <el-input
                    v-model="changeTypeForm.grade_id"
                    placeholder="grade ObjectId"
                  />
                </el-form-item>
                <el-form-item label="New type">
                  <el-select
                    v-model="changeTypeForm.type"
                    placeholder="Select type"
                  >
                    <el-option label="Exam" value="exam" />
                    <el-option label="Assignment" value="assignment" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="warning" @click="submitChangeGradeType">
                    Change type
                  </el-button>
                </el-form-item>
              </el-form>
            </el-col>
          </el-row>
        </el-card>

        <el-card shadow="hover">
          <template #header>
            <span class="font-semibold">Grades list</span>
          </template>

          <el-table
            v-if="gradeList.length"
            :data="gradeList"
            border
            size="small"
            height="320"
          >
            <el-table-column prop="class_name" label="Class" min-width="180" />
            <el-table-column
              prop="student_name"
              label="Student"
              min-width="180"
            />
            <el-table-column
              prop="subject_label"
              label="Subject"
              min-width="180"
            />
            <el-table-column prop="score" label="Score" min-width="80" />
            <el-table-column prop="type" label="Type" min-width="110" />
            <el-table-column prop="term" label="Term" min-width="110" />
          </el-table>

          <div
            v-else
            class="text-sm text-gray-500 italic text-center py-4 mt-2"
          >
            No grades for this class.
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
