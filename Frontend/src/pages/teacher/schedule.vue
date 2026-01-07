<script setup lang="ts">
import { ref, computed, onMounted, h, watch } from "vue";
import { storeToRefs } from "pinia";
import { navigateTo } from "nuxt/app";

definePageMeta({ layout: "default" });

/* Types */
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { TeacherScheduleDTO } from "~/api/teacher/dto";
import type { ClassSectionDTO } from "~/api/types/school.dto";

/* Base components */
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";
import BaseButton from "~/components/base/BaseButton.vue";

/* Element Plus */
import {
  ElEmpty,
  ElSkeleton,
  ElAlert,
  ElTag,
  ElRow,
  ElCol,
  ElSelect,
  ElOption,
  ElTimeSelect,
  ElButton,
  ElSpace,
} from "element-plus";

/* Services */
import { teacherService } from "~/api/teacher";

/* Pagination + header stats */
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { useHeaderState } from "~/composables/ui/useHeaderState";

/* Auth + roles */
import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/api/types/enums/role.enum";

/* Preferences store (page size) */
import { usePreferencesStore } from "~/stores/preferencesStore";

/* ---------------------- helpers ---------------------- */
const weekdayShortLabels = [
  "Mon",
  "Tue",
  "Wed",
  "Thu",
  "Fri",
  "Sat",
  "Sun",
] as const;

function toDayLabel(dayOfWeek?: number) {
  const idx = (Number(dayOfWeek || 1) - 1) as number;
  return weekdayShortLabels[idx] ?? "Unknown";
}

/* ---------------------- filters ---------------------- */
type ScheduleFilter = {
  class_id?: string;
  day_of_week?: number;
  start_time_from?: string; // "HH:mm"
  start_time_to?: string; // "HH:mm"
};

const filterRef = ref<ScheduleFilter>({});

const selectedClassId = ref<string>("all");
const selectedDay = ref<number | "all">("all");
const startTimeFrom = ref<string | null>(null);
const startTimeTo = ref<string | null>(null);

const canReset = computed(() => {
  return (
    selectedClassId.value !== "all" ||
    selectedDay.value !== "all" ||
    !!startTimeFrom.value ||
    !!startTimeTo.value
  );
});

function normalizeTimeRange() {
  if (
    startTimeFrom.value &&
    startTimeTo.value &&
    startTimeFrom.value > startTimeTo.value
  ) {
    const tmp = startTimeFrom.value;
    startTimeFrom.value = startTimeTo.value;
    startTimeTo.value = tmp;
  }
}

function applyFilters() {
  normalizeTimeRange();
  filterRef.value = {
    class_id:
      selectedClassId.value !== "all" ? selectedClassId.value : undefined,
    day_of_week:
      selectedDay.value !== "all" ? Number(selectedDay.value) : undefined,
    start_time_from: startTimeFrom.value || undefined,
    start_time_to: startTimeTo.value || undefined,
  };
}

function resetFilters() {
  selectedClassId.value = "all";
  selectedDay.value = "all";
  startTimeFrom.value = null;
  startTimeTo.value = null;
  applyFilters();
  goPage(1);
}

/* ---------------------- columns ---------------------- */
const teacherScheduleColumns: ColumnConfig<TeacherScheduleDTO>[] = [
  {
    field: "day_label",
    label: "Day",
    sortable: true,
    controls: false,
    minWidth: "120px",
    render: (row) => {
      const v = String(
        (row as TeacherScheduleDTO).day_label ?? toDayLabel(row.day_of_week)
      );
      return h(
        ElTag,
        { type: "info", effect: "plain", size: "small" },
        { default: () => v }
      );
    },
  },
  {
    field: "start_time",
    label: "Time",
    sortable: true,
    controls: false,
    minWidth: "180px",
    render: (row) => {
      const start = row.start_time ?? "—";
      const end = row.end_time ?? "—";
      return h("span", { class: "font-mono text-xs" }, `${start} – ${end}`);
    },
  },
  {
    field: "class_name",
    label: "Class",
    sortable: true,
    controls: false,
    minWidth: "220px",
    showOverflowTooltip: true,
  },
  {
    field: "subject_label",
    label: "Subject",
    sortable: false,
    controls: false,
    minWidth: "320px",
    useSlot: true,
    slotName: "subject",
  },
  {
    field: "room",
    label: "Room",
    sortable: true,
    controls: false,
    minWidth: "140px",
    render: (row) => {
      const v = String((row as any).room ?? "").trim();
      if (!v) {
        return h(
          "span",
          {
            class:
              "inline-flex items-center px-2 py-[2px] rounded-full text-xs " +
              "border border-[var(--border-color)] text-[var(--muted-color)] " +
              "bg-[color-mix(in_srgb,var(--hover-bg)_55%,transparent)]",
          },
          "Not set"
        );
      }
      return h("span", { class: "font-medium" }, v);
    },
  },
];

