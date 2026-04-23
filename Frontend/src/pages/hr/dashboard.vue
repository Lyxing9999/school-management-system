<script setup lang="ts">
import { computed, onActivated, onMounted, ref } from "vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { ElDialog } from "element-plus";
import { hrmsAdminService } from "~/api/hr_admin";
import type { AttendanceDTO } from "~/api/hr_admin/attendance/dto";
import type { OvertimeRequestDTO } from "~/api/hr_admin/overtime/dto";
import type { LeaveRequestDTO } from "~/api/hr_admin/leave/dto";
import type { PayrollRunDTO } from "~/api/hr_admin/payroll/dto";
import type { HrEmployeeWithAccountSummaryDTO } from "~/api/hr_admin/employees/dto";
import type { PublicHolidayDTO } from "~/api/hr_admin/publicHoliday/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

type PendingAction = {
  id: string;
  type: "overtime" | "leave" | "payroll" | "attendance";
  status: string;
  employee_id?: string;
  summary: string;
  route: string;
  requested_at?: string | null;
};

type CalendarCell = {
  key: string;
  date: Date;
  label: number;
  inMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  holiday?: PublicHolidayDTO;
};

const router = useRouter();
const hrService = hrmsAdminService();

const loading = ref(false);
const initialized = ref(false);

const employees = ref<HrEmployeeWithAccountSummaryDTO[]>([]);
const attendances = ref<AttendanceDTO[]>([]);
const overtimeRequests = ref<OvertimeRequestDTO[]>([]);
const leaveRequests = ref<LeaveRequestDTO[]>([]);
const payrollRuns = ref<PayrollRunDTO[]>([]);
const publicHolidays = ref<PublicHolidayDTO[]>([]);

const employeeTotal = ref(0);
const attendanceTotal = ref(0);
const payrollTotal = ref(0);

const activeSegment = ref<"profile" | "reports" | "employee">("profile");

const calendarCursor = ref(new Date());
const selectedDate = ref(new Date());
const selectedHoliday = ref<PublicHolidayDTO | null>(null);
const holidayDialogOpen = ref(false);
const weekdayLabels = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

function toIsoDate(value: Date): string {
  const yyyy = value.getFullYear();
  const mm = String(value.getMonth() + 1).padStart(2, "0");
  const dd = String(value.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function formatDate(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

function formatShortDate(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
  });
}

function formatMonthShort(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(`${value}-01T00:00:00`);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-US", {
    month: "short",
    year: "2-digit",
  });
}

function initialsFromName(value?: string): string {
  const safe = String(value || "Unknown").trim();
  const parts = safe.split(/\s+/).filter(Boolean);
  if (!parts.length) return "HR";
  return parts
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() || "")
    .join("");
}

const greetingTitle = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
});

const activeEmployees = computed(
  () =>
    employees.value.filter(
      (item) => String(item.employee?.status || "").toLowerCase() === "active",
    ).length,
);

const departmentCount = computed(() => {
  const set = new Set<string>();
  for (const row of employees.value) {
    const key = String(row.employee?.department || "").trim();
    if (key) set.add(key);
  }
  return set.size;
});

const todayIso = computed(() => toIsoDate(new Date()));

const presentTodayCount = computed(() => {
  const presentStates = new Set([
    "checked_in",
    "checked_out",
    "late",
    "early_leave",
    "wrong_location_pending",
    "wrong_location_approved",
    "wrong_location_rejected",
  ]);
  return attendances.value.filter(
    (row) =>
      row.attendance_date === todayIso.value &&
      presentStates.has(String(row.status || "").toLowerCase()),
  ).length;
});

const pendingLeave = computed(
  () =>
    leaveRequests.value.filter(
      (row) => String(row.status || "").toLowerCase() === "pending",
    ).length,
);

