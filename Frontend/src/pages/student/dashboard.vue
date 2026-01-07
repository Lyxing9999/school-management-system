<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";

import { studentService } from "~/api/student";
import { formatDate } from "~/utils/date/formatDate";
import { reportError } from "~/utils/errors/errors";

import type {
  StudentClassListDTO,
  StudentAttendanceListDTO,
  StudentGradeListDTO,
  StudentScheduleListDTO,
} from "~/api/student/student.dto";

const student = studentService();

/* -----------------------------
 * Types (frontend view models)
 * ---------------------------- */

type ClassItem = StudentClassListDTO["items"][number] & {
  subject_labels?: string[];
  teacher_name?: string;
};

type AttendanceItem = StudentAttendanceListDTO["items"][number] & {
  class_name?: string;
  teacher_name?: string;
};

type GradeItem = StudentGradeListDTO["items"][number] & {
  subject_label?: string;
  class_name?: string;
};

type ScheduleItem = StudentScheduleListDTO["items"][number] & {
  class_name?: string;
  teacher_name?: string;
  subject_label?: string;
};

/* -----------------------------
 * State
 * ---------------------------- */

const loading = ref(false);
const errorMessage = ref<string | null>(null);

const myClass = ref<ClassItem | null>(null);

const schedule = ref<ScheduleItem[]>([]);
const grades = ref<GradeItem[]>([]);
const attendance = ref<AttendanceItem[]>([]);

/* -----------------------------
 * Helpers
 * ---------------------------- */

const normalizeStatusCode = (val: unknown): string => {
  if (val == null) return "";
  return String(val).toLowerCase();
};

const dayShort = (day: number) =>
  (["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day - 1] as string) ?? "—";

const timeRange = (row: any) =>
  `${row.start_time ?? "—"} - ${row.end_time ?? "—"}`;

const getRecordDate = (row: any) =>
  row?.record_date ?? row?.date ?? row?.lifecycle?.created_at ?? null;

const getCreatedAt = (row: any) =>
  row?.lifecycle?.created_at ?? row?.created_at ?? null;

/* -----------------------------
 * Loaders (MVP: no filters, assume 1 class)
 * ---------------------------- */

const loadMyClass = async () => {
  const res = await student.student.getMyClasses({ showError: true });
  const items = (res.items ?? []) as ClassItem[];

  // MVP: student has one class; if multiple exist, take the first
  myClass.value = items[0] ?? null;
};

const loadSchedule = async () => {
  // If your backend supports class_id filter, keep it to reduce payload.
  // If not supported, it will be ignored safely.
  const res = await student.student.getMySchedule(
    myClass.value?.id ? { class_id: myClass.value.id } : undefined,
    { showError: true, showSuccess: false }
  );

  schedule.value = (res.items ?? []) as ScheduleItem[];
};

const loadGrades = async () => {
  const res = await student.student.getMyGrades({
    showError: true,
    showSuccess: false,
  });

  grades.value = (res.items ?? []) as GradeItem[];
};

const loadAttendance = async () => {
  const res = await student.student.getMyAttendance(
    myClass.value?.id ? { class_id: myClass.value.id } : undefined,
    { showError: true, showSuccess: false }
  );

  attendance.value = (res.items ?? []) as AttendanceItem[];
};

const loadDashboard = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    await loadMyClass();
    await Promise.all([loadSchedule(), loadGrades(), loadAttendance()]);
  } catch (err: unknown) {
    reportError(err, "student.dashboard.load", "log");
    errorMessage.value =
      err instanceof Error ? err.message : "Failed to load dashboard.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

onMounted(loadDashboard);

/* -----------------------------
 * Computed: overview stats
 * ---------------------------- */

const totalSubjects = computed(() => {
  const cls: any = myClass.value;
  if (!cls) return 0;

  // Prefer subject_ids; fallback to subject_labels
  const ids = (cls.subject_ids ?? []) as string[];
  if (ids.length) return new Set(ids).size;

  const labels = (cls.subject_labels ?? []) as string[];
  return new Set(labels).size;
});

const averageScore = computed(() => {
  const rows = grades.value as any[];
  if (!rows.length) return null;
  const total = rows.reduce((sum, g) => sum + Number(g.score ?? 0), 0);
  return total / rows.length;
});

const statusSummary = computed(() => {
  const summary = {
    total: attendance.value.length,
    present: 0,
    absent: 0,
    excused: 0,
    late: 0,
  };

  for (const rec of attendance.value as any[]) {
    const s = normalizeStatusCode(rec.status);
    if (s === "present") summary.present++;
    else if (s === "absent") summary.absent++;
    else if (s === "excused") summary.excused++;
    else if (s === "late") summary.late++;
  }

  return summary;
});

const presentRate = computed(() => {
  if (!statusSummary.value.total) return null;
  return (
    Math.round(
      (statusSummary.value.present / statusSummary.value.total) * 1000
    ) / 10
  );
});

// Today schedule (1..7)
const todayDayOfWeek = computed(() => {
  const jsDay = new Date().getDay(); // 0=Sun..6=Sat
  return jsDay === 0 ? 7 : jsDay;
});

const todaySchedule = computed(() => {
  const rows = (schedule.value as any[]).filter(
    (s) => Number(s.day_of_week) === todayDayOfWeek.value
  );

  // Sort by start_time
  return rows.sort((a, b) =>
    String(a.start_time ?? "").localeCompare(String(b.start_time ?? ""))
  );
});

const recentGrades = computed(() => {
  const rows = (grades.value as any[]).slice();

  return rows
    .sort(
      (a, b) =>
        new Date(getCreatedAt(b) ?? 0).getTime() -
        new Date(getCreatedAt(a) ?? 0).getTime()
    )
    .slice(0, 6);
});

const recentAttendance = computed(() => {
  const rows = (attendance.value as any[]).slice();

  return rows
    .sort(
      (a, b) =>
        new Date(getRecordDate(b) ?? 0).getTime() -
        new Date(getRecordDate(a) ?? 0).getTime()
    )
    .slice(0, 8);
});

/* -----------------------------
 * Chart options (ECharts)
 * - assumes <VChart> is available in your project
 * ---------------------------- */

const attendanceStatusOption = computed(() => {
  const rows = attendance.value as any[];

  if (!rows.length) {
    return {
      title: { text: "No attendance data", left: "center", top: "center" },
    };
  }

  const counts = new Map<string, number>();
  for (const r of rows) {
    const k = normalizeStatusCode(r.status) || "unknown";
    counts.set(k, (counts.get(k) ?? 0) + 1);
  }

  const data = Array.from(counts.entries()).map(([name, value]) => ({
    name,
    value,
  }));

  return {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
      {
        name: "Attendance",
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 8, borderWidth: 1 },
        data,
      },
    ],
  };
});

