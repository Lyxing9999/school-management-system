<!-- ~/pages/teacher/classes/[classId].vue -->
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { teacherService } from "~/api/teacher";
import StudentSelect from "~/components/Selects/StudentSelect.vue";
import type {
  ClassSectionDTO,
  AttendanceDTO,
  GradeDTO,
  AttendanceStatus,
  GradeType,
} from "~/api/types/school.dto";
import { ElMessage } from "element-plus";

definePageMeta({
  layout: "teacher", // or your layout name
});

const route = useRoute();
const teacher = teacherService();

const classId = computed(() => route.params.classId as string);

// ---------------- state ----------------
const loading = ref(true);
const errorMessage = ref<string | null>(null);

const currentClass = ref<ClassSectionDTO | null>(null);
const attendanceList = ref<AttendanceDTO[]>([]);
const gradeList = ref<GradeDTO[]>([]);

// attendance form
const attendanceForm = ref<{
  student_id: string;
  status: AttendanceStatus | "";
  record_date: string;
}>({
  student_id: "",
  status: "" as AttendanceStatus | "",
  record_date: new Date().toISOString().slice(0, 10), // YYYY-MM-DD
});

// grade form
const gradeForm = ref<{
  student_id: string;
  subject_id: string;
  score: number | null;
  type: GradeType | "";
  term: string;
}>({
  student_id: "",
  subject_id: "",
  score: null,
  type: "" as GradeType | "",
  term: "",
});

// update score form
const updateScoreForm = ref<{
  grade_id: string;
  score: number | null;
}>({
  grade_id: "",
  score: null,
});

// change type form
const changeTypeForm = ref<{
  grade_id: string;
  type: GradeType | "";
}>({
  grade_id: "",
  type: "" as GradeType | "",
});

// -------------- load helpers --------------

const loadClass = async () => {
  const res = await teacher.teacher.getMyClasses();
  currentClass.value = res.items.find((c) => c.id === classId.value) ?? null;
};

const loadAttendance = async () => {
  const res = await teacher.teacher.listAttendanceForClass(classId.value);
  attendanceList.value = res.items ?? [];
};

const loadGrades = async () => {
  const res = await teacher.teacher.listGradesForClass(classId.value);
  gradeList.value = res.items ?? [];
};

const loadAll = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    await Promise.all([loadClass(), loadAttendance(), loadGrades()]);
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load class details.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

onMounted(loadAll);

// -------------- actions: attendance --------------

const submitAttendance = async () => {
  if (!attendanceForm.value.student_id || !attendanceForm.value.status) {
    ElMessage.warning("Student and status are required.");
    return;
  }

  try {
    const dto = await teacher.teacher.markAttendance({
      student_id: attendanceForm.value.student_id,
      class_id: classId.value,
      status: attendanceForm.value.status as AttendanceStatus,
      record_date: attendanceForm.value.record_date || undefined,
    });

    attendanceList.value.unshift(dto);
    ElMessage.success("Attendance recorded.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to record attendance.");
  }
};

const quickChangeAttendanceStatus = async (
  attendanceId: string,
  newStatus: AttendanceStatus
) => {
  try {
    const dto = await teacher.teacher.changeAttendanceStatus(attendanceId, {
      new_status: newStatus,
    });
    const idx = attendanceList.value.findIndex((a) => a.id === dto.id);
    if (idx !== -1) attendanceList.value[idx] = dto;
    ElMessage.success("Attendance updated.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to update status.");
  }
};

// -------------- actions: grades --------------