const topStats = computed(() => [
  {
    label: "Department",
    value: departmentCount.value || 0,
    helper: "Org units",
  },
  {
    label: "Employee",
    value: employeeTotal.value,
    helper: `${activeEmployees.value} active`,
  },
  { label: "Presence", value: presentTodayCount.value, helper: "Today" },
  { label: "Leave", value: pendingLeave.value, helper: "Pending" },
]);

const departmentDistributionOption = computed(() => {
  const grouped = new Map<string, number>();
  for (const row of employees.value) {
    const dept = String(row.employee?.department || "Unassigned");
    grouped.set(dept, (grouped.get(dept) || 0) + 1);
  }

  const pieRows = [...grouped.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }));

  // Get chart colors from CSS variables with fallback to global theme tokens
  const computedStyle =
    typeof window !== "undefined"
      ? getComputedStyle(document.documentElement)
      : null;

  // Fallback to muted-color for label and border-color for borders
  const chartLabelColor =
    computedStyle?.getPropertyValue("--chart-label-color").trim() ||
    computedStyle?.getPropertyValue("--muted-color").trim() ||
    "#6b7280";
  const chartBorderColor =
    computedStyle?.getPropertyValue("--chart-border-color").trim() ||
    computedStyle?.getPropertyValue("--border-color").trim() ||
    "#e5e7eb";

  return {
    tooltip: { trigger: "item" },
    legend: { show: false },
    series: [
      {
        type: "pie",
        radius: ["28%", "72%"],
        center: ["50%", "50%"],
        itemStyle: {
          borderRadius: 8,
          borderColor: chartBorderColor,
          borderWidth: 2,
        },
        label: { color: chartLabelColor, fontSize: 10 },
        labelLine: { length: 8, length2: 6 },
        data: pieRows,
      },
    ],
  };
});

const attendanceTrendOption = computed(() => {
  const dayMap = new Map<string, { present: number; flagged: number }>();
  for (const row of attendances.value) {
    const key = row.attendance_date;
    if (!dayMap.has(key)) dayMap.set(key, { present: 0, flagged: 0 });
    const item = dayMap.get(key)!;
    const status = String(row.status || "").toLowerCase();
    if (status !== "absent") item.present += 1;
    if (
      status === "late" ||
      status === "early_leave" ||
      status.includes("wrong_location")
    ) {
      item.flagged += 1;
    }
  }

  const days = [...dayMap.keys()].sort().slice(-10);
  const present = days.map((d) => dayMap.get(d)?.present ?? 0);
  const flagged = days.map((d) => dayMap.get(d)?.flagged ?? 0);

  return {
    tooltip: { trigger: "axis" },
    legend: {
      top: 0,
      left: "center",
      itemGap: 14,
      textStyle: { fontSize: 11 },
    },
    grid: { left: 28, right: 12, top: 34, bottom: 24 },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: days.map((d) => formatShortDate(d)),
      axisLabel: {
        hideOverlap: true,
        fontSize: 11,
        margin: 10,
      },
    },
    yAxis: { type: "value", minInterval: 1 },
    series: [
      {
        name: "Present",
        type: "line",
        smooth: true,
        symbolSize: 6,
        data: present,
        areaStyle: { opacity: 0.12 },
      },
      {
        name: "Flagged",
        type: "line",
        smooth: true,
        symbolSize: 6,
        data: flagged,
      },
    ],
  };
});

