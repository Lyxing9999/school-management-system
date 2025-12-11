<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

import { studentService } from "~/api/student";

import { formatDate } from "~/utils/formatDate";

definePageMeta({
  layout: "student",
});

const student = studentService();

/* ------------------------------------------------
 * State
 * ------------------------------------------------ */

const loadingOverview = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<[]>([]);
const grades = ref<[]>([]);
const schedule = ref<[]>([]);
const attendance = ref<[]>([]);

// which class we use for dashboard attendance (MVP: first class)
const defaultClassId = ref<string | null>(null);

/* ------------------------------------------------
 * Load overview data (classes, grades, schedule, attendance)
 * ------------------------------------------------ */

const loadOverview = async () => {
  loadingOverview.value = true;
  errorMessage.value = null;

  try {
    // 1) load main data in parallel (classes, grades, schedule)
    const [classesRes, gradesRes, scheduleRes] = await Promise.all([
      student.student.getMyClasses(),
      student.student.getMyGrades({}), // no filter for now (MVP)
      student.student.getMySchedule(),
    ]);

    classes.value = classesRes.items ?? [];
    grades.value = gradesRes.items ?? [];
    schedule.value = scheduleRes.items ?? [];

    // pick a default class for attendance (first one)
    if (!defaultClassId.value && classes.value.length > 0) {
      defaultClassId.value = classes.value[0].id;
    }

    // 2) load attendance for the default class (MVP)
    if (defaultClassId.value) {
      const attendanceRes = await student.student.getMyAttendance({
        class_id: defaultClassId.value,
      });
      attendance.value = attendanceRes.items ?? [];
    } else {
      attendance.value = [];
    }
  } catch (err: any) {
  } finally {
    loadingOverview.value = false;
  }
};

/* ------------------------------------------------
 * Stats
 * ------------------------------------------------ */

const totalClasses = computed(() => classes.value.length);

const totalSubjects = computed(() => {
  const set = new Set<string>();
  for (const c of classes.value) {
    (c.subject_ids ?? []).forEach((sid: string) => set.add(sid));
  }
  return set.size;
});

const averageScore = computed(() => {
  if (!grades.value.length) return null;
  const total = grades.value.reduce((sum, g) => sum + g.score, 0);
  return total / grades.value.length;
});

// today of week: backend uses 1=Monday, 7=Sunday
const todayDayOfWeek = computed(() => {
  const jsDay = new Date().getDay(); // 0=Sunday..6=Saturday
  // Convert JS day to 1..7 with Monday=1
  return jsDay === 0 ? 7 : jsDay;
});

const todaySchedule = computed(() =>
  schedule.value.filter((s) => s.day_of_week === todayDayOfWeek.value)
);

const recentGrades = computed(() =>
  grades.value
    .slice()
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    .slice(0, 5)
);

// Most recent attendance records for the default class
const recentAttendance = computed(() =>
  attendance.value
    .slice()
    .sort(
      (a, b) =>
        new Date(b.record_date).getTime() - new Date(a.record_date).getTime()
    )
    .slice(0, 8)
);

/* ------------------------------------------------
 * Cambodia Holidays (FullCalendar)
 * ------------------------------------------------ */
import CambodiaCalendar from "~/components/Calendar/CambodiaCalendar.vue";

/* ------------------------------------------------
 * Lifecycle
 * ------------------------------------------------ */

