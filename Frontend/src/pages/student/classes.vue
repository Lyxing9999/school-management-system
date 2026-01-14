<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from "vue";

import { studentService } from "~/api/student";
import type { StudentClassSectionDTO } from "~/api/student/student.dto";
import { formatDate } from "~/utils/date/formatDate";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import { useHeaderState } from "~/composables/ui/useHeaderState";
import BaseButton from "~/components/base/BaseButton.vue";

const student = studentService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const classes = ref<StudentClassSectionDTO[]>([]);
let requestSeq = 0;
definePageMeta({ layout: "default" });
/* ---------------- helpers ---------------- */

const safeText = (v: any, fallback = "—") => {
  const s = String(v ?? "").trim();
  return s ? s : fallback;
};

const extractErrorMessage = (err: any) => {
  return (
    err?.response?.data?.message ||
    err?.message ||
    "Failed to load classes. Please try again."
  );
};

const statusTagType = (s?: string | null) => {
  if (s === "active") return "success";
  if (s === "inactive") return "info";
  if (s === "archived") return "warning";
  return "info";
};

const statusLabel = (s?: string | null) => {
  const v = safeText(s, "—");
  return v === "—" ? v : v.charAt(0).toUpperCase() + v.slice(1);
};

/* ---------------- load classes ---------------- */

const loadClasses = async () => {
  const seq = ++requestSeq;
  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await student.student.getMyClasses({ showError: false });
    if (seq !== requestSeq) return;

    // backend returns: { success, message, data: { items: [...] } }
    const payload = (res as any)?.data ?? res;
    classes.value = (payload?.items ?? []) as StudentClassSectionDTO[];
  } catch (err: any) {
    if (seq !== requestSeq) return;

    errorMessage.value = extractErrorMessage(err);
    classes.value = [];
  } finally {
    if (seq === requestSeq) loading.value = false;
  }
};

onMounted(loadClasses);
onBeforeUnmount(() => {
  requestSeq++;
});

/* ---------------- view model ---------------- */

type ClassRow = {
  id: string;
  name: string;
  teacherName: string;
  status: string;

  subjectLabels: string[];
  subjectCount: number;

  studentCount: number;
  maxStudents: number | null;

  createdAtRaw: string | null;
  updatedAtRaw: string | null;
};

const rows = computed<ClassRow[]>(() => {
  return (classes.value ?? []).map((c: any, idx) => {
    const subjectLabels: string[] = Array.isArray(c.subject_labels)
      ? c.subject_labels
      : Array.isArray(c.subjectLabels)
      ? c.subjectLabels
      : [];

    const subjectCount =
      Number(
        c.subject_count ??
          c.subjectCount ??
          (Array.isArray(c.subject_ids) ? c.subject_ids.length : 0) ??
          (Array.isArray(c.subjectIds) ? c.subjectIds.length : 0)
      ) || 0;

    const studentCount =
      Number(
        c.student_count ??
          c.studentCount ??
          c.enrolled_count ??
          c.enrolledCount ??
          0
      ) || 0;

    const maxStudents =
      c.max_students === null || c.max_students === undefined
        ? c.maxStudents ?? null
        : Number(c.max_students);

    const teacherName =
      c.homeroom_teacher_name ??
      c.homeroomTeacherName ??
      c.teacher_name ??
      c.teacherName ??
      "—";

    return {
      id: String(c.id ?? c._id ?? `${idx}`),
      name: safeText(c.name, "—"),
      teacherName: safeText(teacherName, "—"),
      status: safeText(c.status, "—"),

      subjectLabels,
      subjectCount,

      studentCount,
      maxStudents: Number.isFinite(maxStudents) ? maxStudents : null,

      createdAtRaw:
        c.lifecycle?.created_at ??
        c.lifecycle?.createdAt ??
        c.created_at ??
        c.createdAt ??
        null,
      updatedAtRaw:
        c.lifecycle?.updated_at ??
        c.lifecycle?.updatedAt ??
        c.updated_at ??
        c.updatedAt ??
        null,
    };
  });
});

