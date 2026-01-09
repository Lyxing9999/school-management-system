<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, onMounted, computed, onBeforeUnmount, watch } from "vue";
import {
  ElAlert,
  ElCard,
  ElEmpty,
  ElSkeleton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElSelect,
  ElOption,
  ElButton,
  ElPagination,
  ElProgress,
  ElRow,
  ElCol,
} from "element-plus";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import { useHeaderState } from "~/composables/ui/useHeaderState";
import { formatDate } from "~/utils/date/formatDate";

import { studentService } from "~/api/student";
import type {
  StudentGradeDTO,
  StudentGradePagedDTO,
  StudentGradesFilterDTO,
} from "~/api/student/student.dto";

import { usePreferencesStore } from "~/stores/preferencesStore";

const student = studentService();
const prefs = usePreferencesStore();

/* ---------------- state ---------------- */
const loading = ref(false);
const errorMessage = ref<string | null>(null);

const items = ref<StudentGradeDTO[]>([]);
const total = ref(0); // server total (after filters)
const page = ref(1);
const pageSize = ref<number>(prefs.getTablePageSize());
const pages = ref(1);

/**
 * Single dropdown "Term" that includes year:
 *  - "" => all
 *  - "2026-S1", "2026-S2", "2025-S1", ...
 */
const termFilter = ref<string>("");

let requestSeq = 0;

/* ---------------- helpers ---------------- */
const safeText = (v: any, fallback = "—") => {
  const s = String(v ?? "").trim();
  return s ? s : fallback;
};

const toNumber = (v: any) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};

const parseDate = (v: any) => {
  const d = new Date(v ?? "");
  return Number.isNaN(d.getTime()) ? null : d;
};

const extractErrorMessage = (err: any) => {
  return (
    err?.response?.data?.user_message ||
    err?.response?.data?.message ||
    err?.message ||
    "Failed to load grades. Please try again."
  );
};

const tagTypeByGradeType = (value?: string) => {
  const v = String(value ?? "").toLowerCase();
  if (v === "assignment") return "success";
  if (v === "exam") return "danger";
  if (v === "quiz") return "warning";
  return "info";
};

const formatType = (value?: string) => {
  const v = String(value ?? "").trim();
  if (!v) return "—";
  return v.charAt(0).toUpperCase() + v.slice(1);
};

function clampPct(score: number | null) {
  if (typeof score !== "number") return 0;
  return Math.max(0, Math.min(100, Math.round(score)));
}

type GradeRowVM = {
  id: string;
  subjectLabel: string;
  className: string;
  score: number | null;
  type: string;
  term: string; // base term like "S1" / "S2"
  createdAtRaw: string;
  createdAtDate: Date | null;
};

function avgScore(list: GradeRowVM[]) {
  const nums = list
    .map((i) => i.score)
    .filter((n): n is number => typeof n === "number");
  if (!nums.length) return null;
  const a = nums.reduce((x, y) => x + y, 0) / nums.length;
  return Math.round(a * 10) / 10;
}

function progressVars(
  score: number | null,
  mode: "primary" | "semantic" = "semantic"
) {
  const pct = clampPct(score);

  const bar =
    mode === "primary"
      ? "var(--color-primary)"
      : pct >= 70
      ? "var(--button-success-bg)"
      : pct >= 40
      ? "var(--button-warning-bg)"
      : "var(--button-danger-bg)";

  return {
    "--pbar": bar,
    "--ptrack": "color-mix(in srgb, var(--border-color) 55%, transparent)",
  } as Record<string, string>;
}

/* ---------------- year/term dropdown ---------------- */
/**
 * 10 years, starting from current year going backward:
 * [2026, 2025, 2024, ...]
 */
const START_YEAR = 2025;
const yearOptions = computed(() => {
  const current = new Date().getFullYear();
  const years: number[] = [];
  for (let y = current; y >= START_YEAR; y--) years.push(y);
  return years;
});

/* ---------------- view model ---------------- */
const rows = computed<GradeRowVM[]>(() => {
  return (items.value ?? [])
    .map((g: any, idx) => {
      const createdAt =
        g.lifecycle?.created_at ?? g.created_at ?? g.createdAt ?? "";
      return {
        id: String(g.id ?? g._id ?? `${idx}`),
        subjectLabel: safeText(g.subject_label ?? g.subjectLabel),
        className: safeText(g.class_name ?? g.className),
        score: toNumber(g.score),
        type: safeText(g.type, ""),
        term: safeText(g.term, "—"),
        createdAtRaw: createdAt,
        createdAtDate: parseDate(createdAt),
      };
    })
    .sort(
      (a, b) =>
        (b.createdAtDate?.getTime() ?? 0) - (a.createdAtDate?.getTime() ?? 0)
    );
});

