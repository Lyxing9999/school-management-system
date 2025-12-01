<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";
import type { TeacherStudentNameDTO } from "~/api/teacher/dto";

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

const selectedClass = computed(
  () => classes.value.find((c) => c.id === selectedClassId.value) ?? null
);

// load teacher classes
const loadClasses = async () => {
  loadingClasses.value = true;
  errorMessage.value = null;

  try {
    const res = await teacher.teacher.listMyClasses();
    if (!res) return;

    classes.value = res.items ?? [];

    // auto-select first class if none selected
    if (!selectedClassId.value && classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id;
    }
  } catch (err: any) {
    // safeApiCall already handled toast; we only keep local state
    errorMessage.value = err?.message ?? "Failed to load classes.";
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
    const res = await teacher.teacher.listStudentNamesInClass(classId);
    if (!res) return;
    students.value = res.items ?? [];
  } catch (err: any) {

    errorMessage.value = err?.message ?? "Failed to load students.";
  } finally {
    loadingStudents.value = false;
  }
};

// react when class changes
watch(selectedClassId, (newVal) => {
  loadStudentsForClass(newVal);
});

// initial
onMounted(async () => {
  await loadClasses();
  if (selectedClassId.value) {
    await loadStudentsForClass(selectedClassId.value);
  }
});
</script>

<template>
  <div class="p-4 lg:p-6 max-w-5xl mx-auto space-y-4">
    <!-- Page header -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white/80 rounded-xl border border-gray-100 shadow-sm p-4"
    >
      <div>
        <h1 class="text-xl font-semibold text-gray-800">My Students</h1>
        <p class="mt-1 text-xs text-gray-500">
          Select a class to see all enrolled students.
        </p>
      </div>

      <div class="flex items-center gap-2 justify-end">
        <el-button
          type="primary"
          plain
          :loading="loadingClasses || loadingStudents"
          @click="
            () => {
              loadClasses();
              if (selectedClassId) loadStudentsForClass(selectedClassId);
            }
          "
        >
          Refresh
        </el-button>
      </div>
    </div>


    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="rounded-lg border border-red-100"
    />

    <!-- Main card -->
    <el-card
      shadow="never"
      :body-style="{ padding: '16px 20px 20px' }"
      class="border border-gray-100 rounded-xl"
    >
      <template #header>
        <div
          class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-gray-800">Class & Students</span>
              <el-tag v-if="selectedClass" size="small" effect="plain">
                {{ selectedClass.student_ids?.length ?? 0 }} students
              </el-tag>
            </div>
            <p class="text-xs text-gray-500">
              Choose a class to see its student list.
            </p>
          </div>

          <el-select
            v-model="selectedClassId"
            placeholder="Select class"
            size="small"
            style="min-width: 220px"
            :disabled="!classes.length || loadingClasses"
            clearable
          >
            <el-option
              v-for="c in classes"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </div>
      </template>

      <!-- Class meta -->
      <div
        v-if="selectedClass"
        class="mb-4 text-xs text-gray-500 flex flex-wrap gap-x-6 gap-y-1"
      >
        <div>
          <span class="font-semibold text-gray-700">Class: </span>
          {{ selectedClass.name }}
        </div>
        <div>
          <span class="font-semibold text-gray-700">Total students: </span>
          {{ selectedClass.student_ids?.length ?? 0 }}
        </div>
      </div>

      <!-- Table / empty states -->
      <el-table
        v-if="students.length"
        v-loading="loadingStudents"
        :data="students"
        size="small"
        border
        stripe
        highlight-current-row
        :style="{ width: '100%' }"
      >
        <el-table-column
          prop="username"
          label="Student Name"
          min-width="220"
          show-overflow-tooltip
        />
      </el-table>

      <div v-else class="py-8">
        <el-empty
          v-if="!loadingStudents && selectedClassId"
          description="No students enrolled in this class yet."
        >
          <template #extra>
            <p class="text-xs text-gray-500">
              Once students are added to this class, they will appear here.
            </p>
          </template>
        </el-empty>

        <el-empty
          v-else-if="!loadingStudents && !selectedClassId && !classes.length"
          description="No classes available."
        >
          <template #extra>
            <p class="text-xs text-gray-500">
              When classes are assigned to you, they will appear here.
            </p>
          </template>
        </el-empty>

        <el-empty
          v-else-if="!loadingStudents && !selectedClassId && classes.length"
          description="Select a class to view students."
        />
      </div>
    </el-card>
  </div>
</template>