const payrollFlowOption = computed(() => {
  const monthly = new Map<
    string,
    { draft: number; finalized: number; paid: number }
  >();
  for (const row of payrollRuns.value) {
    const month = String(row.month || "-");
    if (!monthly.has(month))
      monthly.set(month, { draft: 0, finalized: 0, paid: 0 });
    const status = String(row.status || "").toLowerCase();
    const bucket = monthly.get(month)!;
    if (status === "draft") bucket.draft += 1;
    if (status === "finalized") bucket.finalized += 1;
    if (status === "paid") bucket.paid += 1;
  }

  const months = [...monthly.keys()].sort().slice(-8);

  return {
    tooltip: { trigger: "axis" },
    legend: {
      top: 0,
      left: "center",
      itemGap: 14,
      textStyle: { fontSize: 11 },
    },
    grid: { left: 28, right: 12, top: 34, bottom: 24 },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: months.map((m) => formatMonthShort(m)),
      axisLabel: {
        hideOverlap: true,
        fontSize: 11,
        margin: 10,
      },
    },
    yAxis: { type: "value", minInterval: 1 },
    series: [
      {
        name: "Draft",
        type: "line",
        smooth: true,
        symbolSize: 5,
        data: months.map((m) => monthly.get(m)?.draft ?? 0),
        areaStyle: { opacity: 0.08 },
      },
      {
        name: "Finalized",
        type: "line",
        smooth: true,
        symbolSize: 5,
        data: months.map((m) => monthly.get(m)?.finalized ?? 0),
      },
      {
        name: "Paid",
        type: "line",
        smooth: true,
        symbolSize: 5,
        data: months.map((m) => monthly.get(m)?.paid ?? 0),
      },
    ],
  };
});

const leaveSpotlights = computed(() =>
  leaveRequests.value
    .filter((row) => String(row.status || "").toLowerCase() === "pending")
    .sort(
      (a, b) =>
        new Date(b.lifecycle?.created_at || 0).getTime() -
        new Date(a.lifecycle?.created_at || 0).getTime(),
    )
    .slice(0, 3),
);

const pendingQueue = computed<PendingAction[]>(() => {
  const overtimeActions: PendingAction[] = overtimeRequests.value
    .filter((row) => String(row.status || "").toLowerCase() === "pending")
    .map((row) => ({
      id: row.id,
      type: "overtime",
      status: row.status,
      employee_id: row.employee_id,
      summary: `OT ${Number(row.approved_hours || 0).toFixed(
        1,
      )}h for ${formatShortDate(row.request_date)}`,
      route: ROUTES.HR_ADMIN.OVERTIME_REVIEWS,
      requested_at: row.submitted_at,
    }));

  const leaveActions: PendingAction[] = leaveRequests.value
    .filter((row) => String(row.status || "").toLowerCase() === "pending")
    .map((row) => ({
      id: row.id,
      type: "leave",
      status: row.status,
      employee_id: row.employee_id,
      summary: `${String(row.leave_type).toUpperCase()} ${formatShortDate(
        row.start_date,
      )}-${formatShortDate(row.end_date)}`,
      route: ROUTES.HR_ADMIN.LEAVE_REVIEWS,
      requested_at: row.lifecycle?.created_at,
    }));

  const payrollActions: PendingAction[] = payrollRuns.value
    .filter((row) => String(row.status || "").toLowerCase() === "draft")
    .map((row) => ({
      id: row.id,
      type: "payroll",
      status: row.status,
      summary: `Draft run ${row.month}`,
      route: ROUTES.HR_ADMIN.PAYROLL_RUNS,
      requested_at: row.lifecycle?.created_at,
    }));

  return [...overtimeActions, ...leaveActions, ...payrollActions]
    .sort(
      (a, b) =>
        new Date(b.requested_at || 0).getTime() -
        new Date(a.requested_at || 0).getTime(),
    )
    .slice(0, 6);
});

const monthTitle = computed(() =>
  calendarCursor.value.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  }),
);