const scoreTrendOption = computed(() => {
  const rows = (grades.value as any[])
    .slice()
    .sort(
      (a, b) =>
        new Date(getCreatedAt(a) ?? 0).getTime() -
        new Date(getCreatedAt(b) ?? 0).getTime()
    );

  if (!rows.length) {
    return { title: { text: "No grade data", left: "center", top: "center" } };
  }

  const x = rows.map((r) => formatDate(getCreatedAt(r)));
  const y = rows.map((r) => Number(r.score ?? 0));

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: { type: "category", data: x },
    yAxis: { type: "value", name: "Score", min: 0, max: 100 },
    series: [{ name: "Score", type: "line", smooth: true, data: y }],
  };
});

const avgBySubjectOption = computed(() => {
  const rows = grades.value as any[];
  if (!rows.length) {
    return { title: { text: "No grade data", left: "center", top: "center" } };
  }

  const map = new Map<
    string,
    { label: string; total: number; count: number; avg: number }
  >();

  for (const g of rows) {
    const label = g.subject_label ?? g.subject_id ?? "Unknown";
    const cur = map.get(label) || { label, total: 0, count: 0, avg: 0 };
    cur.total += Number(g.score ?? 0);
    cur.count += 1;
    cur.avg = cur.total / cur.count;
    map.set(label, cur);
  }

  const list = Array.from(map.values()).sort((a, b) => b.avg - a.avg);
  const labels = list.map((x) => x.label);
  const values = list.map((x) => Number(x.avg.toFixed(1)));

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 40, left: 40, right: 16, bottom: 80 },
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        interval: 0,
        rotate: labels.length > 4 ? 30 : 0,
        fontSize: 11,
      },
    },
    yAxis: { type: "value", name: "Avg", min: 0, max: 100 },
    series: [{ name: "Average", type: "bar", data: values, barWidth: "60%" }],
  };
});

/* -----------------------------
 * Header pill text (MVP)
 * ---------------------------- */

const headerPill = computed(() => {
  const cls = myClass.value?.name ?? "My class";
  const avg =
    averageScore.value == null ? "N/A" : averageScore.value.toFixed(1);
  const pr = presentRate.value == null ? "N/A" : `${presentRate.value}%`;
  return `${cls} • Avg: ${avg} • Present: ${pr}`;
});

/* -----------------------------
 * Actions
 * ---------------------------- */

const handleRefresh = async () => {
  await loadDashboard();
};
</script>

