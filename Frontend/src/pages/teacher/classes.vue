<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";

import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";

const teacher = teacherService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);

/**
 * Backend shape you already return:
 * - is_homeroom
 * - homeroom_teacher_name
 * - subject_labels            (all subjects in class)
 * - assigned_subject_labels   (subjects THIS teacher teaches in that class)
 */
type TeacherClassEnriched = ClassSectionDTO & {
  enrolled_count?: number;
  subject_count?: number;

  is_homeroom?: boolean;
  homeroom_teacher_id?: string;
  homeroom_teacher_name?: string;

  subject_labels?: string[];
  assigned_subject_labels?: string[];

  max_students?: number;
};

type DisplayClassRow = TeacherClassEnriched & {
  studentCount: number;
  subjectCount: number;

  roleLabel: "Homeroom" | "Subject Teacher";
  roleType: "success" | "warning";

  homeroomDisplay: string;

  mySubjects: string[];
  classSubjects: string[];
};

const classes = ref<TeacherClassEnriched[]>([]);

/* ---------- sorting ---------- */
const sortedClasses = computed(() => {
  const items = [...classes.value];
  items.sort((a, b) => {
    const ah = Boolean(a.is_homeroom);
    const bh = Boolean(b.is_homeroom);
    if (ah !== bh) return ah ? -1 : 1;

    return String(a.name || "").localeCompare(String(b.name || ""), undefined, {
      sensitivity: "base",
    });
  });
  return items;
});

/* ---------- display mapping ---------- */
const displayClasses = computed<DisplayClassRow[]>(() =>
  sortedClasses.value.map((c) => {
    const studentCount = c.enrolled_count ?? 0;

    const subjectCount =
      c.subject_count ??
      (Array.isArray((c as any).subject_ids)
        ? ((c as any).subject_ids as any[]).length
        : 0);

    const isHomeroom = Boolean(c.is_homeroom);

    const mySubjects = (c.assigned_subject_labels ?? []).filter(Boolean);
    const classSubjects = (c.subject_labels ?? []).filter(Boolean);

    const roleLabel = isHomeroom ? "Homeroom" : "Subject Teacher";
    const roleType: "success" | "warning" = isHomeroom ? "success" : "warning";

    const homeroomDisplay = isHomeroom ? "Me" : c.homeroom_teacher_name || "—";

    return {
      ...c,
      studentCount,
      subjectCount,
      roleLabel,
      roleType,
      homeroomDisplay,
      mySubjects,
      classSubjects,
    };
  })
);

/* ---------- stats ---------- */
const totalClasses = computed(() => displayClasses.value.length);

const totalStudents = computed(() =>
  displayClasses.value.reduce((sum, c) => sum + (c.studentCount ?? 0), 0)
);

const totalMySubjects = computed(() =>
  displayClasses.value.reduce((sum, c) => sum + (c.mySubjects?.length ?? 0), 0)
);

/**
 * Fix for TS "readonly cannot be assigned to mutable array"
 * Make stats a computed with an explicit mutable array type.
 */
type OverviewStatItem = {
  key?: string | number;
  value: number;
  singular?: string;
  plural?: string;
  label?: string;
  suffix?: string;
  prefix?: string;
  variant?: "primary" | "secondary";
  dotClass?: string;
};

const headerStats = computed<OverviewStatItem[]>(() => [
  {
    key: "classes",
    value: totalClasses.value,
    singular: "class",
    plural: "classes",
    variant: "primary",
  },
  {
    key: "students",
    value: totalStudents.value,
    singular: "student",
    plural: "students",
    suffix: "total",
    variant: "secondary",
    dotClass: "bg-emerald-500",
  },
  {
    key: "mySubjects",
    value: totalMySubjects.value,
    singular: "subject",
    plural: "subjects",
    suffix: "I teach",
    variant: "secondary",
    dotClass: "bg-indigo-500",
  },
]);

/* ---------- api ---------- */
function unwrapItems(res: any): TeacherClassEnriched[] {
  // supports:
  // A) res.data.items (wrap_response)
  // B) res.items
  const items = (res?.data?.items ??
    res?.items ??
    []) as TeacherClassEnriched[];
  return Array.isArray(items) ? items : [];
}