const calendarCells = computed<CalendarCell[]>(() => {
  const cursor = calendarCursor.value;
  const year = cursor.getFullYear();
  const month = cursor.getMonth();

  const firstDay = new Date(year, month, 1);
  const dayOffset = firstDay.getDay();
  const firstVisible = new Date(year, month, 1 - dayOffset);

  const todayIsoValue = toIsoDate(new Date());
  const selectedIsoValue = toIsoDate(selectedDate.value);

  // Create a map of holidays by date for quick lookup
  const holidaysByDate = new Map<string, PublicHolidayDTO>();
  for (const holiday of publicHolidays.value) {
    holidaysByDate.set(holiday.date, holiday);
  }

  const cells: CalendarCell[] = [];
  for (let i = 0; i < 42; i += 1) {
    const date = new Date(firstVisible);
    date.setDate(firstVisible.getDate() + i);
    const iso = toIsoDate(date);
    cells.push({
      key: iso,
      date,
      label: date.getDate(),
      inMonth: date.getMonth() === month,
      isToday: iso === todayIsoValue,
      isSelected: iso === selectedIsoValue,
      holiday: holidaysByDate.get(iso),
    });
  }
  return cells;
});

const selectedDateLeaves = computed(() => {
  const target = toIsoDate(selectedDate.value);
  return leaveRequests.value.filter((row) => {
    return row.start_date <= target && target <= row.end_date;
  });
});

function shiftMonth(delta: number) {
  const base = new Date(calendarCursor.value);
  base.setMonth(base.getMonth() + delta);
  calendarCursor.value = base;
}

function goToday() {
  const now = new Date();
  calendarCursor.value = new Date(now.getFullYear(), now.getMonth(), 1);
  selectedDate.value = now;
}

function setSelectedDate(date: Date) {
  selectedDate.value = new Date(date);
}

function showHolidayDetails(holiday: PublicHolidayDTO) {
  selectedHoliday.value = holiday;
  holidayDialogOpen.value = true;
}

function closeHolidayDialog() {
  holidayDialogOpen.value = false;
  selectedHoliday.value = null;
}

async function fetchDashboard() {
  loading.value = true;
  try {
    const [
      employeeRes,
      attendanceRes,
      overtimeRes,
      leaveRes,
      payrollRes,
      holidaysRes,
    ] = await Promise.all([
      hrService.employee.getEmployeesWithAccounts({ page: 1, limit: 160 }),
      hrService.attendance.getAttendances({ page: 1, limit: 220 }),
      hrService.overtimeRequest.getRequests({ page: 1, limit: 120 }),
      hrService.leaveRequest.getRequests({ page: 1, limit: 120 }),
      hrService.payrollRun.listRuns({ page: 1, limit: 120 }),
      hrService.publicHoliday.getPublicHolidays(),
    ]);

    employees.value = employeeRes.items ?? [];
    attendances.value = attendanceRes.items ?? [];
    overtimeRequests.value = overtimeRes.items ?? [];
    leaveRequests.value = leaveRes.items ?? [];
    payrollRuns.value = payrollRes.items ?? [];
    publicHolidays.value = holidaysRes ?? [];

    employeeTotal.value = employeeRes.total ?? employees.value.length;
    attendanceTotal.value =
      attendanceRes.pagination?.total ?? attendances.value.length;
    payrollTotal.value = payrollRes.total ?? payrollRuns.value.length;
  } catch {
    // Service layer already handles API notifications.
  } finally {
    loading.value = false;
  }
}

async function ensureInitialLoad() {
  if (initialized.value) return;
  initialized.value = true;
  await fetchDashboard();
}

onMounted(() => {
  void ensureInitialLoad();
});

onActivated(() => {
  void fetchDashboard();
});
</script>