onMounted(async () => {
  await loadOverview();
});
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Header -->
    <el-row justify="space-between" align="middle" class="mb-2">
      <el-col :span="18">
        <h1 class="text-xl font-semibold">Student Dashboard</h1>
        <p class="text-xs text-gray-500">
          Overview of your classes, schedule, grades, attendance, and upcoming
          holidays.
        </p>
        <p v-if="defaultClassId" class="text-[10px] text-gray-400 mt-1">
          Attendance on this dashboard is shown for your first class only (MVP).
        </p>
      </el-col>
      <el-col :span="6" class="text-right">
        <el-button
          type="primary"
          :loading="loadingOverview"
          @click="loadOverview"
        >
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <!-- Error -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-2"
    />

    <!-- Stats Row -->
    <el-row :gutter="16">
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Enrolled Classes</div>
          <div class="text-2xl font-semibold">
            {{ totalClasses }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Total Subjects</div>
          <div class="text-2xl font-semibold">
            {{ totalSubjects }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Average Score</div>
          <div class="text-2xl font-semibold">
            <span v-if="averageScore !== null">
              {{ averageScore.toFixed(1) }}
            </span>
            <span v-else class="text-gray-400">N/A</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Today&apos;s Lessons</div>
          <div class="text-2xl font-semibold">
            {{ todaySchedule.length }}
          </div>
          <div class="text-[10px] text-gray-400 mt-1">
            Based on your weekly schedule
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ONE ROW: Attendance (left) + Calendar & Today Schedule (right) -->
    <el-row :gutter="16">
      <!-- LEFT: Recent Attendance -->
      <el-col :xs="24" :md="14">
        <el-card shadow="hover">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Today&apos;s Schedule</div>
              <div class="text-xs text-gray-500">
                Lessons planned for today.
              </div>
            </div>
          </div>

          <el-table
            :data="todaySchedule"
            v-loading="loadingOverview"
            size="small"
            style="width: 100%"
            border
          >
            <el-table-column
              prop="class_name"
              label="Class"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column
              prop="teacher_name"
              label="Teacher"
              min-width="120"
              show-overflow-tooltip
            />
            <el-table-column label="Time" min-width="110">
              <template #default="{ row }">
                {{ row.start_time }} - {{ row.end_time }}
              </template>
            </el-table-column>
            <el-table-column
              prop="room"
              label="Room"
              min-width="90"
              show-overflow-tooltip
            />
          </el-table>

          <div
            v-if="!loadingOverview && !todaySchedule.length"
            class="text-center text-gray-500 text-xs py-3"
          >
            No lessons scheduled for today.
          </div>
        </el-card>
        <el-card shadow="hover">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Recent Grades</div>
              <div class="text-xs text-gray-500">
                Latest results across your subjects.
              </div>
            </div>
          </div>

          <el-table
            :data="recentGrades"
            v-loading="loadingOverview"
            size="small"
            style="width: 100%"
            border
          >
            <el-table-column
              prop="subject_label"
              label="Subject"
              min-width="180"
              show-overflow-tooltip
            />
            <el-table-column
              prop="class_name"
              label="Class"
              min-width="160"
              show-overflow-tooltip
            />
            <el-table-column prop="score" label="Score" min-width="80" />
            <el-table-column prop="type" label="Type" min-width="100" />
            <el-table-column
              prop="term"
              label="Term"
              min-width="120"
              show-overflow-tooltip
            />
            <el-table-column
              prop="created_at"
              label="Recorded At"
              min-width="180"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>

          <div
            v-if="!loadingOverview && !recentGrades.length"
            class="text-center text-gray-500 text-xs py-3"
          >
            No grades recorded yet.
          </div>
        </el-card>
      </el-col>

      <!-- RIGHT: Calendar + Today Schedule stacked -->
      <el-col :xs="24" :md="10">
        <!-- Cambodia holidays -->
        <el-card shadow="hover" class="mb-4">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Cambodia Holidays</div>
              <div class="text-xs text-gray-500">
                Public holidays from Calendarific.
              </div>
            </div>
          </div>

          <div>
            <CambodiaCalendar />
          </div>
        </el-card>

        <!-- Today’s schedule -->
      </el-col>
    </el-row>

    <!-- Recent Grades (full row under everything) -->
    <el-row :gutter="16">
      <el-col :xs="24" :md="24">
        <el-card shadow="hover">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Recent Attendance</div>
              <div class="text-xs text-gray-500">
                Latest attendance records for your first enrolled class.
              </div>
            </div>
          </div>

          <el-table
            :data="recentAttendance"
            v-loading="loadingOverview"
            size="small"
            style="width: 100%"
            border
          >
            <el-table-column prop="record_date" label="Date" min-width="130">
              <template #default="{ row }">
                {{ formatDate(row.record_date) }}
              </template>
            </el-table-column>

            <el-table-column
              prop="class_name"
              label="Class"
              min-width="160"
              show-overflow-tooltip
            />

            <el-table-column prop="status" label="Status" min-width="120">
              <template #default="{ row }">
                <el-tag
                  size="small"
                  :type="
                    row.status === 'present'
                      ? 'success'
                      : row.status === 'excused'
                      ? 'warning'
                      : 'danger'
                  "
                >
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column
              prop="teacher_name"
              label="Marked By"
              min-width="150"
              show-overflow-tooltip
            />

            <el-table-column
              prop="created_at"
              label="Recorded At"
              min-width="180"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>

          <div
            v-if="!loadingOverview && !recentAttendance.length"
            class="text-center text-gray-500 text-xs py-3"
          >
            No attendance records yet for this class.
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.slide-text {
  display: inline-block;
  white-space: nowrap;
}
</style>
