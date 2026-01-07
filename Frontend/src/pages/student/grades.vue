<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, onMounted, computed, onBeforeUnmount } from "vue";

import { studentService } from "~/api/student";
import type { GradeDTO } from "~/api/types/school.dto";
import type { StudentGradeListDTO } from "~/api/student/student.dto";

import { useHeaderState } from "~/composables/ui/useHeaderState";
import { formatDate } from "~/utils/date/formatDate";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";

const student = studentService();

type StudentGradeItem = StudentGradeListDTO["items"][number] | GradeDTO;

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const grades = ref<StudentGradeItem[]>([]);
const termFilter = ref<string>(""); // "" = all

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

const getTagType = (value?: string) => {
  if (!value) return "info";
  const v = value.toLowerCase();
  if (v === "assignment") return "success";
  if (v === "exam") return "danger";
  if (v === "quiz") return "warning";
  return "info";
};

const formatType = (value?: string) => {
  if (!value) return "—";
  return value.charAt(0).toUpperCase() + value.slice(1);
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

/* ---------------- load grades ---------------- */

const loadGrades = async () => {
  const seq = ++requestSeq;
  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await student.student.getMyGrades();
    if (seq !== requestSeq) return;

    grades.value = res.items ?? [];
  } catch (err: any) {
    if (seq !== requestSeq) return;

    errorMessage.value = extractErrorMessage(err);
    grades.value = [];
  } finally {
    if (seq === requestSeq) loading.value = false;
  }
};

onMounted(loadGrades);
onBeforeUnmount(() => {
  requestSeq++;
});

/* ---------------- view model ---------------- */

type GradeRowVM = {
  id: string;
  subjectLabel: string;
  className: string;
  score: number | null;
  type: string;
  term: string;
  createdAt: string; // raw for formatDate
  createdAtDate: Date | null;
};

const rows = computed<GradeRowVM[]>(() => {
  const list = grades.value ?? [];
  return list
    .map((g: any, idx) => {
      const createdAt = g.created_at ?? g.createdAt ?? "";
      return {
        id: String(g._id ?? g.id ?? `${idx}`),
        subjectLabel: safeText(g.subject_label ?? g.subjectLabel),
        className: safeText(g.class_name ?? g.className),
        score: toNumber(g.score),
        type: safeText(g.type, ""),
        term: safeText(g.term, "—"),
        createdAt: g.lifecycle?.created_at ?? g.created_at ?? g.createdAt ?? "",
        createdAtDate: parseDate(
          g.lifecycle?.created_at ?? g.created_at ?? g.createdAt
        ),
      };
    })
    .sort((a, b) => {
      // newest first
      const ad = a.createdAtDate?.getTime() ?? 0;
      const bd = b.createdAtDate?.getTime() ?? 0;
      return bd - ad;
    });
});

const termOptions = computed(() => {
  const set = new Set<string>();
  for (const r of rows.value) {
    if (r.term && r.term !== "—") set.add(r.term);
  }
  return Array.from(set).sort();
});

const filteredRows = computed(() => {
  if (!termFilter.value) return rows.value;
  return rows.value.filter((r) => r.term === termFilter.value);
});

const groupedByTerm = computed(() => {
  const map = new Map<string, GradeRowVM[]>();
  for (const r of filteredRows.value) {
    const key = r.term || "—";
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(r);
  }

  // sort terms: put "—" last, others alphabetically
  return [...map.entries()].sort((a, b) => {
    if (a[0] === "—") return 1;
    if (b[0] === "—") return -1;
    return a[0].localeCompare(b[0]);
  });
});

/* ---------------- overview stats ---------------- */

const totalGrades = computed(() => filteredRows.value.length);

const distinctSubjects = computed(() => {
  return new Set(filteredRows.value.map((g) => g.subjectLabel)).size;
});