<template>
  <div class="hr-soft-dashboard" v-loading="loading">
    <OverviewHeader
      title="HR Dashboard"
      :description="`${greetingTitle}, HR team`"
      :backPath="ROUTES.HR_ADMIN.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain @click="fetchDashboard">Refresh Data</BaseButton>
      </template>
    </OverviewHeader>

    <section class="hero-shell">
      <div class="hero-strip">
        <div class="hero-copy">
          <h2>People &amp; Operations Insights</h2>
          <p>
            Today attendance: {{ presentTodayCount }} of
            {{ employeeTotal }} employees
          </p>
        </div>

        <div class="segment-switch">
          <button
            class="segment-chip"
            :class="{ 'segment-chip--active': activeSegment === 'profile' }"
            @click="activeSegment = 'profile'"
          >
            Profile
          </button>
          <button
            class="segment-chip"
            :class="{ 'segment-chip--active': activeSegment === 'reports' }"
            @click="router.push(ROUTES.HR_ADMIN.REPORTS_ATTENDANCE)"
          >
            Reports
          </button>
          <button
            class="segment-chip"
            :class="{ 'segment-chip--active': activeSegment === 'employee' }"
            @click="router.push(ROUTES.HR_ADMIN.EMPLOYEES)"
          >
            Employee
          </button>
        </div>
      </div>

      <div class="metric-grid">
        <article
          v-for="(item, index) in topStats"
          :key="item.label"
          class="metric-card"
          :style="{ animationDelay: `${index * 70}ms` }"
        >
          <span class="metric-label">{{ item.label }}</span>
          <strong class="metric-value">{{ item.value }}</strong>
          <span class="metric-note">{{ item.helper }}</span>
        </article>
      </div>

      <div class="chart-trio">
        <article class="panel-card">
          <header>
            <h3>Department Split</h3>
            <small>Top divisions</small>
          </header>
          <ClientOnly>
            <div class="chart-box">
              <VChart
                :option="departmentDistributionOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div class="chart-fallback">Loading chart...</div>
            </template>
          </ClientOnly>
        </article>

        <article class="panel-card">
          <header>
            <h3>Attendance Wave</h3>
            <small>Last 10 activity days</small>
          </header>
          <ClientOnly>
            <div class="chart-box">
              <VChart
                :option="attendanceTrendOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div class="chart-fallback">Loading chart...</div>
            </template>
          </ClientOnly>
        </article>

        <article class="panel-card">
          <header>
            <h3>Payroll Flow</h3>
            <small>{{ payrollTotal }} total runs</small>
          </header>
          <ClientOnly>
            <div class="chart-box">
              <VChart
                :option="payrollFlowOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div class="chart-fallback">Loading chart...</div>
            </template>
          </ClientOnly>
        </article>
      </div>

      <div class="bottom-grid">
        <article class="leave-zone">
          <div class="leave-zone__head">
            <h3>Employee Leave Spotlight</h3>
            <BaseButton
              plain
              size="small"
              @click="router.push(ROUTES.HR_ADMIN.LEAVE_REVIEWS)"
            >
              Open Reviews
            </BaseButton>
          </div>

          <div v-if="!leaveSpotlights.length" class="empty-note">
            No pending leave request right now.
          </div>

          <div v-else class="leave-cards">
            <div
              v-for="row in leaveSpotlights"
              :key="row.id"
              class="leave-card"
            >
              <div class="leave-card__avatar">
                {{
                  initialsFromName(
                    displayRelation(row.employee_name, row.employee_id),
                  )
                }}
              </div>
              <div class="leave-card__info">
                <h4>
                  {{ displayRelation(row.employee_name, row.employee_id) }}
                </h4>
                <p>
                  {{ String(row.leave_type).toUpperCase() }}
                  •
                  {{ Number(row.total_days || 0).toFixed(1) }} day(s)
                </p>
                <span
                  >{{ formatDate(row.start_date) }} -
                  {{ formatDate(row.end_date) }}</span
                >
              </div>
            </div>
          </div>

          <div v-if="pendingQueue.length" class="pending-feed">
            <h4>Latest Pending Actions</h4>
            <button
              v-for="item in pendingQueue"
              :key="item.id"
              class="pending-row"
              @click="router.push(item.route)"
            >
              <span>{{ item.summary }}</span>
              <small>{{ String(item.type).toUpperCase() }}</small>
            </button>
          </div>
        </article>

        <article class="calendar-zone">
          <div class="calendar-head">
            <button class="calendar-nav" @click="shiftMonth(-1)">‹</button>
            <h3>{{ monthTitle }}</h3>
            <button class="calendar-nav" @click="shiftMonth(1)">›</button>
          </div>

          <div class="calendar-weekdays">
            <span v-for="day in weekdayLabels" :key="day">{{ day }}</span>
          </div>

          <div class="calendar-grid">
            <button
              v-for="cell in calendarCells"
              :key="cell.key"
              class="calendar-cell"
              :class="{
                'calendar-cell--out': !cell.inMonth,
                'calendar-cell--today': cell.isToday,
                'calendar-cell--selected': cell.isSelected,
                'calendar-cell--holiday': cell.holiday,
              }"
              @click="
                cell.holiday
                  ? showHolidayDetails(cell.holiday)
                  : setSelectedDate(cell.date)
              "
            >
              <span class="calendar-cell__day">{{ cell.label }}</span>
              <span v-if="cell.holiday" class="calendar-cell__holiday-dot" />
            </button>
          </div>

          <div class="calendar-foot">
            <strong
              >{{ selectedDateLeaves.length }} leave event(s) on
              {{ formatDate(toIsoDate(selectedDate)) }}</strong
            >
            <BaseButton plain size="small" @click="goToday"
              >Go Today</BaseButton
            >
          </div>

          <div class="calendar-mini-stats">
            <div>
              <span>Attendance Records</span>
              <strong>{{ attendanceTotal }}</strong>
            </div>
            <div>
              <span>Pending OT</span>
              <strong>{{
                overtimeRequests.filter(
                  (x) => String(x.status).toLowerCase() === "pending",
                ).length
              }}</strong>
            </div>
            <div>
              <span>Pending Leave</span>
              <strong>{{ pendingLeave }}</strong>
            </div>
          </div>
        </article>
      </div>
    </section>

    <ElDialog
      v-model="holidayDialogOpen"
      title="Public Holiday Details"
      width="440px"
      @close="closeHolidayDialog"
    >
      <div v-if="selectedHoliday" class="holiday-dialog-content">
        <div class="holiday-field">
          <label>Date</label>
          <span class="holiday-value">{{
            formatDate(selectedHoliday.date)
          }}</span>
        </div>
        <div class="holiday-field">
          <label>Holiday Name</label>
          <span class="holiday-value">{{ selectedHoliday.name }}</span>
        </div>
        <div v-if="selectedHoliday.name_kh" class="holiday-field">
          <label>Khmer Name</label>
          <span class="holiday-value">{{ selectedHoliday.name_kh }}</span>
        </div>
        <div class="holiday-field">
          <label>Paid Holiday</label>
          <span class="holiday-value holiday-value--paid">
            {{ selectedHoliday.is_paid ? "Yes" : "No" }}
          </span>
        </div>
        <div v-if="selectedHoliday.description" class="holiday-field">
          <label>Description</label>
          <span class="holiday-value">{{ selectedHoliday.description }}</span>
        </div>
      </div>
    </ElDialog>
  </div>