/**
 * Always show S1 then S2 (stable order), plus any extra term strings after.
 */
const baseTerms = computed(() => {
  const set = new Set<string>(["S1", "S2"]);
  for (const r of rows.value) {
    const t = String(r.term ?? "").trim();
    if (t && t !== "—") set.add(t);
  }

  const ordered = ["S1", "S2"];
  const extras = Array.from(set)
    .filter((x) => !ordered.includes(x))
    .sort();

  return [...ordered.filter((x) => set.has(x)), ...extras];
});

/**
 * Term dropdown options:
 * 2026-S1, 2026-S2, 2025-S1, 2025-S2, ...
 */
const termOptions = computed(() => {
  const out: string[] = [];
  for (const y of yearOptions.value) {
    out.push(`${y}-S1`);
    out.push(`${y}-S2`);
  }
  return out;
});

/* ---------------- parse "YYYY-S1" into {year, term} ---------------- */
function parseYearTerm(value: string): { year?: number; term?: string } {
  const v = String(value ?? "").trim();
  if (!v) return {};

  const parts = v.split("-");
  if (parts.length < 2) return {};

  const y = Number(parts[0]);
  const t = parts.slice(1).join("-").trim();

  if (!Number.isFinite(y) || !t) return {};
  return { year: y, term: t };
}

/* ---------------- fetch (server-side filtering + paging) ---------------- */
async function loadGrades(opts?: { page?: number; pageSize?: number }) {
  const seq = ++requestSeq;
  loading.value = true;
  errorMessage.value = null;

  const p = opts?.page ?? page.value;
  const ps = opts?.pageSize ?? pageSize.value;

  try {
    const { year, term } = parseYearTerm(termFilter.value);

    const params: StudentGradesFilterDTO = {
      page: p,
      page_size: ps,
      term: termFilter.value,
    };

    const wrapped = (await student.student.getMyGrades(params)) as any;

    const res = ((wrapped as any)?.data ?? wrapped) as StudentGradePagedDTO;

    if (seq !== requestSeq) return;

    items.value = Array.isArray((res as any)?.items) ? (res as any).items : [];
    total.value = Number((res as any)?.total ?? 0) || 0;

    page.value = Number((res as any)?.page ?? p ?? 1) || 1;
    pageSize.value = Number((res as any)?.page_size ?? ps ?? 10) || 10;
    pages.value = Number((res as any)?.pages ?? 1) || 1;
  } catch (err: any) {
    if (seq !== requestSeq) return;

    errorMessage.value = extractErrorMessage(err);
    items.value = [];
    total.value = 0;
    pages.value = 1;
  } finally {
    if (seq === requestSeq) loading.value = false;
  }
}

onMounted(() => loadGrades());
onBeforeUnmount(() => {
  requestSeq++;
});

/* ---------------- grouping ---------------- */
const currentYearFromFilter = computed(
  () => parseYearTerm(termFilter.value).year
);

const groupedByTerm = computed(() => {
  const y = currentYearFromFilter.value;

  const map = new Map<string, GradeRowVM[]>();
  for (const r of rows.value) {
    const base = r.term || "—";
    const key = y ? `${y}-${base}` : base;

    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(r);
  }

  return [...map.entries()].sort((a, b) => {
    if (a[0] === "—") return 1;
    if (b[0] === "—") return -1;
    return a[0].localeCompare(b[0]);
  });
});

/* ---------------- overview stats ---------------- */
const pageCount = computed(() => items.value.length);
const hasFilter = computed(() => !!termFilter.value);

const summaryText = computed(() => {
  if (hasFilter.value)
    return `Showing ${pageCount.value} of ${total.value} matching records`;
  return `Showing ${pageCount.value} of ${total.value} total records`;
});

const distinctSubjects = computed(
  () => new Set(rows.value.map((g) => g.subjectLabel)).size
);

const averageScore = computed(() => {
  const nums = rows.value
    .map((g) => g.score)
    .filter((n): n is number => typeof n === "number");
  if (!nums.length) return null;

  const a = nums.reduce((x, y) => x + y, 0) / nums.length;
  return Math.round(a * 10) / 10;
});

const bestScore = computed(() => {
  const nums = rows.value
    .map((g) => g.score)
    .filter((n): n is number => typeof n === "number");
  if (!nums.length) return null;

  return Math.max(...nums);
});