const averageScore = computed(() => {
  const numeric = filteredRows.value
    .map((g) => g.score)
    .filter((n): n is number => typeof n === "number");

  if (!numeric.length) return null;

  const sum = numeric.reduce((acc, n) => acc + n, 0);
  return Math.round((sum / numeric.length) * 10) / 10;
});

const { headerState } = useHeaderState({
  items: [
    {
      key: "total",
      getValue: () => totalGrades.value,
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
      suffix: "graded",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
    {
      key: "avg_score",
      getValue: () => averageScore.value ?? 0,
      label: (v) =>
        averageScore.value === null ? undefined : `Average score: ${v}`,
      variant: "secondary",
      dotClass: "bg-blue-500",
      hideWhenZero: averageScore.value === null,
    },
  ],
});

const handleRefresh = async () => {
  if (loading.value) return;
  await loadGrades();
};

const clearFilter = () => {
  termFilter.value = "";
};
</script>
<template>
  <div class="p-4 space-y-4" v-loading="loading">
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

    <!-- Filters (simple, consistent) -->
    <el-card shadow="never" class="rounded-xl">
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
      >
        <div>
          <div class="font-semibold text-gray-800">Term</div>
          <div class="text-xs text-gray-500">
            Showing
            <span class="font-medium text-gray-700">{{
              filteredRows.length
            }}</span>
            of
            <span class="font-medium text-gray-700">{{ rows.length }}</span>
            records
          </div>
        </div>

        <div class="flex items-center gap-2">
          <el-select
            v-model="termFilter"
            placeholder="All terms"
            clearable
            class="w-56"
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
      </div>
    </el-card>

    <!-- Skeleton for first load -->
    <el-card v-if="loading && !rows.length" shadow="never" class="rounded-xl">
      <el-skeleton animated :rows="6" />
    </el-card>

    <!-- Empty -->
    <el-empty
      v-else-if="!loading && !filteredRows.length"
      description="No grades found."
      class="bg-white rounded-xl border"
    />

    <!-- Grouped by term -->
    <div v-else class="space-y-3">
      <el-card
        v-for="[term, items] in groupedByTerm"
        :key="term"
        shadow="hover"
        class="rounded-xl"
      >
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex flex-col">
              <span class="font-semibold">{{
                term === "—" ? "Other" : term
              }}</span>
              <span class="text-xs text-gray-500">
                {{ items.length }} record{{ items.length === 1 ? "" : "s" }}
              </span>
            </div>

            <!-- tiny summary (simple, not complex) -->
            <div class="text-xs text-gray-500">
              Avg:
              <span class="font-medium text-gray-700">
                {{
                  (() => {
                    const nums = items
                      .map((i) => i.score)
                      .filter((n): n is number => typeof n === "number");
                    if (!nums.length) return "—";
                    const avg = nums.reduce((a, b) => a + b, 0) / nums.length;
                    return Math.round(avg * 10) / 10;
                  })()
                }}
              </span>
            </div>
          </div>
        </template>

        <el-table
          :data="items"
          border
          size="small"
          style="width: 100%"
          highlight-current-row
          :header-cell-style="{
            background: '#f9fafb',
            color: '#374151',
            fontWeight: '600',
            fontSize: '13px',
          }"
        >
          <el-table-column
            prop="subjectLabel"
            label="Subject"
            min-width="220"
            show-overflow-tooltip
          />
          <el-table-column
            prop="className"
            label="Class"
            min-width="180"
            show-overflow-tooltip
          />

          <el-table-column label="Score" min-width="90" align="right">
            <template #default="{ row }">
              <span class="font-medium">{{ row.score ?? "—" }}</span>
            </template>
          </el-table-column>

          <el-table-column label="Type" min-width="130">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" :type="getTagType(row.type)">
                {{ formatType(row.type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="Recorded" min-width="160">
            <template #default="{ row }">
              <span class="text-xs text-gray-600">
                {{
                  formatDate(row.lifecycle?.createdAt ?? row.createdAt ?? "—")
                }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>