</template>

<style scoped>
.hr-soft-dashboard {
  padding: 16px;
  max-width: 1460px;
  margin: 0 auto;
}

.hero-shell {
  border-radius: 22px;
  padding: 16px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--color-primary-light-9) 100%, var(--color-card)) 0%,
    var(--color-card) 100%
  );
  border: 1px solid var(--border-color);
  box-shadow: 0 16px 38px var(--card-shadow);
}

.hero-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.hero-copy h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 20px;
  font-weight: 800;
}

.hero-copy p {
  margin: 3px 0 0;
  color: var(--muted-color);
  font-size: 13px;
}

.segment-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border-radius: 999px;
  background: var(--hover-bg);
}

.segment-chip {
  border: none;
  cursor: pointer;
  border-radius: 999px;
  background: transparent;
  padding: 6px 14px;
  color: var(--muted-color);
  font-weight: 600;
  font-size: 12px;
  transition: all 0.2s ease;
}

.segment-chip--active,
.segment-chip:hover {
  background: var(--color-card);
  color: var(--text-color);
  box-shadow: 0 5px 12px var(--card-shadow);
}

.metric-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  border-radius: 16px;
  padding: 14px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--color-primary-light-8) 100%, var(--color-card)) 0%,
    var(--color-card) 100%
  );
  border: 1px solid var(--border-color);
  animation: revealUp 0.5s ease both;
}