const { headerState } = useHeaderState({
  items: [
    {
      key: "total",
      getValue: () => total.value,
      singular: "record",
      plural: "records",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "subjects",
      getValue: () => distinctSubjects.value,
      singular: "subject",
      plural: "subjects",
      suffix: "on page",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
    {
      key: "avg_score",
      getValue: () => averageScore.value ?? 0,
      label: (v: number) =>
        averageScore.value === null ? undefined : `Average: ${v}`,
      variant: "secondary",
      dotClass: "bg-blue-500",
      hideWhenZero: averageScore.value === null,
    },
  ],
});

/* ---------------- handlers ---------------- */
async function handleRefresh() {
  if (loading.value) return;
  await loadGrades({ page: 1, pageSize: pageSize.value });
}

function clearFilter() {
  termFilter.value = "";
}

async function onPageChange(p: number) {
  await loadGrades({ page: p, pageSize: pageSize.value });
}

async function onSizeChange(ps: number) {
  prefs.setTablePageSize(ps);
  pageSize.value = prefs.getTablePageSize();
  await loadGrades({ page: 1, pageSize: pageSize.value });
}

/* Server filter refetch */
watch(termFilter, async () => {
  if (loading.value) return;
  await loadGrades({ page: 1, pageSize: pageSize.value });
});

/* Keep page size synced with preferences store */
watch(
  () => prefs.tablePageSize,
  async () => {
    const next = prefs.getTablePageSize();
    if (pageSize.value === next) return;

    pageSize.value = next;
    await loadGrades({ page: 1, pageSize: pageSize.value });
  }
);
</script>

<template>
  <div class="p-4 space-y-4 max-w-6xl mx-auto pb-10" v-loading="loading">
    <OverviewHeader
      title="My Grades"
      description="View your grades across subjects and terms."
      :loading="loading"
      :showRefresh="true"
      :stats="headerState"
      @refresh="handleRefresh"
    />

    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="mb-2 rounded-xl border border-red-200/60 shadow-sm"
        @close="errorMessage = null"
      />
    </transition>

    <!-- Top summary cards -->
    <el-row :gutter="12" class="items-stretch">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card
          shadow="hover"
          class="rounded-2xl border"
          style="border-color: var(--border-color)"
        >
          <div class="text-xs font-medium" style="color: var(--muted-color)">
            Average score (this page)
          </div>
          <div class="mt-1 text-2xl font-bold" style="color: var(--text-color)">
            {{ averageScore ?? "—" }}
          </div>
          <el-progress
            class="mt-2 app-progress"
            :percentage="clampPct(averageScore)"
            :stroke-width="10"
            :show-text="false"
            :style="progressVars(averageScore, 'primary')"
          />
          <div class="mt-2 text-xs" style="color: var(--muted-color)">
            {{ summaryText }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card
          shadow="hover"
          class="rounded-2xl border"
          style="border-color: var(--border-color)"
        >
          <div class="text-xs font-medium" style="color: var(--muted-color)">
            Best score (this page)
          </div>
          <div class="mt-1 text-2xl font-bold" style="color: var(--text-color)">
            {{ bestScore ?? "—" }}
          </div>
          <el-progress
            class="mt-2 app-progress"
            :percentage="clampPct(bestScore)"
            :stroke-width="10"
            :show-text="false"
            :style="progressVars(bestScore, 'primary')"
          />
          <div class="mt-2 text-xs" style="color: var(--muted-color)">
            Page subjects: {{ distinctSubjects }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card
          shadow="hover"
          class="rounded-2xl border"
          style="border-color: var(--border-color)"
        >
          <div class="text-xs font-medium" style="color: var(--muted-color)">
            Pagination
          </div>
          <div
            class="mt-1 text-base font-semibold"
            style="color: var(--text-color)"
          >
            Page {{ page }} / {{ pages }}
          </div>
          <div class="mt-2 text-xs" style="color: var(--muted-color)">
            Total records:
            <span class="font-medium" style="color: var(--text-color)">{{
              total
            }}</span>
          </div>
          <div class="mt-2 text-xs" style="color: var(--muted-color)">
            Page size:
            <span class="font-medium" style="color: var(--text-color)">{{
              pageSize
            }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card
      shadow="never"
      class="rounded-2xl border"
      style="border-color: var(--border-color)"
    >
      <el-row :gutter="12" class="items-end">
        <el-col :xs="24" :sm="12">
          <div class="font-semibold" style="color: var(--text-color)">
            Filter by term
          </div>
          <div class="text-xs mt-1" style="color: var(--muted-color)">
            <span class="font-medium" style="color: var(--text-color)">{{
              summaryText
            }}</span>
            <span style="color: var(--muted-color)"> (this page)</span>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12">
          <div class="flex items-center justify-end gap-2 flex-wrap">
            <el-select
              v-model="termFilter"
              placeholder="All terms"
              clearable
              class="w-60"
              :disabled="loading"
            >
              <el-option
                v-for="t in termOptions"
                :key="t"
                :label="t"
                :value="t"
              />
            </el-select>

            <el-button :disabled="loading || !termFilter" @click="clearFilter">
              Clear
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Skeleton -->
    <el-card
      v-if="loading && !rows.length"
      shadow="never"
      class="rounded-2xl border"
      style="border-color: var(--border-color)"
    >
      <el-skeleton animated :rows="7" />
    </el-card>

    <!-- Empty -->
    <el-empty
      v-else-if="!loading && !rows.length"
      description="No grades found."
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    />

    <!-- Grouped -->
    <div v-else class="space-y-3">
      <el-card
        v-for="[termKey, list] in groupedByTerm"
        :key="termKey"
        shadow="hover"
        class="rounded-2xl border"
        style="border-color: var(--border-color)"
      >
        <template #header>
          <el-row :gutter="12" class="items-start">
            <el-col :xs="24" :sm="16">
              <div
                class="font-semibold truncate"
                style="color: var(--text-color)"
              >
                {{ termKey === "—" ? "Other" : termKey }}
              </div>
              <div class="text-xs mt-1" style="color: var(--muted-color)">
                {{ list.length }} record{{ list.length === 1 ? "" : "s" }} •
                Avg:
                <span class="font-medium" style="color: var(--text-color)">{{
                  avgScore(list) ?? "—"
                }}</span>
              </div>
            </el-col>

            <el-col :xs="24" :sm="8">
              <div class="flex sm:justify-end">
                <div class="w-full sm:w-56">
                  <div class="text-xs mb-1" style="color: var(--muted-color)">
                    Avg progress
                  </div>
                  <el-progress
                    class="app-progress"
                    :percentage="clampPct(avgScore(list))"
                    :stroke-width="10"
                    :show-text="false"
                    :style="progressVars(avgScore(list), 'primary')"
                  />
                </div>
              </div>
            </el-col>
          </el-row>
        </template>

        <el-table
          :data="list"
          size="small"
          style="width: 100%"
          highlight-current-row
          class="rounded-xl overflow-hidden"
        >
          <!-- Subject -->
          <el-table-column
            label="Subject"
            min-width="260"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div class="flex items-center gap-2 min-w-0">
                <el-tag
                  size="small"
                  effect="plain"
                  :type="tagTypeByGradeType(row.type)"
                >
                  {{ formatType(row.type) }}
                </el-tag>

                <div class="min-w-0">
                  <div
                    class="font-medium truncate"
                    style="color: var(--text-color)"
                  >
                    {{ row.subjectLabel }}
                  </div>
                  <div
                    class="text-xs truncate"
                    style="color: var(--muted-color)"
                  >
                    Class: {{ row.className }}
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>

          <!-- Score -->
          <el-table-column label="Score" min-width="220">
            <template #default="{ row }">
              <div class="flex items-center gap-3">
                <div class="w-[160px] max-w-full">
                  <el-progress
                    class="app-progress"
                    :percentage="clampPct(row.score)"
                    :stroke-width="10"
                    :show-text="false"
                    :style="progressVars(row.score, 'semantic')"
                  />
                </div>
                <div
                  class="text-sm font-semibold"
                  style="color: var(--text-color)"
                >
                  {{ row.score ?? "—" }}
                </div>
              </div>
            </template>
          </el-table-column>

          <!-- Recorded -->
          <el-table-column label="Recorded" min-width="180">
            <template #default="{ row }">
              <div class="text-xs" style="color: var(--muted-color)">
                {{ row.createdAtRaw ? formatDate(row.createdAtRaw) : "—" }}
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- Pagination -->
      <el-card
        shadow="never"
        class="rounded-2xl border"
        style="border-color: var(--border-color)"
      >
        <el-row :gutter="12" class="items-center">
          <el-col :xs="24" :sm="10">
            <div class="text-xs" style="color: var(--muted-color)">
              Total:
              <span class="font-medium" style="color: var(--text-color)">{{
                total
              }}</span>
              • Page:
              <span class="font-medium" style="color: var(--text-color)">{{
                page
              }}</span>
              / {{ pages }}
            </div>
          </el-col>

          <el-col :xs="24" :sm="14">
            <div class="flex justify-end overflow-x-auto">
              <el-pagination
                background
                layout="prev, pager, next, sizes, total"
                :current-page="page"
                :page-size="pageSize"
                :page-sizes="prefs.getAllowedPageSizes()"
                :total="total"
                @current-change="onPageChange"
                @size-change="onSizeChange"
              />
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
:deep(.el-card) {
  border-radius: 16px;
}

/* Progress: use CSS vars from :style="progressVars(...)" */
:deep(.app-progress .el-progress-bar__outer) {
  background: var(--ptrack) !important;
}
:deep(.app-progress .el-progress-bar__inner) {
  background: var(--pbar) !important;
}
</style>
