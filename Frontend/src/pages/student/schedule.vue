<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, onMounted, computed, onBeforeUnmount } from "vue";
import {
  ElMessage,
  ElAlert,
  ElCard,
  ElEmpty,
  ElSkeleton,
  ElTable,
  ElTableColumn,
  ElInput,
  ElSelect,
  ElOption,
  ElSegmented,
  ElTag,
  ElRow,
  ElCol,
  ElButton,
} from "element-plus";

import { studentService } from "~/api/student";
import type { ScheduleDTO } from "~/api/types/school.dto";
import type { StudentScheduleFilterDTO } from "~/api/student/student.dto";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import { useHeaderState } from "~/composables/ui/useHeaderState";

import { dayOptions as DAY_OPTIONS } from "~/utils/constants/dayOptions";

const student = studentService();

/* ---------------- state ---------------- */
const loading = ref(false);
const errorMessage = ref<string | null>(null);
const schedule = ref<ScheduleDTO[]>([]);

/** prevent stale responses overriding newer refreshes */
let requestSeq = 0;

/* ---------------- helpers ---------------- */
const dayOfWeekLabel = (d: number | string) => {
  const map: Record<string, string> = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
  };
  return map[String(d)] ?? String(d);
};

const safeText = (v: any, fallback = "—") => {
  const s = String(v ?? "").trim();
  return s ? s : fallback;
};

const toMinutes = (t?: string) => {
  // expects "HH:mm" or "HH:mm:ss"
  if (!t) return Number.MAX_SAFE_INTEGER;
  const [hh, mm] = t.split(":");
  const h = Number(hh);
  const m = Number(mm);
  return (Number.isFinite(h) ? h : 0) * 60 + (Number.isFinite(m) ? m : 0);
};

const durationLabel = (start?: string, end?: string) => {
  const a = toMinutes(start);
  const b = toMinutes(end);
  if (
    !Number.isFinite(a) ||
    !Number.isFinite(b) ||
    a === Number.MAX_SAFE_INTEGER ||
    b === Number.MAX_SAFE_INTEGER
  )
    return "—";
  const diff = Math.max(0, b - a);
  if (!diff) return "—";
  const h = Math.floor(diff / 60);
  const m = diff % 60;
  if (h && m) return `${h}h ${m}m`;
  if (h) return `${h}h`;
  return `${m}m`;
};

const extractErrorMessage = (err: any) => {
  return (
    err?.response?.data?.user_message ||
    err?.response?.data?.message ||
    err?.message ||
    "Failed to load schedule. Please try again."
  );
};

/* ---------------- UI state ---------------- */
type ViewMode = "day" | "table";
const viewMode = ref<ViewMode>("day");

const selectedDay = ref<"all" | 1 | 2 | 3 | 4 | 5 | 6 | 7>("all");
const search = ref("");

/** IMPORTANT: when clearable is clicked, Element Plus may set model to null/undefined.
 * We force it back to "all" (your default).
 */
const onDayClear = () => {
  selectedDay.value = "all";
};

const onSearchClear = () => {
  search.value = "";
};

/* ---------------- view model ---------------- */
type ScheduleRowVM = {
  id: string;
  day: number;
  dayLabel: string;
  start: string;
  end: string;
  duration: string;

  classId: string;
  className: string;

  teacherName: string;
  room: string;

  subjectId: string;
  subjectLabel: string;

  updatedAt?: string;
};

const rows = computed<ScheduleRowVM[]>(() => {
  return (schedule.value ?? [])
    .map((s: any, idx) => {
      const id = String(s.id ?? s._id ?? `${idx}`);
      const day = Number(s.day_of_week ?? 0);

      return {
        id,
        day,
        dayLabel: dayOfWeekLabel(day),

        start: safeText(s.start_time),
        end: safeText(s.end_time),
        duration: durationLabel(s.start_time, s.end_time),

        classId: safeText(s.class_id, ""),
        className: safeText(s.class_name),

        teacherName: safeText(s.teacher_name),
        room: safeText(s.room),

        subjectId: safeText(s.subject_id, ""),
        subjectLabel: safeText(s.subject_label),

        updatedAt: s?.lifecycle?.updated_at
          ? String(s.lifecycle.updated_at)
          : undefined,
      };
    })
    .sort((a, b) => {
      if (a.day !== b.day) return a.day - b.day;
      return toMinutes(a.start) - toMinutes(b.start);
    });
});

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase();

  return rows.value.filter((r) => {
    const dayOk =
      selectedDay.value === "all" ? true : r.day === selectedDay.value;
    if (!dayOk) return false;

    if (!q) return true;

    const subject = r.subjectLabel.toLowerCase();
    if (subject.includes(q)) return true;

    const secondary = [r.teacherName, r.room, r.dayLabel, r.start, r.end]
      .join(" ")
      .toLowerCase();

    return secondary.includes(q);
  });
});