.metric-label {
  display: block;
  font-size: 12px;
  color: var(--muted-color);
}

.metric-value {
  display: block;
  margin-top: 5px;
  font-size: 38px;
  line-height: 1;
  color: var(--text-color);
  font-weight: 800;
}

.metric-note {
  display: block;
  margin-top: 4px;
  color: var(--muted-color);
  font-size: 12px;
}

.chart-trio {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.panel-card {
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: var(--color-card);
  padding: 14px;
}

.panel-card header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.panel-card h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 14px;
  font-weight: 700;
}

.panel-card small {
  color: var(--muted-color);
  font-size: 11px;
}

.chart-box {
  margin-top: 8px;
  width: 100%;
  height: 290px;
}

.chart-fallback {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted-color);
  font-size: 12px;
}

.bottom-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: 1.8fr 1fr;
  gap: 12px;
}

.leave-zone,
.calendar-zone {
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: var(--color-card);
  padding: 14px;
}

.leave-zone__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.leave-zone__head h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 22px;
  font-weight: 800;
}

.empty-note {
  border-radius: 12px;
  background: var(--hover-bg);
  color: var(--muted-color);
  padding: 10px;
  font-size: 13px;
}

.leave-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.leave-card {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--hover-bg);
  padding: 10px;
  min-height: 130px;
}

.leave-card__avatar {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--text-color);
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--color-primary-light-8) 100%, var(--color-card)) 0%,
    color-mix(in srgb, var(--color-primary-light-7) 100%, var(--color-card))
      100%
  );
}

.leave-card__info h4 {
  margin: 8px 0 2px;
  font-size: 14px;
  color: var(--text-color);
  line-height: 1.25;
}

.leave-card__info p {
  margin: 0;
  color: var(--muted-color);
  font-size: 12px;
}

.leave-card__info span {
  display: block;
  margin-top: 6px;
  color: var(--muted-color);
  font-size: 11px;
}

.pending-feed {
  margin-top: 12px;
}

.pending-feed h4 {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--text-color);
}

.pending-row {
  width: 100%;
  border: 1px solid var(--border-color);
  background: var(--color-card);
  border-radius: 10px;
  padding: 9px 10px;
  margin-bottom: 8px;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  cursor: pointer;
}

.pending-row span {
  color: var(--text-color);
  font-size: 12px;
}

.pending-row small {
  color: var(--muted-color);
  font-size: 10px;
}

.calendar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.calendar-head h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-color);
  font-weight: 700;
}

.calendar-nav {
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: var(--hover-bg);
  color: var(--text-color);
  cursor: pointer;
}