const submitAddGrade = async () => {
  const form = gradeForm.value;
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
    const dto = await teacher.teacher.addGrade({
      student_id: form.student_id,
      subject_id: form.subject_id,
      class_id: classId.value,
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
    const dto = await teacher.teacher.updateGradeScore(form.grade_id, {
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
    const dto = await teacher.teacher.changeGradeType(form.grade_id, {
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
    <!-- header -->
    <el-row justify="space-between" align="middle">
      <el-col :span="18">
        <h1 class="text-xl font-semibold">
          Class:
          <span v-if="currentClass">{{ currentClass.name }}</span>
          <span v-else class="text-gray-400">Loading...</span>
        </h1>
        <p v-if="currentClass" class="text-xs text-gray-500">
          ID: {{ currentClass.id }}
        </p>
      </el-col>
      <el-col :span="6" class="text-right">
        <el-button type="primary" :loading="loading" @click="loadAll">
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
    />

    <el-skeleton v-if="loading" :rows="4" animated />

    <el-row v-else :gutter="16">
      <!-- Attendance column -->
      <el-col :xs="24" :lg="12" class="space-y-4">
        <el-card shadow="hover">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-semibold">Attendance</span>
            </div>
          </template>

          <!-- form -->
          <el-form
            :model="attendanceForm"
            label-width="110px"
            size="small"
            class="mb-4"
          >
            <el-form-item label="Student ID">
              <StudentSelect
                v-model="attendanceForm.student_id"
                placeholder="student ObjectId"
              />
            </el-form-item>

            <el-form-item label="Status">
              <el-select v-model="attendanceForm.status" placeholder="Select">
                <el-option label="Present" value="present" />
                <el-option label="Absent" value="absent" />
                <el-option label="Excused" value="excused" />
              </el-select>
            </el-form-item>

            <el-form-item label="Date">
              <el-date-picker
                v-model="attendanceForm.record_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="Pick a day"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="submitAttendance">
                Save attendance
              </el-button>
            </el-form-item>
          </el-form>

          <!-- table -->
          <el-table
            :data="attendanceList"
            size="small"
            border
            height="320"
            v-if="attendanceList.length"
          >
            <el-table-column
              prop="student_id"
              label="Student ID"
              min-width="180"
            />
            <el-table-column prop="date" label="Date" min-width="120" />
            <el-table-column prop="status" label="Status" min-width="120">
              <template #default="{ row }">
                <el-tag
                  :type="
                    row.status === 'present'
                      ? 'success'
                      : row.status === 'excused'
                      ? 'warning'
                      : 'danger'
                  "
                  size="small"
                >
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="Actions" min-width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  size="small"
                  @click="quickChangeAttendanceStatus(row.id, 'present')"
                >
                  Present
                </el-button>
                <el-button
                  size="small"
                  @click="quickChangeAttendanceStatus(row.id, 'absent')"
                >
                  Absent
                </el-button>
                <el-button
                  size="small"
                  @click="quickChangeAttendanceStatus(row.id, 'excused')"
                >
                  Excused
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div
            v-else
            class="text-sm text-gray-500 italic text-center py-4 mt-2"
          >
            No attendance records yet.
          </div>
        </el-card>
      </el-col>

      <!-- Grades column -->
      <el-col :xs="24" :lg="12" class="space-y-4">
        <el-card shadow="hover">
          <template #header>
            <span class="font-semibold">Add Grade</span>
          </template>

          <el-form :model="gradeForm" label-width="110px" size="small">
            <el-form-item label="Student ID">
              <el-input
                v-model="gradeForm.student_id"
                placeholder="student ObjectId"
              />
            </el-form-item>

            <el-form-item label="Subject ID">
              <el-input
                v-model="gradeForm.subject_id"
                placeholder="subject ObjectId"
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

        <el-card shadow="hover">
          <template #header>
            <span class="font-semibold">Update Grade</span>
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
            <span class="font-semibold">Grades</span>
          </template>

          <el-table
            :data="gradeList"
            border
            size="small"
            height="320"
            v-if="gradeList.length"
          >
            <el-table-column
              prop="student_id"
              label="Student"
              min-width="180"
            />
            <el-table-column
              prop="subject_id"
              label="Subject"
              min-width="180"
            />
            <el-table-column prop="score" label="Score" min-width="80" />
            <el-table-column prop="type" label="Type" min-width="110" />
            <el-table-column prop="term" label="Term" min-width="110" />
            <el-table-column
              prop="id"
              label="Grade ID"
              min-width="260"
              show-overflow-tooltip
            />
          </el-table>

          <div
            v-else
            class="text-sm text-gray-500 italic text-center py-4 mt-2"
          >
            No grades yet.
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
