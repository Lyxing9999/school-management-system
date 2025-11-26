<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";

import { studentService } from "~/api/student";

import type {
  ClassSectionDTO,
  AttendanceDTO,
  GradeDTO,
} from "~/api/types/school.dto";
import type {
  StudentAttendanceFilterDTO,
  StudentGradesFilterDTO,
  StudentScheduleFilterDTO,
  StudentScheduleListDTO,
} from "~/api/student/dto";

definePageMeta({
  layout: "student",
});

const route = useRoute();
const student = studentService();

const classId = computed(() => route.params.classId as string);

// ------------ state ------------
const loading = ref(true);
const errorMessage = ref<string | null>(null);

const currentClass = ref<ClassSectionDTO | null>(null);

const attendanceList = ref<AttendanceDTO[]>([]);
const attendanceLoading = ref(false);

const gradeList = ref<GradeDTO[]>([]);
const gradeLoading = ref(false);
const termFilter = ref<string>("");

const fullSchedule = ref<StudentScheduleListDTO["items"] | any[]>([]);
const scheduleLoading = ref(false);

// computed: schedule only for this class
const scheduleForClass = computed(() =>
  (fullSchedule.value ?? []).filter(
    (slot: any) => String(slot.class_id) === String(classId.value)
  )
);

// ------------ load helpers ------------

const loadClassInfo = async () => {
  // naive: re-use getMyClasses and find this class
  const res = await student.student.getMyClasses();
  currentClass.value =
    res.items.find((c: ClassSectionDTO) => c.id === classId.value) ?? null;
};

const loadAttendance = async () => {
  attendanceLoading.value = true;
  try {
    const params: StudentAttendanceFilterDTO = {
      // assuming filter type has this field; backend will ignore unknown keys safely
      class_id: classId.value as any,
    };
    const res = await student.student.getMyAttendance(params);
    attendanceList.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to load attendance.");
  } finally {
    attendanceLoading.value = false;
  }
};

const loadGrades = async () => {
  gradeLoading.value = true;
  try {
    const params: StudentGradesFilterDTO = {} as any;
    if (termFilter.value) {
      (params as any).term = termFilter.value;
    }
    const res = await student.student.getMyGrades(params);
    // you might want to filter by class_id on client if DTO has class_id
    gradeList.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to load grades.");
  } finally {
    gradeLoading.value = false;
  }
};

const loadSchedule = async () => {
  scheduleLoading.value = true;
  try {
    const params: StudentScheduleFilterDTO = {} as any;
    const res = await student.student.getMySchedule(params);
    fullSchedule.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to load schedule.");
  } finally {
    scheduleLoading.value = false;
  }
};

const loadAll = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    await Promise.all([
      loadClassInfo(),
      loadAttendance(),
      loadGrades(),
      loadSchedule(),
    ]);
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load class details.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

const applyTermFilter = async () => {
  await loadGrades();
};

onMounted(loadAll);
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
      class="mb-2"
    />

    <el-skeleton v-if="loading" :rows="4" animated />

    <el-row v-else :gutter="16">
      <!-- Attendance column -->
      <el-col :xs="24" :lg="12" class="space-y-4">
        <el-card shadow="hover">
          <template #header>
            <span class="font-semibold">My Attendance (this class)</span>
          </template>

          <el-table
            :data="attendanceList"
            border
            size="small"
            height="360"
            v-loading="attendanceLoading"
          >
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
            <el-table-column
              prop="class_id"
              label="Class ID"
              min-width="220"
              show-overflow-tooltip
            />
          </el-table>

          <div
            v-if="!attendanceLoading && !attendanceList.length"
            class="text-sm text-gray-500 italic text-center py-4 mt-2"
          >
            No attendance records for this class yet.
          </div>
        </el-card>
      </el-col>

      <!-- Grades + Schedule column -->
      <el-col :xs="24" :lg="12" class="space-y-4">
        <!-- Grades -->
        <el-card shadow="hover">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-semibold">My Grades</span>

              <div class="flex items-center gap-2">
                <el-input
                  v-model="termFilter"
                  placeholder="Filter by term (e.g. 2024-S1)"
                  size="small"
                  style="width: 200px"
                  clearable
                />
                <el-button size="small" type="primary" @click="applyTermFilter">
                  Apply
                </el-button>
              </div>
            </div>
          </template>

          <el-table
            :data="gradeList"
            border
            size="small"
            height="260"
            v-loading="gradeLoading"
          >
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
              min-width="220"
              show-overflow-tooltip
            />
          </el-table>

          <div
            v-if="!gradeLoading && !gradeList.length"
            class="text-sm text-gray-500 italic text-center py-3"
          >
            No grades yet.
          </div>
        </el-card>

        <!-- Schedule -->
        <el-card shadow="hover">
          <template #header>
            <span class="font-semibold">Schedule (this class)</span>
          </template>

          <el-table
            :data="scheduleForClass"
            size="small"
            border
            height="220"
            v-loading="scheduleLoading"
          >
            <el-table-column
              prop="day_of_week"
              label="Day"
              min-width="100"
              :formatter="(row) => row.day_of_week"
            />
            <el-table-column prop="start_time" label="Start" min-width="100" />
            <el-table-column prop="end_time" label="End" min-width="100" />
            <el-table-column prop="room" label="Room" min-width="100" />
          </el-table>

          <div
            v-if="!scheduleLoading && !scheduleForClass.length"
            class="text-sm text-gray-500 italic text-center py-3"
          >
            No schedule slots for this class yet.
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
