<script setup lang="ts">
import { computed, ref } from "vue";
import { ElMessage } from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type { AttendanceDTO } from "~/api/hr_admin/attendance";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

definePageMeta({ layout: "default" });

type StatusSummaryRow = {
  key: string;
  label: string;
  count: number;
  percentage: string;
};

type SummaryType = "all" | "attendance" | "wrong-location";

const attendanceService = hrmsAdminService().attendance;

const loading = ref(false);
const summaryType = ref<SummaryType>("all");
const startDate = ref("");
const endDate = ref("");

const attendanceRows = ref<AttendanceDTO[]>([]);
const wrongLocationRows = ref<AttendanceDTO[]>([]);
const attendanceTotal = ref(0);
const wrongLocationTotal = ref(0);

const statusLabelMap: Record<string, string> = {
  checked_in: "Checked In",
  checked_out: "Checked Out",
  late: "Late",
  early_leave: "Early Leave",
  absent: "Absent",
  wrong_location_pending: "Wrong Location - Pending",
  wrong_location_approved: "Wrong Location - Approved",
  wrong_location_rejected: "Wrong Location - Rejected",
};

const dayTypeLabelMap: Record<string, string> = {
  working_day: "Working Day",
  weekend: "Weekend",
  public_holiday: "Public Holiday",
};

function toLabel(key: string, map: Record<string, string>): string {
  return (
    map[key] || key.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase())
  );
}

function aggregateBy(
  rows: AttendanceDTO[],
  keySelector: (row: AttendanceDTO) => string | null | undefined,
  labelMap: Record<string, string> = {},
): StatusSummaryRow[] {
  const grouped = new Map<string, number>();

  for (const row of rows) {
    const key = keySelector(row) || "unknown";
    grouped.set(key, (grouped.get(key) || 0) + 1);
  }

  const total = rows.length || 1;

  return Array.from(grouped.entries())
    .map(([key, count]) => ({
      key,
      label: toLabel(key, labelMap),
      count,
      percentage: `${((count / total) * 100).toFixed(1)}%`,
    }))
    .sort((a, b) => b.count - a.count);
}

const attendanceStatusSummary = computed(() =>
  aggregateBy(
    attendanceRows.value,
    (row) => String(row.status || "unknown").toLowerCase(),
    statusLabelMap,
  ),
);

const attendanceDayTypeSummary = computed(() =>
  aggregateBy(
    attendanceRows.value,
    (row) => String(row.day_type || "unknown").toLowerCase(),
    dayTypeLabelMap,
  ),
);

const wrongLocationStatusSummary = computed(() =>
  aggregateBy(
    wrongLocationRows.value,
    (row) => String(row.status || "unknown").toLowerCase(),
    {
      wrong_location_pending: "Pending",
      wrong_location_approved: "Approved",
      wrong_location_rejected: "Rejected",
    },
  ),
);

const totalAttendanceRecords = computed(() => attendanceTotal.value);
const totalWrongLocationRecords = computed(() => wrongLocationTotal.value);

const totalLate = computed(
  () =>
    attendanceRows.value.filter(
      (row) => String(row.status || "").toLowerCase() === "late",
    ).length,
);

const totalAbsent = computed(
  () =>
    attendanceRows.value.filter(
      (row) => String(row.status || "").toLowerCase() === "absent",
    ).length,
);

const locationRows = computed(() =>
  attendanceRows.value
    .filter(
      (row) =>
        typeof row.check_in_latitude === "number" &&
        typeof row.check_in_longitude === "number",
    )
    .slice(0, 20),
);

const selectedMapRowId = ref<string>("");

const selectedMapRow = computed(() => {
  if (!locationRows.value.length) return null;

  const found = locationRows.value.find(
    (row) => row.id === selectedMapRowId.value,
  );
  return found ?? locationRows.value[0] ?? null;
});

const selectedMapEmbedUrl = computed(() => {
  const row = selectedMapRow.value;
  if (
    !row ||
    typeof row.check_in_latitude !== "number" ||
    typeof row.check_in_longitude !== "number"
  ) {
    return "";
  }

  return `https://maps.google.com/maps?q=${row.check_in_latitude},${row.check_in_longitude}&z=16&output=embed`;
});

