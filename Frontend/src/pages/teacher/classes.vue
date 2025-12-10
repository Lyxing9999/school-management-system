<!-- ~/pages/teacher/classes/index.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import OverviewHeader from "~/components/OverView/OverViewHeader.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";

definePageMeta({
  layout: "teacher",
});

const teacher = teacherService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);

/**
 * Extend DTO with enriched fields from backend:
 *  - student_count
 *  - subject_count
 *  - teacher_name
 *  - subject_labels
 */
type TeacherClassEnriched = ClassSectionDTO & {
  student_count?: number;
  subject_count?: number;
  teacher_name?: string;
  subject_labels?: string[];
};

const classes = ref<TeacherClassEnriched[]>([]);

// summary stats
const totalClasses = ref(0);
const totalStudents = ref(0);
const totalSubjects = ref(0);

// add derived counts for table display (use backend counts first)
const displayClasses = computed(() =>
  classes.value.map((c) => ({
    ...c,
    studentCount:
      c.student_count ??
      (Array.isArray(c.student_ids) ? c.student_ids.length : 0),
    subjectCount:
      c.subject_count ??
      (Array.isArray(c.subject_ids) ? c.subject_ids.length : 0),
  }))
);

const recomputeSummary = () => {
  totalClasses.value = classes.value.length;

  totalStudents.value = classes.value.reduce(
    (sum, c) =>
      sum +
      (c.student_count ??
        (Array.isArray(c.student_ids) ? c.student_ids.length : 0)),
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
    console.error(err);
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
  <div class="p-4 space-y-4">
    <!-- Header (consistent with other teacher pages) -->
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

    <!-- Error -->
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

    <!-- Main table -->
    <el-card
      shadow="never"
      :body-style="{ padding: '20px' }"
      class="rounded-2xl border border-gray-200/60 shadow-sm bg-white"
    >
      <template #header>
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
        >
          <div>
            <div class="text-base font-semibold text-gray-800">Class list</div>
            <p class="text-xs text-gray-500">
              Click a row to see more details about that class.
            </p>
          </div>
        </div>
      </template>

      <el-table
        :data="displayClasses"
        v-loading="loading"
        style="width: 100%"
        highlight-current-row
        class="rounded-lg overflow-hidden"
        :header-cell-style="{
          background: '#f9fafb',
          color: '#374151',
          fontWeight: '600',
          fontSize: '13px',
        }"
      >
        <!-- Class info + subject labels -->
        <el-table-column label="Class" min-width="320">
          <template #default="{ row }">
            <div class="flex flex-col gap-1">
              <div class="font-medium text-gray-800">
                {{ row.name }}
              </div>
              <div class="text-[11px] text-gray-400">ID: {{ row.id }}</div>

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
            <span class="text-gray-700">
              {{ row.teacher_name || "Me" }}
            </span>
          </template>
        </el-table-column>

        <!-- Subjects count -->
        <el-table-column label="Subjects" min-width="130">
          <template #default="{ row }">
            <span class="font-medium text-gray-800">
              {{ row.subjectCount }}
            </span>
          </template>
        </el-table-column>

        <!-- Students with capacity -->
        <el-table-column label="Students" min-width="200">
          <template #default="{ row }">
            <div class="flex flex-col gap-1">
              <span class="font-medium text-gray-800">
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
            <p class="text-sm text-gray-500 max-w-md mx-auto">
              Classes assigned to you will appear here automatically.
            </p>
          </template>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<style scoped></style>