const groupedByDay = computed(() => {
  const map = new Map<number, ScheduleRowVM[]>();
  for (const r of filteredRows.value) {
    const key = r.day || 0;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(r);
  }
  return [...map.entries()].sort((a, b) => a[0] - b[0]);
});

/* ---------------- overview stats ---------------- */
const totalLessons = computed(() => filteredRows.value.length);
const distinctClasses = computed(
  () => new Set(filteredRows.value.map((s) => s.className)).size
);
const distinctSubjects = computed(() => {
  const set = new Set(
    filteredRows.value.map((s) => s.subjectLabel).filter((x) => x && x !== "—")
  );
  return set.size;
});

const { headerState } = useHeaderState({
  items: [
    {
      key: "lessons",
      getValue: () => totalLessons.value,
      singular: "lesson",
      plural: "lessons",
      suffix: "shown",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "classes",
      getValue: () => distinctClasses.value,
      singular: "class",
      plural: "classes",
      suffix: "distinct",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
    {
      key: "subjects",
      getValue: () => distinctSubjects.value,
      singular: "subject",
      plural: "subjects",
      suffix: "distinct",
      variant: "secondary",
      dotClass: "bg-violet-500",
      hideWhenZero: false,
    },
  ],
});

/* ---------------- load schedule ---------------- */
const loadSchedule = async () => {
  const seq = ++requestSeq;

  loading.value = true;
  errorMessage.value = null;

  try {
    const params: StudentScheduleFilterDTO = {};
    const res = await student.student.getMySchedule(params);

    if (seq !== requestSeq) return;
    schedule.value = (res as any)?.items ?? [];
  } catch (err: any) {
    if (seq !== requestSeq) return;
    errorMessage.value = extractErrorMessage(err);
    schedule.value = [];
  } finally {
    if (seq === requestSeq) loading.value = false;
  }
};

const handleRefresh = async () => {
  if (loading.value) return;
  await loadSchedule();
  ElMessage.success("Schedule refreshed");
};

const clearFilters = () => {
  selectedDay.value = "all";
  search.value = "";
};

onMounted(loadSchedule);
onBeforeUnmount(() => {
  requestSeq++;
});
</script>

<template>
  <div class="p-4 space-y-4 max-w-6xl mx-auto pb-10" v-loading="loading">
    <OverviewHeader
      title="My Schedule"
      description="Your lessons, timings, and classroom details."
      :loading="loading"
      :showRefresh="true"
      :stats="headerState"
      @refresh="handleRefresh"
    >
      <template #filters>
        <el-card
          shadow="never"
          class="rounded-2xl border"
          style="
            background: color-mix(in srgb, var(--color-card) 96%, transparent);
            border-color: var(--border-color);
          "
        >
          <el-row :gutter="12" class="items-center">
            <!-- Left: Day + Search -->
            <el-col :xs="24" :md="16">
              <el-row :gutter="12" class="items-center">
                <el-col :xs="24" :sm="10" :md="8">
                  <ElSelect
                    v-model="selectedDay"
                    class="w-full"
                    placeholder="Filter by day"
                    :disabled="loading"
                    clearable
                    @clear="onDayClear"
                  >
                    <ElOption
                      v-for="opt in DAY_OPTIONS"
                      :key="String(opt.value)"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </el-col>

                <el-col :xs="24" :sm="14" :md="16">
                  <ElInput
                    v-model="search"
                    class="w-full"
                    clearable
                    placeholder="Search subject (and teacher / room...)"
                    :disabled="loading"
                    @clear="onSearchClear"
                  />
                </el-col>
              </el-row>
            </el-col>

            <!-- Right: View Mode + Reset -->
            <el-col :xs="24" :md="8">
              <div
                class="flex flex-wrap items-center justify-start md:justify-end gap-2"
              >
                <ElSegmented
                  v-model="viewMode"
                  :options="[
                    { label: 'By day', value: 'day' },
                    { label: 'Table', value: 'table' },
                  ]"
                  :disabled="loading"
                />

                <ElButton :disabled="loading" @click="clearFilters"
                  >Reset</ElButton
                >
              </div>
            </el-col>
          </el-row>
        </el-card>
      </template>
    </OverviewHeader>

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

    <!-- Skeleton for first load -->
    <el-card
      v-if="loading && !rows.length"
      shadow="never"
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    >
      <el-skeleton animated :rows="8" />
    </el-card>

    <!-- Empty -->
    <el-empty
      v-else-if="!loading && !filteredRows.length"
      description="No schedule found for these filters."
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    />

    <!-- Day view -->
    <div v-else-if="viewMode === 'day'" class="space-y-3">
      <el-card
        v-for="[day, items] in groupedByDay"
        :key="day"
        shadow="hover"
        class="rounded-2xl border"
        style="
          background: color-mix(in srgb, var(--color-card) 96%, transparent);
          border-color: var(--border-color);
        "
      >
        <template #header>
          <el-row :gutter="12" class="items-center">
            <el-col :xs="24" :sm="16">
              <div class="flex items-center gap-2 min-w-0">
                <div
                  class="font-semibold truncate"
                  style="color: var(--text-color)"
                >
                  {{ items[0]?.dayLabel ?? "Schedule" }}
                </div>

                <ElTag size="small" effect="plain" type="info">
                  {{ items.length }} lesson{{ items.length === 1 ? "" : "s" }}
                </ElTag>
              </div>
              <div class="text-xs mt-1" style="color: var(--muted-color)">
                Sorted by start time
              </div>
            </el-col>

            <el-col :xs="24" :sm="8">
              <div class="flex sm:justify-end">
                <div class="text-xs" style="color: var(--muted-color)">
                  Showing {{ items.length }}
                </div>
              </div>
            </el-col>
          </el-row>
        </template>

        <el-table
          :data="items"
          size="small"
          style="width: 100%"
          highlight-current-row
          class="app-table rounded-xl overflow-hidden"
        >
          <el-table-column prop="start" label="Start" min-width="90" />
          <el-table-column prop="end" label="End" min-width="90" />
          <el-table-column prop="duration" label="Duration" min-width="110" />

          <el-table-column
            prop="className"
            label="Class"
            min-width="220"
            show-overflow-tooltip
          />

          <el-table-column
            prop="subjectLabel"
            label="Subject"
            min-width="220"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div class="flex items-center gap-2 min-w-0">
                <span
                  class="inline-block h-2 w-2 rounded-full"
                  style="background: var(--color-primary)"
                />
                <span class="truncate" style="color: var(--text-color)">{{
                  row.subjectLabel
                }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            prop="teacherName"
            label="Teacher"
            min-width="200"
            show-overflow-tooltip
          />
          <el-table-column
            prop="room"
            label="Room"
            min-width="120"
            show-overflow-tooltip
          />
        </el-table>
      </el-card>
    </div>

    <!-- Table view -->
    <el-card
      v-else
      shadow="hover"
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    >
      <template #header>
        <el-row :gutter="12" class="items-center">
          <el-col :xs="24" :sm="16">
            <div class="font-semibold" style="color: var(--text-color)">
              All lessons
            </div>
            <div class="text-xs mt-1" style="color: var(--muted-color)">
              Sorted by day then start time
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="flex sm:justify-end">
              <div class="text-xs" style="color: var(--muted-color)">
                {{ filteredRows.length }} item{{
                  filteredRows.length === 1 ? "" : "s"
                }}
              </div>
            </div>
          </el-col>
        </el-row>
      </template>

      <el-table
        :data="filteredRows"
        size="small"
        style="width: 100%"
        highlight-current-row
        class="app-table rounded-xl overflow-hidden"
      >
        <el-table-column prop="dayLabel" label="Day" min-width="130" />
        <el-table-column prop="start" label="Start" min-width="90" />
        <el-table-column prop="end" label="End" min-width="90" />
        <el-table-column prop="duration" label="Duration" min-width="110" />
        <el-table-column
          prop="className"
          label="Class"
          min-width="220"
          show-overflow-tooltip
        />
        <el-table-column
          prop="subjectLabel"
          label="Subject"
          min-width="220"
          show-overflow-tooltip
        />
        <el-table-column
          prop="teacherName"
          label="Teacher"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column
          prop="room"
          label="Room"
          min-width="120"
          show-overflow-tooltip
        />
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
/* keep consistent with your token system */
:deep(.el-card) {
  border-radius: 16px;
}

/* Table: consistent borders + header using your tokens */
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

:deep(.app-table.el-table--border .el-table__inner-wrapper::after),
:deep(.app-table.el-table--border::after),
:deep(.app-table.el-table--border::before) {
  background-color: var(--border-color);
}

/* inputs/selects/segmented blend with theme */
:deep(.el-input__wrapper),
:deep(.el-select__wrapper),
:deep(.el-segmented) {
  border-radius: 12px;
}
</style>