const showAttendanceSection = computed(
  () => summaryType.value === "all" || summaryType.value === "attendance",
);

const showWrongLocationSection = computed(
  () => summaryType.value === "all" || summaryType.value === "wrong-location",
);

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatCoordinate(value?: number | null): string {
  if (typeof value !== "number") return "-";
  return value.toFixed(6);
}

function buildGoogleMapsUrl(lat?: number | null, lng?: number | null): string {
  if (typeof lat !== "number" || typeof lng !== "number") return "";
  return `https://www.google.com/maps?q=${lat},${lng}`;
}

function handleMapRowChange(row?: AttendanceDTO | null) {
  if (row?.id) {
    selectedMapRowId.value = row.id;
  }
}

async function fetchReportData() {
  loading.value = true;
  try {
    const params = {
      ...(startDate.value ? { start_date: startDate.value } : {}),
      ...(endDate.value ? { end_date: endDate.value } : {}),
      page: 1,
      limit: 500,
    };
    const [attendanceResponse, wrongLocationResponse] = await Promise.all([
      attendanceService.getAttendances(params, { showError: false }),
      attendanceService.getWrongLocationReports(params, { showError: false }),
    ]);
    attendanceRows.value = attendanceResponse.items || [];
    attendanceTotal.value =
      attendanceResponse.pagination?.total ?? attendanceRows.value.length;
    wrongLocationRows.value = wrongLocationResponse.items || [];
    wrongLocationTotal.value =
      wrongLocationResponse.pagination?.total ?? wrongLocationRows.value.length;
    const firstLocation = attendanceRows.value.find(
      (row) =>
        typeof row.check_in_latitude === "number" &&
        typeof row.check_in_longitude === "number",
    );
    if (firstLocation?.id) {
      selectedMapRowId.value = firstLocation.id;
    }
  } catch {
    ElMessage.error("Failed to load attendance report summaries");
    attendanceRows.value = [];
    attendanceTotal.value = 0;
    wrongLocationRows.value = [];
    wrongLocationTotal.value = 0;
    selectedMapRowId.value = "";
  } finally {
    loading.value = false;
  }
}

import { onMounted } from "vue";
onMounted(() => {
  fetchReportData();
});
</script>

