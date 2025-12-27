<script setup lang="ts">
definePageMeta({
  layout: "student",
});

import { ref, onMounted, watch, computed } from "vue";

import { studentService } from "~/api/student";
import { formatDate } from "~/utils/formatDate";

import type {
  StudentClassListDTO,
  StudentAttendanceListDTO,
} from "~/api/student/student.dto";
import { useHeaderState } from "~/composables/useHeaderState";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";

const student = studentService();

/**
 * DTO shapes (data part from backend):
 * - StudentClassListDTO: { items: ClassItem[] }
 * - StudentAttendanceListDTO: { items: AttendanceItem[] }
 */
type StudentClassItem = StudentClassListDTO["items"][number];
type StudentAttendanceItem = StudentAttendanceListDTO["items"][number];

const loadingClasses = ref(false);
const loadingAttendance = ref(false);

const classes = ref<StudentClassItem[]>([]);
const selectedClassId = ref<string | null>(null);
const attendance = ref<StudentAttendanceItem[]>([]);

/**
 * Helper: normalize status to a lowercase code.
 * This makes it robust if backend returns:
 *  - "Present", "PRESENT", "present"
 *  - "Absent", "ABSENT", "absent"
 *  - "Excused", etc.
 */
const normalizeStatusCode = (val: unknown): string => {
  if (val == null) return "";
  return String(val).toLowerCase();
};

/* ---------------- load classes ---------------- */

const loadClasses = async () => {
  loadingClasses.value = true;
  try {
    const res = await student.student.getMyClasses({
      showError: true,
    });
    classes.value = res.items ?? [];

    // auto-select first class
    if (!selectedClassId.value && classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id;
    }
  } finally {
    loadingClasses.value = false;
  }
};

/* ---------------- load attendance for selected class ---------------- */

const loadAttendance = async () => {
  if (!selectedClassId.value) {
    attendance.value = [];
    return;
  }

  loadingAttendance.value = true;
  try {
    const res = await student.student.getMyAttendance(
      { class_id: selectedClassId.value },
      {
        showError: true,
        showSuccess: false,
      }
    );
    // StudentAttendanceListDTO => { items: [...] }
    attendance.value = res.items ?? [];
  } finally {
    loadingAttendance.value = false;
  }
};

watch(selectedClassId, async () => {
  // reset to first page when class changes
  current.value = 1;
  await loadAttendance();
});

onMounted(async () => {
  await loadClasses();
  await loadAttendance();
});

/* ---------------- pagination ---------------- */

const current = ref(1);
const pageSize = ref(10);

const pagedData = computed(() => {
  const start = (current.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return attendance.value.slice(start, end);
});

/* ---------------- overview stats ---------------- */

const statusSummary = computed(() => {
  const summary = {
    total: attendance.value.length,
    present: 0,
    absent: 0,
    excused: 0,
  };

  for (const rec of attendance.value) {
    const s = normalizeStatusCode(rec.status);
    if (s === "present") summary.present++;
    else if (s === "absent") summary.absent++;
    else if (s === "excused") summary.excused++;
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
const presentCount = computed(() => statusSummary.value.present);
const absentCount = computed(() => statusSummary.value.absent);
const excusedCount = computed(() => statusSummary.value.excused);

const { headerState: headerStats } = useHeaderState({
  items: [
    {
      key: "total",
      getValue: () => statusSummary.value.total,
      singular: "record",
      variant: "primary",
      hideWhenZero: true,
    },
    {
      key: "present",
      getValue: () => presentCount.value,
      prefix: "Present:",
      singular: "record",
      variant: "secondary",
      dotClass: "bg-emerald-500",
    },
    {
      key: "absent",
      getValue: () => absentCount.value,
      prefix: "Absent:",
      singular: "record",
      variant: "secondary",
      dotClass: "bg-red-500",
    },
    {
      key: "excused",
      getValue: () => excusedCount.value,
      prefix: "Excused:",
      singular: "record",
      variant: "secondary",
      dotClass: "bg-amber-500",
    },
    {
      key: "present_rate",
      getValue: () => presentRate.value ?? 0,
      label: (value) =>
        statusSummary.value.total === 0 ? undefined : `Present rate: ${value}%`,
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});

const canRefresh = computed(
  () => !loadingClasses.value && !loadingAttendance.value
);

const handleRefresh = async () => {
  if (!canRefresh.value) return;
  await loadClasses();
  await loadAttendance();
};
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- OVERVIEW HEADER -->
    <OverviewHeader
      title="My Attendance"
      description="Check your attendance for each class."
      :loading="loadingClasses || loadingAttendance"
      :showRefresh="true"
      :stats="headerStats"
      @refresh="handleRefresh"
    >
      <!-- Filters slot: class select -->
      <template #filters>
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Class:</span>
            <el-select
              v-model="selectedClassId"
              placeholder="Select class"
              style="min-width: 220px"
              :loading="loadingClasses"
              clearable
            >
              <el-option
                v-for="c in classes"
                :key="c.id"
                :label="c.name"
                :value="c.id"
              />
            </el-select>
          </div>
        </div>
      </template>
    </OverviewHeader>

    <!-- MAIN CARD -->
    <el-card shadow="hover" class="space-y-4">
      <!-- Small header inside card -->
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
      >
        <div>
          <div class="text-base font-semibold text-gray-800">
            Attendance records
          </div>
          <p class="text-xs text-gray-500">
            Each row is one record for a given class and date.
          </p>
        </div>

        <div class="text-xs text-gray-500">
          Showing {{ pagedData.length }} / {{ attendance.length }} records
        </div>
      </div>

      <!-- TABLE -->
      <el-table
        :data="pagedData"
        v-loading="loadingAttendance"
        border
        size="small"
        style="width: 100%"
        highlight-current-row
      >
        <!-- Date -->
        <el-table-column prop="record_date" label="Date" min-width="130">
          <template #default="{ row }">
            {{ row.record_date }}
          </template>
        </el-table-column>

        <!-- Class -->
        <el-table-column
          prop="class_name"
          label="Class"
          min-width="160"
          show-overflow-tooltip
        />

        <!-- Status -->
        <el-table-column prop="status" label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag
              :type="
                normalizeStatusCode(row.status) === 'present'
                  ? 'success'
                  : normalizeStatusCode(row.status) === 'excused'
                  ? 'warning'
                  : 'danger'
              "
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- Teacher -->
        <el-table-column
          prop="teacher_name"
          label="Marked By"
          min-width="150"
          show-overflow-tooltip
        />

        <!-- Created at -->
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

      <!-- Empty state -->
      <div
        v-if="!loadingAttendance && !attendance.length"
        class="text-center text-gray-500 text-sm py-4"
      >
        No attendance records for this class yet.
      </div>

      <!-- PAGINATION -->
      <el-row v-if="attendance.length > 0" justify="end" class="mt-6">
        <el-pagination
          v-model:current-page="current"
          v-model:page-size="pageSize"
          :total="attendance.length"
          layout="prev, pager, next, jumper, ->, total, sizes"
          :page-sizes="[5, 10, 20, 50]"
          class="mt-2 flex justify-end"
        />
      </el-row>
    </el-card>
  </div>
</template>

<style scoped></style>
