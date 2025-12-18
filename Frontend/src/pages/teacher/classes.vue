<!-- ~/pages/teacher/classes/index.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import TableCard from "~/components/Cards/TableCard.vue";
import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";

definePageMeta({ layout: "teacher" });

const teacher = teacherService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);

type TeacherClassEnriched = ClassSectionDTO & {
  enrolled_count?: number;
  subject_count?: number;
  teacher_name?: string;
  subject_labels?: string[];
};

const classes = ref<TeacherClassEnriched[]>([]);

const totalClasses = ref(0);
const totalStudents = ref(0);
const totalSubjects = ref(0);

const displayClasses = computed(() =>
  classes.value.map((c) => ({
    ...c,
    studentCount: c.enrolled_count ?? 0,
    subjectCount:
      c.subject_count ??
      (Array.isArray(c.subject_ids) ? c.subject_ids.length : 0),
  }))
);

const recomputeSummary = () => {
  totalClasses.value = classes.value.length;

  totalStudents.value = classes.value.reduce(
    (sum, c) => sum + (c.enrolled_count ?? 0),
    0
  );

  totalSubjects.value = classes.value.reduce(
    (sum, c) =>
      sum +
      (c.subject_count ??
        (Array.isArray(c.subject_ids) ? c.subject_ids.length : 0)),
    0
  );
};

const loadClasses = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await teacher.teacher.listMyClasses({ showError: false });
    if (!res) {
      errorMessage.value = "Failed to load classes.";
      classes.value = [];
      return;
    }

    classes.value = (res.items ?? []) as TeacherClassEnriched[];
    recomputeSummary();

    if (!classes.value.length) {
      ElMessage.info("You don't have any classes yet.");
    }
  } catch (err: any) {
    const msg = err?.message ?? "Failed to load classes.";
    errorMessage.value = msg;
    ElMessage.error(msg);
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
      description="Overview of every class you are responsible for, with capacity and subject coverage."
      :stats="[
        {
          key: 'classes',
          value: totalClasses,
          singular: 'class',
          plural: 'classes',
          variant: 'primary',
        },
        {
          key: 'students',
          value: totalStudents,
          singular: 'student',
          plural: 'students',
          suffix: 'total',
          variant: 'secondary',
          dotClass: 'bg-emerald-500',
        },
      ]"
      :loading="loading"
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
      description="Click a row to see more details about that class."
      :rightText="`Showing ${displayClasses.length} / ${totalClasses} classes`"
    >
      <el-table
        :data="displayClasses"
        v-loading="loading"
        highlight-current-row
        class="rounded-lg overflow-hidden w-full"
        :header-cell-style="{
          background: 'var(--color-card)',
          color: 'var(--text-color)',
          fontWeight: '600',
          fontSize: '13px',
          borderBottom: '1px solid var(--border-color)',
        }"
        :row-style="{
          color: 'var(--text-color)',
        }"
      >
        <!-- Class info + subject labels -->
        <el-table-column label="Class" min-width="320">
          <template #default="{ row }">
            <div class="flex flex-col gap-1">
              <div class="font-medium" style="color: var(--text-color)">
                {{ row.name }}
              </div>

              <div class="text-[11px]" style="color: var(--muted-color)">
                ID: {{ row.id }}
              </div>

              <div
                v-if="row.subject_labels?.length"
                class="flex flex-wrap gap-1 mt-1"
              >
                <el-tag
                  v-for="label in row.subject_labels"
                  :key="label"
                  size="small"
                  type="info"
                  effect="plain"
                >
                  {{ label }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Teacher -->
        <el-table-column label="Teacher" min-width="160">
          <template #default="{ row }">
            <span style="color: var(--muted-color)">
              {{ row.teacher_name || "Me" }}
            </span>
          </template>
        </el-table-column>

        <!-- Subjects count -->
        <el-table-column label="Subjects" min-width="130">
          <template #default="{ row }">
            <span class="font-medium" style="color: var(--text-color)">
              {{ row.subjectCount }}
            </span>
          </template>
        </el-table-column>

        <!-- Students with capacity -->
        <el-table-column label="Students" min-width="200">
          <template #default="{ row }">
            <div class="flex flex-col gap-1">
              <span class="font-medium" style="color: var(--text-color)">
                {{ row.studentCount }} / {{ row.max_students || "∞" }}
              </span>

              <el-progress
                v-if="row.max_students"
                :percentage="
                  row.max_students
                    ? Math.round((row.studentCount / row.max_students) * 100)
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
/* Make table hover match your theme */
:deep(.el-table__body tr:hover > td.el-table__cell) {
  background: var(--hover-bg) !important;
}

/* Optional: remove Element Plus header “gray” in some themes */
:deep(.el-table thead th.el-table__cell) {
  background: var(--color-card) !important;
}
</style>