<template>
  <div class="attendance-reports-page">
    <OverviewHeader
      :title="'Attendance Reports'"
      :description="'Summary tables for attendance and wrong-location reports'"
      :backPath="'/hr/attendance'"
    >
      <template #actions>
        <BaseButton
          plain
          :loading="loading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="fetchReportData"
        >
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-card class="mt-4">
      <el-row :gutter="12" class="mb-2">
        <el-col :xs="24" :sm="8">
          <el-date-picker
            v-model="startDate"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="Start date"
            class="w-full"
          />
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-date-picker
            v-model="endDate"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="End date"
            class="w-full"
          />
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-select
            v-model="summaryType"
            class="w-full"
            placeholder="Summary type"
          >
            <el-option label="All summaries" value="all" />
            <el-option label="Attendance only" value="attendance" />
            <el-option label="Wrong-location only" value="wrong-location" />
          </el-select>
        </el-col>
      </el-row>

      <el-row :gutter="12">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="summary-stat">
            <p class="summary-stat__title">Attendance records</p>
            <p class="summary-stat__value">{{ totalAttendanceRecords }}</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="summary-stat">
            <p class="summary-stat__title">Wrong-location records</p>
            <p class="summary-stat__value">{{ totalWrongLocationRecords }}</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="summary-stat">
            <p class="summary-stat__title">Late records</p>
            <p class="summary-stat__value">{{ totalLate }}</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="summary-stat">
            <p class="summary-stat__title">Absent records</p>
            <p class="summary-stat__value">{{ totalAbsent }}</p>
          </div>
        </el-col>
      </el-row>

      <div class="mt-3 flex justify-end">
        <BaseButton type="primary" :loading="loading" @click="fetchReportData">
          Apply Filters
        </BaseButton>
      </div>
    </el-card>

    <el-row v-if="showAttendanceSection" :gutter="16" class="mt-4">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="table-header">Attendance Summary by Status</div>
          </template>

          <el-empty
            v-if="attendanceStatusSummary.length === 0"
            description="No attendance records found"
          />
          <el-table v-else :data="attendanceStatusSummary" stripe>
            <el-table-column prop="label" label="Status" min-width="190" />
            <el-table-column prop="count" label="Count" width="120" />
            <el-table-column prop="percentage" label="Percentage" width="130" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="table-header">Attendance Summary by Day Type</div>
          </template>

          <el-empty
            v-if="attendanceDayTypeSummary.length === 0"
            description="No attendance records found"
          />
          <el-table v-else :data="attendanceDayTypeSummary" stripe>
            <el-table-column prop="label" label="Day Type" min-width="180" />
            <el-table-column prop="count" label="Count" width="120" />
            <el-table-column prop="percentage" label="Percentage" width="130" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="showWrongLocationSection" class="mt-4">
      <template #header>
        <div class="table-header">Wrong-Location Report Summary</div>
      </template>

      <el-empty
        v-if="wrongLocationStatusSummary.length === 0"
        description="No wrong-location report records found"
      />

      <el-table v-else :data="wrongLocationStatusSummary" stripe>
        <el-table-column prop="label" label="Review Status" min-width="220" />
        <el-table-column prop="count" label="Count" width="140" />
        <el-table-column prop="percentage" label="Percentage" width="160" />
      </el-table>
    </el-card>

    <el-card v-if="showAttendanceSection" class="mt-4">
      <template #header>
        <div class="table-header">Check-In Location Map (Lat/Long)</div>
      </template>

      <el-empty
        v-if="locationRows.length === 0"
        description="No check-in latitude/longitude in current results"
      />

      <template v-else>
        <el-row :gutter="16">
          <el-col :xs="24" :lg="14">
            <el-table
              :data="locationRows"
              stripe
              highlight-current-row
              :current-row-key="selectedMapRowId"
              row-key="id"
              @current-change="handleMapRowChange"
            >
              <el-table-column label="Employee" min-width="180">
                <template #default="{ row }">
                  {{ displayRelation(row.employee_name, row.employee_id) }}
                </template>
              </el-table-column>
              <el-table-column label="Check-In Time" min-width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.check_in_time) }}
                </template>
              </el-table-column>
              <el-table-column label="Latitude" width="140">
                <template #default="{ row }">
                  {{ formatCoordinate(row.check_in_latitude) }}
                </template>
              </el-table-column>
              <el-table-column label="Longitude" width="140">
                <template #default="{ row }">
                  {{ formatCoordinate(row.check_in_longitude) }}
                </template>
              </el-table-column>
              <el-table-column label="Map" width="120">
                <template #default="{ row }">
                  <a
                    :href="
                      buildGoogleMapsUrl(
                        row.check_in_latitude,
                        row.check_in_longitude,
                      )
                    "
                    target="_blank"
                    rel="noopener noreferrer"
                    class="map-link"
                  >
                    Open
                  </a>
                </template>
              </el-table-column>
            </el-table>
          </el-col>

          <el-col :xs="24" :lg="10">
            <div class="map-preview-card">
              <div class="map-preview-header">Live Preview</div>
              <iframe
                v-if="selectedMapEmbedUrl"
                :src="selectedMapEmbedUrl"
                width="100%"
                height="320"
                style="border: 0"
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
              />
              <el-empty v-else description="Select a row to preview map" />
            </div>
          </el-col>
        </el-row>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.attendance-reports-page {
  display: flex;
  flex-direction: column;
}

.summary-stat {
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 10px 12px;
  background: #fafbfd;
}

.summary-stat__title {
  margin: 0;
  font-size: 12px;
  color: #606266;
}

.summary-stat__value {
  margin: 4px 0 0;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.table-header {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.map-preview-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 10px;
  background: #fcfcfd;
}

.map-preview-header {
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
  font-weight: 600;
}

.map-link {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
