<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { ElMessage } from "element-plus";

import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";
import type { TeacherStudentNameDTO } from "~/api/teacher/dto";


import BaseButton from "~/components/Base/BaseButton.vue";



definePageMeta({
  layout: "teacher",
});

const teacher = teacherService();

// state
const loadingClasses = ref(false);
const loadingStudents = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<ClassSectionDTO[]>([]);
const selectedClassId = ref<string | null>(null);
const students = ref<TeacherStudentNameDTO[]>([]);

// UI helpers
const searchTerm = ref("");

// derived
const selectedClass = computed(
  () => classes.value.find((c) => c.id === selectedClassId.value) ?? null
);

const totalClasses = computed(() => classes.value.length);
const totalStudentsInSelected = computed(
  () => selectedClass.value?.student_ids?.length ?? 0
);

const filteredStudents = computed(() => {
  const term = searchTerm.value.trim().toLowerCase();
  if (!term) return students.value;
  return students.value.filter((s) =>
    (s.username || "").toString().toLowerCase().includes(term)
  );
});

// load teacher classes
const loadClasses = async () => {
  loadingClasses.value = true;
  errorMessage.value = null;

  try {
    const res = await teacher.teacher.listMyClasses({ showError: false });
    classes.value = res.items ?? [];

    if (!selectedClassId.value && classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id;
    }
  } catch (err: any) {
    const msg = err?.message ?? "Failed to load classes.";
    errorMessage.value = msg;
    ElMessage.error(msg);
  } finally {
    loadingClasses.value = false;
  }
};

// load students for selected class
const loadStudentsForClass = async (classId: string | null) => {
  students.value = [];
  if (!classId) return;

  loadingStudents.value = true;
  errorMessage.value = null;

  try {
    const res = await teacher.teacher.listStudentNamesInClass(classId, {
      showError: false,
    });
    students.value = res.items ?? [];
  } catch (err: any) {
    const msg = err?.message ?? "Failed to load students.";
    errorMessage.value = msg;
    ElMessage.error(msg);
  } finally {
    loadingStudents.value = false;
  }
};

// react when class changes
watch(selectedClassId, (newVal) => {
  searchTerm.value = "";
  loadStudentsForClass(newVal);
});

// initial
onMounted(async () => {
  await loadClasses();
  if (selectedClassId.value) {
    await loadStudentsForClass(selectedClassId.value);
  }
});

// handlers
const handleRefresh = async () => {
  await loadClasses();
  if (selectedClassId.value) {
    await loadStudentsForClass(selectedClassId.value);
  }
};
</script>

