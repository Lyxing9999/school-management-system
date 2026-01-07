<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, onMounted, computed, onBeforeUnmount } from "vue";
import {
  ElMessage,
  ElInput,
  ElSelect,
  ElOption,
  ElSegmented,
  ElTag,
} from "element-plus";

import { studentService } from "~/api/student";
import type { ScheduleDTO } from "~/api/types/school.dto";
import type { StudentScheduleFilterDTO } from "~/api/student/student.dto";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import { useHeaderState } from "~/composables/ui/useHeaderState";

const student = studentService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const schedule = ref<ScheduleDTO[]>([]);

/** prevent stale responses overriding newer refreshes */
let requestSeq = 0;

/* ---------------- helpers ---------------- */

import { dayOptions as DAY_OPTIONS } from "~/utils/constants/dayOptions";

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

/* ---------------- UI state ---------------- */

type ViewMode = "day" | "table";
const viewMode = ref<ViewMode>("day");

const selectedDay = ref<"all" | 1 | 2 | 3 | 4 | 5 | 6 | 7>("all");
const search = ref("");

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

    const haystack = [
      r.dayLabel,
      r.className,
      r.teacherName,
      r.subjectLabel,
      r.room,
      r.start,
      r.end,
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(q);
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
    schedule.value = res.items ?? [];
  } catch (err: any) {
    if (seq !== requestSeq) return;

    const msg =
      err?.response?.data?.user_message ||
      err?.response?.data?.message ||
      err?.message ||
      "Failed to load schedule. Please try again.";

    errorMessage.value = msg;
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
  <div class="p-4 space-y-4" v-loading="loading">
    <OverviewHeader
      title="My Schedule"
      description="Your lessons, timings, and classroom details."
      :loading="loading"
      :showRefresh="true"
      :stats="headerState"
      @refresh="handleRefresh"
    >
      <template #filters>
        <div
          class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <!-- Left: Day + Search -->
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
            <ElSelect
              v-model="selectedDay"
              class="w-full sm:w-[200px]"
              placeholder="Filter by day"
              :disabled="loading"
            >
              <ElOption
                v-for="opt in DAY_OPTIONS"
                :key="String(opt.value)"
                :label="opt.label"
                :value="opt.value"
              />
            </ElSelect>

            <ElInput
              v-model="search"
              class="w-full sm:w-[320px]"
              clearable
              placeholder="Search class, subject, teacher, room..."
              :disabled="loading"
            />
          </div>

          <!-- Right: View Mode + Reset -->
          <div class="flex items-center gap-2">
            <ElSegmented
              v-model="viewMode"
              :options="[
                { label: 'By day', value: 'day' },
                { label: 'Table', value: 'table' },
              ]"
              :disabled="loading"
            />

            <button
              type="button"
              class="px-3 py-2 rounded-lg text-sm border shadow-sm hover:opacity-90"
              style="
                background: color-mix(
                  in srgb,
                  var(--color-card) 92%,
                  transparent
                );
                border-color: var(--border-color);
                color: var(--text-color);
              "
              @click="clearFilters"
              :disabled="loading"
            >
              Reset
            </button>
          </div>
        </div>
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
    <el-card v-if="loading && !rows.length" shadow="never" class="rounded-xl">
      <el-skeleton animated :rows="8" />
    </el-card>

    <!-- Empty -->
    <el-empty
      v-else-if="!loading && !filteredRows.length"
      description="No schedule found for these filters."
      class="rounded-xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 92%, transparent);
        border-color: var(--border-color);
      "
    />

    <!-- Day view -->
    <div v-else-if="viewMode === 'day'" class="space-y-3">
      <el-card
        v-for="[day, items] in groupedByDay"
        :key="day"
        shadow="hover"
        class="rounded-xl"
        style="
          background: color-mix(in srgb, var(--color-card) 96%, transparent);
          border-color: var(--border-color);
        "
      >
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="font-semibold" style="color: var(--text-color)">
                {{ items[0]?.dayLabel ?? "Schedule" }}
              </div>

              <ElTag size="small" effect="plain" type="info">
                {{ items.length }} lesson{{ items.length === 1 ? "" : "s" }}
              </ElTag>
            </div>

            <div class="text-xs" style="color: var(--muted-color)">
              Sorted by start time
            </div>
          </div>
        </template>

        <el-table
          :data="items"
          border
          size="small"
          style="width: 100%"
          :header-cell-style="{
            background:
              'color-mix(in srgb, var(--color-card) 85%, #ffffff 15%)',
            color: 'var(--text-color)',
            fontWeight: '600',
            fontSize: '13px',
          }"
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

    <!-- Table view -->
    <el-card
      v-else
      shadow="hover"
      class="rounded-xl"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    >
      <template #header>
        <div class="flex items-center justify-between">
          <div class="font-semibold" style="color: var(--text-color)">
            All lessons
          </div>
          <div class="text-xs" style="color: var(--muted-color)">
            {{ filteredRows.length }} item{{
              filteredRows.length === 1 ? "" : "s"
            }}
          </div>
        </div>
      </template>

      <el-table
        :data="filteredRows"
        border
        size="small"
        style="width: 100%"
        :default-sort="{ prop: 'day', order: 'ascending' }"
        :header-cell-style="{
          background: 'color-mix(in srgb, var(--color-card) 85%, #ffffff 15%)',
          color: 'var(--text-color)',
          fontWeight: '600',
          fontSize: '13px',
        }"
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
/* Keep UI consistent with your theme tokens */
:deep(.el-card) {
  border-radius: 16px;
}
:deep(.el-table) {
  border-radius: 12px;
}
</style>