const onlyClass = computed(() =>
  rows.value.length === 1 ? rows.value[0] : null
);

const capacityPercent = computed(() => {
  const c = onlyClass.value;
  if (!c) return 0;
  if (!c.maxStudents) return 0;
  if (c.maxStudents <= 0) return 0;
  return Math.min(100, Math.round((c.studentCount / c.maxStudents) * 100));
});

/* ---------------- overview stats ---------------- */

const totalClasses = computed(() => rows.value.length);
const totalSubjects = computed(() =>
  rows.value.reduce((sum, r) => sum + r.subjectCount, 0)
);

const { headerState } = useHeaderState({
  items: [
    {
      key: "classes",
      getValue: () => totalClasses.value,
      singular: "class",
      plural: "classes",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "subjects",
      getValue: () => totalSubjects.value,
      singular: "subject",
      plural: "subjects",
      suffix: "in total",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
  ],
});

const headerDescription = computed(() => {
  const count = totalClasses.value;
  if (!count) return "You are not enrolled in any classes yet.";
  if (count === 1) return "You are enrolled in 1 class.";
  return `You are enrolled in ${count} classes.`;
});

const handleRefresh = async () => {
  if (loading.value) return;
  await loadClasses();
};
</script>

<template>
  <div class="p-4 space-y-5 max-w-6xl mx-auto pb-10" v-loading="loading">
    <OverviewHeader
      title="My Classes"
      :description="headerDescription"
      :loading="loading"
      :showRefresh="true"
      :stats="headerState"
      @refresh="handleRefresh"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="handleRefresh">
          Refresh
        </BaseButton>
      </template>

      <template #filters>
        <div class="text-xs" style="color: var(--muted-color)">
          This page shows the class you are enrolled in (view-only).
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

    <!-- Skeleton -->
    <el-card v-if="loading && !rows.length" shadow="never" class="rounded-2xl">
      <el-skeleton animated :rows="7" />
    </el-card>

    <!-- Empty -->
    <el-empty
      v-else-if="!loading && !rows.length"
      description="You are not enrolled in any classes yet."
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    />

    <!-- Single class (beauty view) -->
    <el-card
      v-else-if="onlyClass"
      shadow="hover"
      class="class-card rounded-2xl border"
      :body-style="{ padding: '18px' }"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    >
      <template #header>
        <div class="class-card__header">
          <div class="min-w-0">
            <div
              class="text-base font-semibold truncate"
              style="color: var(--text-color)"
            >
              {{ onlyClass.name }}
            </div>
            <div class="text-xs mt-1" style="color: var(--muted-color)">
              Teacher:
              <span class="font-medium" style="color: var(--text-color)">{{
                onlyClass.teacherName
              }}</span>
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <el-tag
              size="small"
              effect="plain"
              :type="statusTagType(onlyClass.status)"
            >
              {{ statusLabel(onlyClass.status) }}
            </el-tag>

            <el-tag size="small" effect="plain" type="info">
              {{ onlyClass.studentCount }} /
              {{ onlyClass.maxStudents ?? "∞" }} students
            </el-tag>
          </div>
        </div>
      </template>

      <!-- capacity progress -->
      <div
        class="rounded-xl border px-4 py-3 mb-4"
        style="
          background: color-mix(in srgb, var(--color-card) 90%, transparent);
          border-color: var(--border-color);
        "
      >
        <div class="flex items-center justify-between">
          <div class="text-xs font-medium" style="color: var(--text-color)">
            Class capacity
          </div>
          <div class="text-xs" style="color: var(--muted-color)">
            {{
              onlyClass.maxStudents ? `${capacityPercent}% full` : "Unlimited"
            }}
          </div>
        </div>

        <el-progress
          v-if="onlyClass.maxStudents"
          :percentage="capacityPercent"
          :stroke-width="10"
          :show-text="false"
          class="mt-2"
        />
        <div v-else class="text-xs mt-2" style="color: var(--muted-color)">
          No maximum student limit set.
        </div>
      </div>

      <!-- meta tiles -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="meta-tile">
          <div class="meta-tile__label">Subjects</div>
          <div class="meta-tile__value">{{ onlyClass.subjectCount }}</div>
          <div class="meta-tile__hint">Assigned to this class</div>
        </div>

        <div class="meta-tile">
          <div class="meta-tile__label">Created</div>
          <div class="meta-tile__value meta-tile__value--small">
            {{
              onlyClass.createdAtRaw ? formatDate(onlyClass.createdAtRaw) : "—"
            }}
          </div>
          <div class="meta-tile__hint">First time you joined</div>
        </div>

        <div class="meta-tile">
          <div class="meta-tile__label">Updated</div>
          <div class="meta-tile__value meta-tile__value--small">
            {{
              onlyClass.updatedAtRaw ? formatDate(onlyClass.updatedAtRaw) : "—"
            }}
          </div>
          <div class="meta-tile__hint">Latest changes</div>
        </div>
      </div>

      <el-divider class="!my-4" />

      <!-- subjects -->
      <div>
        <div class="flex items-center justify-between">
          <div class="text-sm font-semibold" style="color: var(--text-color)">
            Subjects
          </div>
          <div class="text-xs" style="color: var(--muted-color)">
            {{ onlyClass.subjectLabels.length }} item{{
              onlyClass.subjectLabels.length === 1 ? "" : "s"
            }}
          </div>
        </div>

        <div class="mt-2 flex flex-wrap gap-2">
          <el-tag
            v-for="label in onlyClass.subjectLabels"
            :key="label"
            size="small"
            effect="plain"
            :type="label.includes('[deleted') ? 'warning' : 'info'"
            class="subject-pill"
          >
            {{ label }}
          </el-tag>

          <span
            v-if="!onlyClass.subjectLabels.length"
            class="text-xs"
            style="color: var(--muted-color)"
          >
            No subjects assigned yet.
          </span>
        </div>
      </div>
    </el-card>

    <!-- Multiple classes fallback -->
    <el-card v-else shadow="hover" class="rounded-2xl border">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="font-semibold" style="color: var(--text-color)">
            Classes
          </div>
          <div class="text-xs" style="color: var(--muted-color)">
            {{ totalClasses }} class{{ totalClasses === 1 ? "" : "es" }}
          </div>
        </div>
      </template>

      <el-table
        :data="rows"
        border
        size="small"
        style="width: 100%"
        highlight-current-row
      >
        <el-table-column
          prop="name"
          label="Class"
          min-width="220"
          show-overflow-tooltip
        />
        <el-table-column
          prop="teacherName"
          label="Teacher"
          min-width="170"
          show-overflow-tooltip
        />

        <el-table-column label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="plain"
              :type="statusTagType(row.status)"
            >
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Subjects" min-width="320">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-tag
                v-for="label in row.subjectLabels"
                :key="label"
                size="small"
                type="info"
                effect="plain"
              >
                {{ label }}
              </el-tag>
              <span
                v-if="!row.subjectLabels.length"
                class="text-xs"
                style="color: var(--muted-color)"
              >
                No subjects assigned
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Students" min-width="150" align="center">
          <template #default="{ row }">
            {{ row.studentCount }} / {{ row.maxStudents ?? "∞" }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
:deep(.el-card) {
  border-radius: 16px;
}

.class-card {
  position: relative;
  overflow: hidden;
}

.class-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(
    90deg,
    var(--color-primary),
    color-mix(in srgb, var(--color-primary) 35%, transparent)
  );
}

.class-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.meta-tile {
  border-radius: 14px;
  border: 1px solid var(--border-color);
  padding: 14px;
  background: color-mix(in srgb, var(--color-card) 92%, transparent);
}

.meta-tile__label {
  font-size: 12px;
  color: var(--muted-color);
}

.meta-tile__value {
  margin-top: 4px;
  font-size: 22px;
  font-weight: 650;
  color: var(--text-color);
}

.meta-tile__value--small {
  font-size: 14px;
  font-weight: 600;
}

.meta-tile__hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--muted-color);
}

.subject-pill {
  border-radius: 999px;
}
</style>
