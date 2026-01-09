<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { ElMessage } from "element-plus";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";

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

/** prevent stale responses overriding newer refreshes */
let requestSeq = 0;
const hasFetchedOnce = ref(false);

/* -----------------------------
 * Helpers
 * ---------------------------- */
const safeText = (v: any, fallback = "—") => {
  const s = String(v ?? "").trim();
  return s ? s : fallback;
};

const normalizeStatusCode = (val: unknown): string => {
  if (val == null) return "";
  return String(val).toLowerCase();
};

const statusTag = (val: unknown) => {
  const s = normalizeStatusCode(val);
  if (s === "present") return "success";
  if (s === "excused") return "warning";
  if (s === "late") return "info";
  if (s === "absent") return "danger";
  return "info";
};

const statusLabel = (val: unknown) => {
  const s = normalizeStatusCode(val);
  if (!s) return "—";
  if (s === "present") return "Present";
  if (s === "absent") return "Absent";
  if (s === "excused") return "Excused";
  if (s === "late") return "Late";
  return String(val);
};

const dayShort = (day: number) =>
  (["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day - 1] as string) ?? "—";

const timeRange = (row: any) =>
  `${safeText(row?.start_time)} - ${safeText(row?.end_time)}`;

const getRecordDate = (row: any) =>
  row?.record_date ?? row?.date ?? row?.lifecycle?.created_at ?? null;

const getCreatedAt = (row: any) =>
  row?.lifecycle?.created_at ?? row?.created_at ?? null;

/* -----------------------------
 * Loaders
 * ---------------------------- */
const loadMyClass = async () => {
  const res = await student.student.getMyClasses({ showError: true });
  const items = (res.items ?? []) as ClassItem[];
  myClass.value = items[0] ?? null;
};

const loadSchedule = async () => {
  const res = await student.student.getMySchedule(
    myClass.value?.id ? { class_id: myClass.value.id } : undefined,
    { showError: true, showSuccess: false } as any
  );
  schedule.value = (res.items ?? []) as ScheduleItem[];
};

const loadGrades = async () => {
  const res = await student.student.getMyGrades({});
  grades.value = (res.items ?? []) as GradeItem[];
};

const loadAttendance = async () => {
  const res = await student.student.getMyAttendance(
    myClass.value?.id ? { class_id: myClass.value.id } : undefined,
    { showError: true, showSuccess: false } as any
  );
  attendance.value = (res.items ?? []) as AttendanceItem[];
};

const loadDashboard = async () => {
  const seq = ++requestSeq;

  loading.value = true;
  errorMessage.value = null;

  try {
    await loadMyClass();
    await Promise.all([loadSchedule(), loadGrades(), loadAttendance()]);
    if (seq !== requestSeq) return;

    hasFetchedOnce.value = true;
  } catch (err: any) {
    if (seq !== requestSeq) return;

    reportError(err, "student.dashboard.load", "log");

    errorMessage.value =
      err?.response?.data?.user_message ||
      err?.response?.data?.message ||
      err?.message ||
      "Failed to load dashboard.";

    myClass.value = myClass.value ?? null;
    schedule.value = [];
    grades.value = [];
    attendance.value = [];
    hasFetchedOnce.value = true;
  } finally {
    if (seq === requestSeq) loading.value = false;
  }
};

const handleRefresh = async () => {
  if (loading.value) return;
  await loadDashboard();
  ElMessage.success("Dashboard refreshed");
};

onMounted(loadDashboard);
onBeforeUnmount(() => {
  requestSeq++;
});

/* -----------------------------
 * Computed: overview stats
 * ---------------------------- */
const totalSubjects = computed(() => {
  const cls: any = myClass.value;
  if (!cls) return 0;

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
    const s = normalizeStatusCode((rec as any).status);
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
    (s) => Number((s as any).day_of_week) === todayDayOfWeek.value
  );
  return rows.sort((a, b) =>
    String((a as any).start_time ?? "").localeCompare(
      String((b as any).start_time ?? "")
    )
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
 * - assumes <VChart> exists
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
    const k = normalizeStatusCode((r as any).status) || "unknown";
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
  const y = rows.map((r) => Number((r as any).score ?? 0));

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
    const label =
      (g as any).subject_label ?? (g as any).subject_id ?? "Unknown";
    const cur = map.get(label) || { label, total: 0, count: 0, avg: 0 };
    cur.total += Number((g as any).score ?? 0);
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

const headerPill = computed(() => {
  const cls = safeText((myClass.value as any)?.name, "My class");
  const avg =
    averageScore.value == null ? "N/A" : averageScore.value.toFixed(1);
  const pr = presentRate.value == null ? "N/A" : `${presentRate.value}%`;
  return `${cls} • Avg: ${avg} • Present: ${pr}`;
});
</script>

<template>
  <div class="p-4 space-y-4 max-w-6xl mx-auto pb-10" v-loading="loading">
    <OverviewHeader
      title="Student Dashboard"
      description="Quick overview of your class, schedule, grades, and attendance."
      :loading="loading"
      :showRefresh="true"
      :showSearch="false"
      :showReset="false"
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
      closable
      class="rounded-xl border border-red-200/60 shadow-sm"
      @close="errorMessage = null"
    />

    <!-- Skeleton first load -->
    <el-card
      v-if="loading && !hasFetchedOnce"
      shadow="never"
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    >
      <el-skeleton animated :rows="10" />
    </el-card>

    <template v-else>
      <!-- MOBILE READY STAT CARDS:
           - xxs (<=480): full width 1 column
           - xs (>=480): 2 columns
           - sm (>=768): 4 columns
      -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="24" :xs="24" :sm="6">
          <el-card class="stat-card" shadow="hover">
            <div class="text-xs mb-1" style="color: var(--muted-color)">
              My Class
            </div>
            <div
              class="text-xl font-semibold truncate"
              style="color: var(--text-color)"
            >
              {{ myClass?.name ?? "—" }}
            </div>
            <div class="text-[10px] mt-1" style="color: var(--muted-color)">
              {{
                myClass?.teacher_name ? `Teacher: ${myClass.teacher_name}` : " "
              }}
            </div>
          </el-card>
        </el-col>

        <el-col :span="24" :xs="24" :sm="6">
          <el-card class="stat-card" shadow="hover">
            <div class="text-xs mb-1" style="color: var(--muted-color)">
              Subjects
            </div>
            <div
              class="text-2xl font-semibold"
              style="color: var(--text-color)"
            >
              {{ totalSubjects }}
            </div>
          </el-card>
        </el-col>

        <el-col :span="24" :xs="24" :sm="6">
          <el-card class="stat-card" shadow="hover">
            <div class="text-xs mb-1" style="color: var(--muted-color)">
              Average Score
            </div>
            <div
              class="text-2xl font-semibold"
              style="color: var(--text-color)"
            >
              <span v-if="averageScore !== null">{{
                averageScore.toFixed(1)
              }}</span>
              <span v-else style="color: var(--muted-color)">N/A</span>
            </div>
          </el-card>
        </el-col>

        <el-col :span="24" :xs="24" :sm="6">
          <el-card class="stat-card" shadow="hover">
            <div class="text-xs mb-1" style="color: var(--muted-color)">
              Present Rate
            </div>
            <div
              class="text-2xl font-semibold"
              style="color: var(--text-color)"
            >
              <span v-if="presentRate !== null">{{ presentRate }}%</span>
              <span v-else style="color: var(--muted-color)">N/A</span>
            </div>
            <div class="text-[10px] mt-1" style="color: var(--muted-color)">
              {{ statusSummary.present }} present •
              {{ statusSummary.absent }} absent •
              {{ statusSummary.excused }} excused •
              {{ statusSummary.late }} late
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Main grid (already mobile stacking because :xs="24") -->
      <el-row :gutter="16">
        <el-col :xs="24" :md="14">
          <TableCard
            title="Today’s Schedule"
            description="Sorted by start time."
            class="mb-4"
            padding="16px"
          >
            <div class="table-scroll">
              <el-table
                :data="todaySchedule"
                size="small"
                border
                style="width: 100%"
                class="app-table"
                highlight-current-row
              >
                <el-table-column label="Day" width="90" align="center">
                  <template #default="{ row }">
                    {{ dayShort(Number(row.day_of_week)) }}
                  </template>
                </el-table-column>

                <el-table-column
                  prop="subject_label"
                  label="Subject"
                  min-width="180"
                  show-overflow-tooltip
                >
                  <template #default="{ row }">
                    <div class="flex items-center gap-2 min-w-0">
                      <span
                        class="inline-block h-2 w-2 rounded-full"
                        style="background: var(--color-primary)"
                      />
                      <span class="truncate" style="color: var(--text-color)">
                        {{ row.subject_label ?? "—" }}
                      </span>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="Time" min-width="130">
                  <template #default="{ row }">
                    <span
                      class="font-mono text-xs"
                      style="color: var(--text-color)"
                    >
                      {{ timeRange(row) }}
                    </span>
                  </template>
                </el-table-column>

                <el-table-column
                  prop="room"
                  label="Room"
                  min-width="110"
                  show-overflow-tooltip
                />

                <template #empty>
                  <div
                    class="text-center text-xs py-3"
                    style="color: var(--muted-color)"
                  >
                    No lessons scheduled for today.
                  </div>
                </template>
              </el-table>
            </div>
          </TableCard>

          <TableCard
            title="Recent Grades"
            description="Latest 6 grade records."
            class="mb-4"
            padding="16px"
          >
            <div class="table-scroll">
              <el-table
                :data="recentGrades"
                size="small"
                border
                style="width: 100%"
                class="app-table"
                highlight-current-row
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
                  <div
                    class="text-center text-xs py-3"
                    style="color: var(--muted-color)"
                  >
                    No grade records yet.
                  </div>
                </template>
              </el-table>
            </div>
          </TableCard>

          <TableCard
            title="Recent Attendance"
            description="Latest 8 attendance records."
            padding="16px"
          >
            <div class="table-scroll">
              <el-table
                :data="recentAttendance"
                size="small"
                border
                style="width: 100%"
                class="app-table"
                highlight-current-row
              >
                <el-table-column label="Date" min-width="140">
                  <template #default="{ row }">
                    {{ formatDate(getRecordDate(row)) }}
                  </template>
                </el-table-column>

                <el-table-column label="Status" width="130" align="center">
                  <template #default="{ row }">
                    <el-tag
                      size="small"
                      :type="statusTag(row.status)"
                      effect="plain"
                    >
                      {{ statusLabel(row.status) }}
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
                  <div
                    class="text-center text-xs py-3"
                    style="color: var(--muted-color)"
                  >
                    No attendance records yet.
                  </div>
                </template>
              </el-table>
            </div>
          </TableCard>
        </el-col>

        <el-col :xs="24" :md="10">
          <TableCard
            title="Attendance Status Summary"
            description="Distribution by status."
            class="mb-4"
            padding="16px"
          >
            <ClientOnly>
              <div class="chart-box chart-box--sm">
                <VChart
                  :option="attendanceStatusOption"
                  autoresize
                  class="w-full h-full"
                />
              </div>

              <template #fallback>
                <div class="chart-fallback">Loading chart...</div>
              </template>
            </ClientOnly>
          </TableCard>

          <TableCard
            title="Score Trend"
            description="Score over time."
            class="mb-4"
            padding="16px"
          >
            <ClientOnly>
              <div class="chart-box chart-box--sm">
                <VChart
                  :option="scoreTrendOption"
                  autoresize
                  class="w-full h-full"
                />
              </div>

              <template #fallback>
                <div class="chart-fallback">Loading chart...</div>
              </template>
            </ClientOnly>
          </TableCard>

          <TableCard
            title="Avg Score by Subject"
            description="Average per subject."
            padding="16px"
          >
            <ClientOnly>
              <div class="chart-box chart-box--md">
                <VChart
                  :option="avgBySubjectOption"
                  autoresize
                  class="w-full h-full"
                />
              </div>

              <template #fallback>
                <div class="chart-fallback">Loading chart...</div>
              </template>
            </ClientOnly>
          </TableCard>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<style scoped>
/* keep consistent with your token system */
:deep(.el-card) {
  border-radius: 16px;
}

/* Stat card styling (consistent tokens) */
.stat-card {
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--color-card) 96%, transparent);
  width: 100%;
  height: 100%;
}

/* MOBILE layout:
   - On very small screens, reduce spacing and let cards be full width
*/
@media (max-width: 480px) {
  .stats-row {
    --el-row-gutter: 12px;
  }
}

/* Table tokens (avoid hard-coded gray/white) */
:deep(.app-table) {
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: color-mix(
    in srgb,
    var(--color-card) 88%,
    var(--color-bg) 12%
  );
  --el-table-header-text-color: var(--text-color);
  --el-table-text-color: var(--text-color);
  --el-table-row-hover-bg-color: var(--hover-bg);
  --el-table-current-row-bg-color: var(--active-bg);
}

:deep(.app-table .el-table__header-wrapper th) {
  font-weight: 650;
  font-size: 13px;
}

/* MOBILE TABLE FIX:
   el-table can overflow on small screens. Wrap it.
*/
.table-scroll {
  width: 100%;
  overflow-x: auto;
}

/* make table minimum width so columns stay readable */
:deep(.table-scroll .el-table) {
  min-width: 620px;
}

/* Chart sizes responsive */
.chart-box {
  width: 100%;
}

/* default desktop heights */
.chart-box--sm {
  height: 240px;
}
.chart-box--md {
  height: 260px;
}

/* mobile reduce chart heights */
@media (max-width: 640px) {
  .chart-box--sm {
    height: 200px;
  }
  .chart-box--md {
    height: 220px;
  }
}

.chart-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted-color);
  font-size: 12px;
  height: 200px;
}

:deep(.app-table.el-table--border .el-table__inner-wrapper::after),
:deep(.app-table.el-table--border::after),
:deep(.app-table.el-table--border::before) {
  background-color: var(--border-color);
}
</style>