/* ---------------------- stores/services ---------------------- */
const authStore = useAuthStore();
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

const teacherApi = teacherService();

/* ---------------------- access ---------------------- */
const canAccess = computed(() => {
  const r = authStore.user?.role;
  return r === Role.TEACHER || r === Role.ADMIN;
});

/* ---------------------- classes for filter ---------------------- */
const classesLoading = ref(false);
const classOptions = ref<ClassSectionDTO[]>([]);

async function loadMyClassesForFilter() {
  classesLoading.value = true;
  try {
    const res: any = await teacherApi.teacher.listMyClasses({
      showError: false,
    } as any);
    const payload = res?.data ?? res;
    const data = payload?.data ?? payload;
    classOptions.value = (data?.items ?? []) as ClassSectionDTO[];
  } finally {
    classesLoading.value = false;
  }
}

/* ---------------------- paginated fetch ---------------------- */
const {
  data: rows,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  initialLoading,
  fetching,
  fetchPage,
  goPage,
} = usePaginatedFetch<TeacherScheduleDTO, ScheduleFilter>(
  async (filter, page, size, signal) => {
    const res: any = await teacherApi.teacher.listMySchedule(
      {
        page,
        page_size: size,
        class_id: filter?.class_id,
        day_of_week: filter?.day_of_week,
        start_time_from: filter?.start_time_from,
        start_time_to: filter?.start_time_to,
        signal,
      },
      { showError: false } as any
    );

    const payload = res?.data?.data ?? res?.data ?? res; // { items, total, ... }

    const itemsRaw = (payload?.items ?? []) as TeacherScheduleDTO[];
    const total = Number(payload?.total ?? itemsRaw.length);

    const items = itemsRaw.map((item: any) => ({
      ...item,
      day_label: item.day_label ?? toDayLabel(item.day_of_week),
    })) as TeacherScheduleDTO[];

    return { items, total };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: filterRef,
  }
);

const tableLoading = computed(() => initialLoading.value || fetching.value);

/* ---------------------- UI states ---------------------- */
const hasRows = computed(() => (rows.value?.length ?? 0) > 0);
const showTable = computed(() => !tableLoading.value && hasRows.value);
const showEmptyState = computed(() => !tableLoading.value && !hasRows.value);

const errorMessage = computed(() =>
  tableError.value
    ? tableError.value.message ?? "Failed to load schedule."
    : null
);

/* ---------------------- header stats ---------------------- */
const totalLessons = computed(() => totalRows.value ?? 0);

const totalDistinctClassesOnPage = computed(() => {
  const items = rows.value ?? [];
  return new Set(items.map((s) => s.class_name ?? "__none__")).size;
});

const totalDistinctSubjectsOnPage = computed(() => {
  const items = rows.value ?? [];
  return new Set(items.map((s) => s.subject_label ?? "__none__")).size;
});