<template>
  <div class="space-y-4">
    <!-- Page header -->
    <div
      class="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-[var(--color-primary-light-9)] to-[var(--color-primary-light-9)] border border-[color:var(--color-primary-light-9)] shadow-sm rounded-2xl p-5"
    >
      <div>
        <h1
          class="text-2xl font-bold flex items-center gap-2 text-[color:var(--color-dark)]"
        >
          My Students
        </h1>
        <p class="mt-1.5 text-sm text-[color:var(--color-primary-light-1)]">
          Quickly see which students belong to each of your classes.
        </p>

        <div class="flex flex-wrap items-center gap-2 mt-2 text-xs">
          <span
            v-if="totalClasses"
            class="inline-flex items-center gap-1 rounded-full bg-[var(--color-primary-light-8)] text-[color:var(--color-primary)] px-3 py-0.5 border border-[var(--color-primary-light-5)]"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />
            {{ totalClasses }}
            {{ totalClasses === 1 ? "class" : "classes" }}
            assigned
          </span>

          <span
            v-if="selectedClass && totalStudentsInSelected"
            class="inline-flex items-center gap-1 rounded-full bg-white text-gray-700 px-3 py-0.5 border border-gray-200"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            {{ totalStudentsInSelected }}
            {{ totalStudentsInSelected === 1 ? "student" : "students" }}
            in this class
          </span>
        </div>
      </div>

      <BaseButton
        plain
        :loading="loadingClasses || loadingStudents"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="handleRefresh"
      >
        Refresh
      </BaseButton>
    </div>

    <!-- Error -->
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

    <!-- Main card -->
    <el-card
      shadow="never"
      :body-style="{ padding: '20px' }"
      class="border border-gray-200/60 rounded-2xl shadow-sm bg-white"
    >
      <template #header>
        <div class="flex flex-col gap-4">
          <!-- Title row -->
          <div
            class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
          >
            <div class="space-y-1">
              <div class="text-base font-semibold text-gray-800">
                Class overview
              </div>
              <p class="text-sm text-gray-500">
                Choose a class, then optionally search by student name.
              </p>
            </div>
          </div>

          <!-- Filters row -->
          <div class="flex flex-col md:flex-row gap-3">
            <div class="flex flex-col gap-1 flex-1 md:max-w-xs">
              <span class="text-xs font-medium text-gray-600">Class</span>
              <el-select
                v-model="selectedClassId"
                placeholder="Select a class..."
                size="default"
                class="w-full"
                :disabled="!classes.length || loadingClasses"
                clearable
                filterable
              >
                <el-option
                  v-for="c in classes"
                  :key="c.id"
                  :label="c.name"
                  :value="c.id"
                />
              </el-select>
            </div>

            <div class="flex flex-col gap-1 flex-1 md:max-w-sm">
              <span class="text-xs font-medium text-gray-600"
                >Search students</span
              >
              <el-input
                v-model="searchTerm"
                size="default"
                placeholder="Type a student name..."
                clearable
                :disabled="!students.length"
                class="w-full"
                prefix-icon="Search"
              />
            </div>
          </div>

          <!-- Class info -->
          <div
            v-if="selectedClass && students.length"
            class="flex flex-wrap items-center gap-3 text-xs text-gray-600 bg-gray-50 rounded-lg p-2.5 border border-gray-100"
          >
            <div class="flex items-center gap-1.5">
              <span class="font-medium text-gray-700">Class:</span>
              <span>{{ selectedClass.name }}</span>
            </div>
            <div class="h-4 w-px bg-gray-300" />
            <div class="flex items-center gap-1.5">
              <span class="font-medium text-gray-700">Showing:</span>
              <span>
                {{ filteredStudents.length }} / {{ students.length }} students
              </span>
            </div>
          </div>
        </div>
      </template>

      <!-- Table / empty states -->
      <el-table
        v-if="filteredStudents.length || loadingClasses || loadingStudents"
        v-loading="loadingClasses || loadingStudents"
        :data="filteredStudents"
        size="default"
        stripe
        highlight-current-row
        class="rounded-lg overflow-hidden"
        :style="{ width: '100%' }"
        :header-cell-style="{
          background: '#f9fafb',
          color: '#374151',
          fontWeight: '600',
          fontSize: '13px',
        }"
      >
        <el-table-column type="index" label="#" width="70" align="center" />

        <el-table-column
          prop="username"
          label="Student"
          min-width="220"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <div
                class="w-7 h-7 rounded-full flex items-center justify-center bg-[var(--color-primary-light-7)] text-[var(--color-primary)] text-xs font-semibold"
              >
                {{ (row.username || "?").charAt(0).toUpperCase() }}
              </div>
              <span class="text-gray-800 font-medium">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="id"
          label="Student ID"
          min-width="260"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="text-gray-500 font-mono text-xs">
              {{ row.id }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div v-else class="py-10">
        <el-empty
          v-if="
            !loadingStudents &&
            selectedClassId &&
            (students.length === 0 || filteredStudents.length === 0)
          "
          :description="
            students.length === 0
              ? 'No students enrolled yet'
              : 'No students match your search'
          "
          :image-size="120"
        >
          <template #extra>
            <p class="text-sm text-gray-500 max-w-md mx-auto">
              {{
                students.length === 0
                  ? "Students will appear here once they are added to this class."
                  : "Check spelling or clear the search box to see all students."
              }}
            </p>
          </template>
        </el-empty>

        <el-empty
          v-else-if="!loadingStudents && !selectedClassId && !classes.length"
          description="No classes available yet"
          :image-size="120"
        >
          <template #extra>
            <p class="text-sm text-gray-500 max-w-md mx-auto">
              Classes assigned to you will appear here automatically.
            </p>
          </template>
        </el-empty>

        <el-empty
          v-else-if="!loadingStudents && !selectedClassId && classes.length"
          description="Select a class to view students"
          :image-size="120"
        >
          <template #extra>
            <p class="text-sm text-gray-500 max-w-md mx-auto">
              Choose from {{ totalClasses }}
              {{ totalClasses === 1 ? "available class" : "available classes" }}
              above.
            </p>
          </template>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.el-table {
  transition: all 0.2s ease;
}

/* Focus styles for inputs and selects to match your theme */
:deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 1px var(--color-primary-light) inset;
}

:deep(.el-select:focus-within .el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--color-primary-light) inset;
}

/* Slight hover for the main card */
.el-card {
  transition: box-shadow 0.2s ease, transform 0.1s ease;
}
.el-card:hover {
  box-shadow: 0 4px 14px rgba(126, 87, 194, 0.12);
}
</style>