const loadClasses = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const res: any = await teacher.teacher.listMyClasses({ showError: false });

    const items = unwrapItems(res);
    classes.value = items;

    if (!classes.value.length) {
      ElMessage.info("You don't have any classes yet.");
    }
  } catch (err: any) {
    const msg = err?.message ?? "Failed to load classes.";
    errorMessage.value = msg;
    ElMessage.error(msg);
    classes.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(loadClasses);
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="My Classes"
      description="Classes you are involved in as homeroom or as a subject-teacher. ‘My Subjects’ always comes from teaching assignments."
      :stats="headerStats"
      :loading="loading"
      :show-refresh="true"
      :show-reset="false"
      :show-search="false"
      @refresh="loadClasses"
    />

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

    <TableCard
      title="Class list"
      description="Homeroom is an admin role. Teaching comes only from assigned_subject_labels."
      :rightText="`Showing ${displayClasses.length} / ${totalClasses} classes`"
    >
      <el-table
        :data="displayClasses"
        v-loading="loading"
        highlight-current-row
        class="rounded-lg overflow-hidden w-full class-table"
        :header-cell-style="{
          background: 'var(--color-card)',
          color: 'var(--text-color)',
          fontWeight: '600',
          fontSize: '13px',
          borderBottom: '1px solid var(--border-color)',
        }"
        :row-style="{ color: 'var(--text-color)' }"
      >
        <!-- Class + Role -->
        <el-table-column label="Class" min-width="260">
          <template #default="{ row }">
            <div class="flex flex-col gap-1 min-w-0">
              <div class="flex items-center gap-2 min-w-0">
                <div
                  class="font-medium truncate"
                  style="color: var(--text-color)"
                >
                  {{ row.name }}
                </div>

                <el-tag size="small" :type="row.roleType" effect="plain">
                  {{ row.roleLabel }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- My teaching subjects -->
        <el-table-column label="My Subjects" min-width="320">
          <template #default="{ row }">
            <div class="flex flex-col gap-1">
              <div class="text-[11px]" style="color: var(--muted-color)">
                Subjects I teach
              </div>

              <div
                v-if="row.mySubjects?.length"
                class="flex flex-wrap gap-1 mt-1"
              >
                <el-tag
                  v-for="label in row.mySubjects"
                  :key="`${row.id}-my-${label}`"
                  size="small"
                  type="info"
                  effect="plain"
                >
                  {{ label }}
                </el-tag>
              </div>

              <div
                v-else
                class="text-[11px] mt-1"
                style="color: var(--muted-color)"
              >
                Not assigned yet.
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Class subjects (homeroom-only overview) -->
        <el-table-column label="Class Subjects" min-width="340">
          <template #default="{ row }">
            <div class="flex flex-col gap-1">
              <div class="flex items-center gap-2">
                <span class="text-[11px]" style="color: var(--muted-color)">
                  Overview
                </span>

                <el-tag
                  v-if="row.is_homeroom"
                  size="small"
                  type="warning"
                  effect="plain"
                >
                  Homeroom
                </el-tag>
                <el-tag v-else size="small" type="info" effect="plain">
                  Hidden
                </el-tag>
              </div>

              <div v-if="row.is_homeroom">
                <div
                  v-if="row.classSubjects?.length"
                  class="flex flex-wrap gap-1 mt-1"
                >
                  <el-tag
                    v-for="label in row.classSubjects"
                    :key="`${row.id}-class-${label}`"
                    size="small"
                    type="warning"
                    effect="plain"
                  >
                    {{ label }}
                  </el-tag>
                </div>

                <div
                  v-else
                  class="text-[11px] mt-1"
                  style="color: var(--muted-color)"
                >
                  No class subjects configured.
                </div>
              </div>

              <div
                v-else
                class="text-[11px] mt-1"
                style="color: var(--muted-color)"
              >
                Only visible for homeroom/admin.
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Summary -->
        <el-table-column label="Summary" min-width="200" align="center">
          <template #default="{ row }">
            <div class="flex flex-col items-center gap-2">
              <div class="flex items-center gap-2 flex-wrap justify-center">
                <el-tag size="small" type="primary" effect="plain">
                  Teach: {{ row.mySubjects?.length ?? 0 }}
                </el-tag>

                <el-tag size="small" type="info" effect="plain">
                  Total: {{ row.subjectCount ?? 0 }}
                </el-tag>

                <el-tag
                  v-if="row.is_homeroom"
                  size="small"
                  type="warning"
                  effect="plain"
                >
                  Class: {{ row.classSubjects?.length ?? 0 }}
                </el-tag>
              </div>

              <el-tag
                v-if="!row.mySubjects?.length"
                size="small"
                type="danger"
                effect="plain"
              >
                No teaching subjects
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <!-- Homeroom teacher -->
        <el-table-column label="Homeroom Teacher" min-width="180">
          <template #default="{ row }">
            <span class="truncate" style="color: var(--muted-color)">
              {{ row.homeroomDisplay }}
            </span>
          </template>
        </el-table-column>

        <!-- Total subjects -->
        <el-table-column label="Total Subjects" min-width="140" align="center">
          <template #default="{ row }">
            <span class="font-medium" style="color: var(--text-color)">
              {{ row.subjectCount }}
            </span>
          </template>
        </el-table-column>

        <!-- Students -->
        <el-table-column label="Students" min-width="220">
          <template #default="{ row }">
            <div class="flex flex-col gap-1">
              <span class="font-medium" style="color: var(--text-color)">
                {{ row.studentCount }} / {{ row.max_students || "∞" }}
              </span>

              <el-progress
                v-if="row.max_students"
                :percentage="
                  row.max_students
                    ? Math.min(
                        100,
                        Math.round((row.studentCount / row.max_students) * 100)
                      )
                    : 0
                "
                :stroke-width="6"
                :show-text="false"
                style="width: 130px"
              />
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && !classes.length" class="py-10">
        <el-empty
          description="You don't have any classes yet"
          :image-size="120"
        >
          <template #extra>
            <p
              class="text-sm max-w-md mx-auto"
              style="color: var(--muted-color)"
            >
              Classes assigned to you will appear here automatically.
            </p>
          </template>
        </el-empty>
      </div>
    </TableCard>
  </div>
</template>

<style scoped>
/* Hover row color */
:deep(.el-table__body tr:hover > td.el-table__cell) {
  background: var(--hover-bg) !important;
}

/* Ensure headers keep theme background */
:deep(.el-table thead th.el-table__cell) {
  background: var(--color-card) !important;
}

/* Critical: allow content to shrink + truncate properly */
:deep(.class-table .cell) {
  min-width: 0;
}
</style>