const { headerState } = useHeaderState({
  items: [
    {
      key: "lessons",
      getValue: () => totalLessons.value,
      singular: "lesson",
      plural: "lessons",
      suffix: "in total",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "classes_page",
      getValue: () => totalDistinctClassesOnPage.value,
      singular: "class",
      plural: "classes",
      suffix: "on this page",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
    {
      key: "subjects_page",
      getValue: () => totalDistinctSubjectsOnPage.value,
      singular: "subject",
      plural: "subjects",
      suffix: "on this page",
      variant: "secondary",
      dotClass: "bg-indigo-500",
      hideWhenZero: false,
    },
  ],
});

/* ---------------------- actions ---------------------- */
async function fetchSchedule(page = currentPage.value || 1) {
  await fetchPage(page);
}

async function handleRefresh() {
  await fetchSchedule(currentPage.value || 1);
}

function handlePageSizeChange(size: number) {
  prefs.setTablePageSize(size);
}

/* When filter UI changes, apply and jump to page 1 */
watch([selectedClassId, selectedDay, startTimeFrom, startTimeTo], () => {
  applyFilters();
  goPage(1);
});

/* ---------------------- mount ---------------------- */
onMounted(async () => {
  if (!canAccess.value) {
    await navigateTo("/");
    return;
  }

  applyFilters();
  await Promise.all([loadMyClassesForFilter(), fetchSchedule(1)]);
});
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="Teacher Schedule"
      description="Your weekly teaching schedule (classes, subjects, time, and room)."
      :loading="tableLoading"
      :showRefresh="false"
      :stats="headerState"
    >
      <template #filters>
        <!-- ✅ Element Plus layout: responsive row/cols -->
        <ElRow :gutter="10" align="middle" class="mb-2">
          <ElCol :xs="24" :sm="12" :md="6">
            <ElSelect
              v-model="selectedClassId"
              size="small"
              class="w-full"
              :loading="classesLoading"
              placeholder="All classes"
              clearable
            >
              <ElOption label="All classes" value="all" />
              <ElOption
                v-for="c in classOptions"
                :key="c.id"
                :label="c.name"
                :value="c.id"
              />
            </ElSelect>
          </ElCol>

          <ElCol :xs="24" :sm="12" :md="5">
            <ElSelect
              v-model="selectedDay"
              size="small"
              class="w-full"
              placeholder="All days"
              clearable
            >
              <ElOption label="All days" value="all" />
              <ElOption label="Mon" :value="1" />
              <ElOption label="Tue" :value="2" />
              <ElOption label="Wed" :value="3" />
              <ElOption label="Thu" :value="4" />
              <ElOption label="Fri" :value="5" />
              <ElOption label="Sat" :value="6" />
              <ElOption label="Sun" :value="7" />
            </ElSelect>
          </ElCol>

          <ElCol :xs="24" :sm="12" :md="5">
            <ElTimeSelect
              v-model="startTimeFrom"
              size="small"
              class="w-full"
              start="06:00"
              step="00:30"
              end="20:00"
              placeholder="From time"
              clearable
            />
          </ElCol>

          <ElCol :xs="24" :sm="12" :md="5">
            <ElTimeSelect
              v-model="startTimeTo"
              size="small"
              class="w-full"
              start="06:00"
              step="00:30"
              end="20:00"
              placeholder="To time"
              clearable
            />
          </ElCol>

          <ElCol :xs="24" :md="3" class="text-right">
            <ElButton
              plain
              class="w-full md:w-auto"
              :disabled="!canReset"
              @click="resetFilters"
            >
              Reset
            </ElButton>
          </ElCol>
        </ElRow>
      </template>

      <template #actions>
        <BaseButton plain :loading="tableLoading" @click="handleRefresh">
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <transition name="el-fade-in">
      <ElAlert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="rounded-xl border shadow-sm"
      />
    </transition>

    <TableCard
      title="Weekly schedule"
      description="This page shows your current schedule. Subjects may be optional for some classes."
      :rightText="totalLessons ? `Total: ${totalLessons}` : ''"
      padding="16px"
    >
      <div v-if="tableLoading" class="py-4">
        <ElSkeleton :rows="4" animated />
      </div>

      <SmartTable
        v-if="showTable"
        :data="rows"
        :columns="teacherScheduleColumns"
        :loading="tableLoading"
      >
        <template #subject="{ row }">
          <div class="subject-cell w-full min-w-0">
            <div class="flex items-start justify-between gap-3 min-w-0">
              <div class="min-w-0">
                <div class="truncate font-medium leading-5">
                  {{ row.subject_label || "No subject assigned" }}
                </div>
                <div class="truncate text-xs schedule-muted leading-4">
                  Class: {{ row.class_name || "—" }}
                </div>
              </div>

              <ElTag
                size="small"
                effect="plain"
                class="shrink-0"
                :type="row.subject_label ? 'success' : 'info'"
              >
                {{ row.subject_label ? "Assigned" : "None" }}
              </ElTag>
            </div>
          </div>
        </template>
      </SmartTable>

      <div v-if="showEmptyState" class="py-10">
        <ElEmpty
          description="You do not have any scheduled lessons yet."
          :image-size="100"
        />
      </div>

      <el-row v-if="showTable && totalRows > 0" justify="end" class="mt-4">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalRows"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="goPage"
          @size-change="handlePageSizeChange"
        />
      </el-row>
    </TableCard>
  </div>
</template>

<style scoped>
.schedule-muted {
  color: var(--muted-color);
}

.subject-cell {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 6px 10px;
  background: color-mix(in srgb, var(--hover-bg) 45%, transparent);
}
</style>