.calendar-weekdays {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-weekdays span {
  text-align: center;
  color: var(--muted-color);
  font-size: 11px;
}

.calendar-grid {
  margin-top: 6px;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-cell {
  border: none;
  border-radius: 8px;
  min-height: 34px;
  background: var(--color-card);
  color: var(--text-color);
  cursor: pointer;
  font-weight: 600;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  transition: all 0.2s ease;
}

.calendar-cell--out {
  color: var(--muted-color);
}

.calendar-cell--today {
  box-shadow: inset 0 0 0 1.5px var(--color-primary);
}

.calendar-cell--selected {
  background: var(--color-primary);
  color: var(--color-light);
}

.calendar-cell--holiday {
  background: var(--active-bg);
  box-shadow: inset 0 0 0 1px var(--border-color);
}

.calendar-cell--holiday:hover {
  background: var(--hover-bg);
  box-shadow: inset 0 0 0 1.5px var(--color-primary);
}

.calendar-cell__day {
  z-index: 1;
}

.calendar-cell__holiday-dot {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-primary);
  bottom: 3px;
  right: 3px;
}

.calendar-foot {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.calendar-foot strong {
  color: var(--text-color);
  font-size: 12px;
  line-height: 1.35;
}

.calendar-mini-stats {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.calendar-mini-stats div {
  border-radius: 10px;
  background: var(--hover-bg);
  border: 1px solid var(--border-color);
  padding: 8px;
}

.calendar-mini-stats span {
  display: block;
  color: var(--muted-color);
  font-size: 10px;
}

.calendar-mini-stats strong {
  display: block;
  margin-top: 2px;
  color: var(--text-color);
  font-size: 17px;
}

@keyframes revealUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.holiday-dialog-content {
  padding: 8px 0;
}

.holiday-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.holiday-field label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 13px;
}

.holiday-value {
  color: var(--muted-color);
  font-size: 14px;
  word-break: break-word;
}

.holiday-value--paid {
  font-weight: 600;
  color: var(--button-success-bg);
}

@media (max-width: 1200px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .chart-trio {
    grid-template-columns: 1fr;
  }

  .chart-box {
    height: 320px;
  }

  .chart-fallback {
    min-height: 290px;
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 780px) {
  .hr-soft-dashboard {
    padding: 10px;
  }

  .hero-shell {
    padding: 12px;
    border-radius: 16px;
  }

  .hero-strip {
    flex-direction: column;
    align-items: flex-start;
  }

  .segment-switch {
    width: 100%;
    justify-content: flex-start;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }

  .metric-value {
    font-size: 30px;
  }

  .metric-card {
    padding: 12px;
  }

  .chart-trio {
    gap: 12px;
  }

  .panel-card {
    padding: 12px;
  }

  .chart-box {
    height: 250px;
  }

  .chart-fallback {
    min-height: 220px;
  }

  .leave-cards {
    grid-template-columns: 1fr;
  }

  .calendar-mini-stats {
    grid-template-columns: 1fr;
  }

  .calendar-cell {
    min-height: 40px;
    font-size: 12px;
  }

  .calendar-weekdays {
    gap: 2px;
  }

  .calendar-weekdays span {
    font-size: 10px;
  }

  .calendar-grid {
    gap: 2px;
  }

  .calendar-head {
    gap: 8px;
  }

  .calendar-head h3 {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .hr-soft-dashboard {
    padding: 8px;
  }

  .hero-shell {
    padding: 10px;
    border-radius: 12px;
  }

  .hero-copy h2 {
    font-size: 18px;
  }

  .hero-copy p {
    font-size: 12px;
  }

  .segment-chip {
    padding: 5px 10px;
    font-size: 11px;
  }

  .metric-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .metric-value {
    font-size: 24px;
  }

  .metric-label {
    font-size: 11px;
  }

  .metric-note {
    font-size: 11px;
  }

  .chart-trio {
    gap: 10px;
  }

  .panel-card {
    padding: 10px;
  }

  .panel-card h3 {
    font-size: 13px;
  }

  .panel-card small {
    font-size: 10px;
  }

  .chart-box {
    margin-top: 6px;
    height: 210px;
  }

  .chart-fallback {
    min-height: 190px;
  }

  .leave-zone__head {
    flex-direction: column;
    align-items: flex-start;
  }

  .leave-zone__head h3 {
    font-size: 18px;
  }

  .leave-cards {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .calendar-cell {
    min-height: 36px;
    font-size: 11px;
  }

  .calendar-weekdays {
    gap: 1px;
  }

  .calendar-grid {
    gap: 1px;
  }

  .calendar-mini-stats {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .calendar-mini-stats div {
    padding: 6px;
  }

  .calendar-mini-stats span {
    font-size: 9px;
  }

  .calendar-mini-stats strong {
    font-size: 15px;
  }
}
</style>