<template>
  <div class="p-4 space-y-4">
    <OverviewHeader
      title="Student Dashboard"
      description="Quick overview of your class, schedule, grades, and attendance."
      :loading="loading"
      :showRefresh="true"
      @refresh="handleRefresh"
    >
      <template #icon>
        <span
          class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-[var(--color-primary-light-6)] text-[color:var(--color-primary)] border border-[color:var(--color-primary-light-4)]"
        >
          {{ headerPill }}
        </span>
      </template>
    </OverviewHeader>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="rounded-xl"
    />

    <!-- Overview cards -->
    <el-row :gutter="16">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">My Class</div>
          <div class="text-base font-semibold truncate">
            {{ myClass?.name ?? "—" }}
          </div>
          <div class="text-[10px] text-gray-400 mt-1">
            {{
              myClass?.teacher_name ? `Teacher: ${myClass.teacher_name}` : " "
            }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Subjects</div>
          <div class="text-2xl font-semibold">{{ totalSubjects }}</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Average Score</div>
          <div class="text-2xl font-semibold">
            <span v-if="averageScore !== null">{{
              averageScore.toFixed(1)
            }}</span>
            <span v-else class="text-gray-400">N/A</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Present Rate</div>
          <div class="text-2xl font-semibold">
            <span v-if="presentRate !== null">{{ presentRate }}%</span>
            <span v-else class="text-gray-400">N/A</span>
          </div>
          <div class="text-[10px] text-gray-400 mt-1">
            {{ statusSummary.present }} present •
            {{ statusSummary.absent }} absent •
            {{ statusSummary.excused }} excused • {{ statusSummary.late }} late
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main grid -->
    <el-row :gutter="16">
      <!-- LEFT -->
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Today’s Schedule</div>

          <el-table
            :data="todaySchedule"
            size="small"
            border
            style="width: 100%"
          >
            <el-table-column label="Day" width="90" align="center">
              <template #default="{ row }">{{
                dayShort(Number(row.day_of_week))
              }}</template>
            </el-table-column>

            <el-table-column
              prop="subject_label"
              label="Subject"
              min-width="180"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <span class="text-gray-800">{{
                  row.subject_label ?? "—"
                }}</span>
              </template>
            </el-table-column>

            <el-table-column label="Time" min-width="130">
              <template #default="{ row }">
                <span class="font-mono text-xs">{{ timeRange(row) }}</span>
              </template>
            </el-table-column>

            <el-table-column
              prop="room"
              label="Room"
              min-width="110"
              show-overflow-tooltip
            />
            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No lessons scheduled for today.
              </div>
            </template>
          </el-table>
        </el-card>

        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Recent Grades</div>

          <el-table
            :data="recentGrades"
            size="small"
            border
            style="width: 100%"
          >
            <el-table-column
              prop="subject_label"
              label="Subject"
              min-width="190"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ row.subject_label ?? row.subject_id ?? "—" }}
              </template>
            </el-table-column>

            <el-table-column
              prop="score"
              label="Score"
              width="90"
              align="center"
            />
            <el-table-column
              prop="type"
              label="Type"
              width="110"
              align="center"
            />
            <el-table-column
              prop="term"
              label="Term"
              width="90"
              align="center"
            />

            <el-table-column
              label="Recorded At"
              min-width="180"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ formatDate(getCreatedAt(row)) }}
              </template>
            </el-table-column>

            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No grade records yet.
              </div>
            </template>
          </el-table>
        </el-card>

        <el-card shadow="hover" v-loading="loading">
          <div class="font-semibold mb-2">Recent Attendance</div>

          <el-table
            :data="recentAttendance"
            size="small"
            border
            style="width: 100%"
          >
            <el-table-column label="Date" min-width="140">
              <template #default="{ row }">
                {{ formatDate(getRecordDate(row)) }}
              </template>
            </el-table-column>

            <el-table-column
              prop="status"
              label="Status"
              width="120"
              align="center"
            >
              <template #default="{ row }">
                <el-tag
                  size="small"
                  :type="
                    normalizeStatusCode(row.status) === 'present'
                      ? 'success'
                      : normalizeStatusCode(row.status) === 'excused'
                      ? 'warning'
                      : normalizeStatusCode(row.status) === 'late'
                      ? 'info'
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
              min-width="170"
              show-overflow-tooltip
            />

            <el-table-column
              label="Recorded At"
              min-width="180"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ formatDate(row?.lifecycle?.created_at) }}
              </template>
            </el-table-column>

            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No attendance records yet.
              </div>
            </template>
          </el-table>
        </el-card>
      </el-col>

      <!-- RIGHT -->
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Attendance Status Summary</div>
          <ClientOnly>
            <div class="w-full" style="height: 240px">
              <VChart
                :option="attendanceStatusOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[240px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>

        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Score Trend</div>
          <ClientOnly>
            <div class="w-full" style="height: 240px">
              <VChart
                :option="scoreTrendOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[240px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>

        <el-card shadow="hover" v-loading="loading">
          <div class="font-semibold mb-2">Avg Score by Subject</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="avgBySubjectOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped></style>
