<!-- ~/pages/teacher/students/index.vue -->
<script setup lang="ts">
definePageMeta({ layout: "teacher" });

import { ref, computed, watch, onMounted } from "vue";
import { ElMessage } from "element-plus";

import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";

import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import TeacherClassSelect from "~/components/Selects/TeacherClassSelect.vue";
import TableCard from "~/components/Cards/TableCard.vue";
import { useHeaderState } from "~/composables/useHeaderState";

const teacher = teacherService();

/* ----------------- types (backend -> UI adapter) ----------------- */

type BackendStudentDTO = {
  id: string;
  user_id?: string;
  student_id_code?: string;
  first_name_kh?: string;
  last_name_kh?: string;
  first_name_en?: string;
  last_name_en?: string;
  gender?: string;
  dob?: string; // "YYYY-MM-DD"
  status?: string;
  phone_number?: string;
  current_class_id?: string;
};

type StudentRow = {
  id: string;
  code: string;
  name: string;
  gender: string;
  dob: string;
  status: string;
  phone: string;
};

const buildStudentName = (s: BackendStudentDTO) => {
  const en = `${s.first_name_en ?? ""} ${s.last_name_en ?? ""}`.trim();
  if (en) return en;

  const kh = `${s.first_name_kh ?? ""} ${s.last_name_kh ?? ""}`.trim();
  if (kh) return kh;

  return s.student_id_code ?? "Unknown Student";
};

const toStudentRow = (s: BackendStudentDTO): StudentRow => ({
  id: s.id,
  code: s.student_id_code ?? "-",
  name: buildStudentName(s),
  gender: s.gender ?? "-",
  dob: s.dob ?? "-",
  status: s.status ?? "-",
  phone: s.phone_number ?? "-",
});

const formatDob = (dob: string) => {
  return dob && dob !== "-" ? dob : "-";
};

const statusTagType = (status: string) => {
  const v = (status || "").toLowerCase();
  if (v === "active") return "success";
  if (v === "inactive") return "info";
  if (v === "suspended") return "warning";
  return "default";
};

/* ----------------- state ----------------- */

const loadingClasses = ref(false);
const loadingStudents = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<ClassSectionDTO[]>([]);
const selectedClassId = ref<string | null>(null);
const students = ref<StudentRow[]>([]);

// UI helpers
const searchTerm = ref("");

// derived
const selectedClass = computed(
  () => classes.value.find((c) => c.id === selectedClassId.value) ?? null
);

const totalClasses = computed(() => classes.value.length);
const totalStudentsInSelected = computed(() => students.value.length);

/* ----------------- filter + pagination ----------------- */

const filteredStudents = computed(() => {
  const term = searchTerm.value.trim().toLowerCase();
  if (!term) return students.value;

  return students.value.filter((s) => {
    return (
      s.name.toLowerCase().includes(term) ||
      s.code.toLowerCase().includes(term) ||
      s.phone.toLowerCase().includes(term) ||
      s.id.toLowerCase().includes(term)
    );
  });
});

const currentPage = ref(1);
const pageSize = ref(10);

const pagedStudents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredStudents.value.slice(start, end);
});

watch(
  () => searchTerm.value,
  () => {
    currentPage.value = 1;
  }
);

/* ----------------- API: load classes ----------------- */

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

/* ----------------- API: load students ----------------- */

const loadStudentsForClass = async (classId: string | null) => {
  students.value = [];
  currentPage.value = 1;
  searchTerm.value = "";

  if (!classId) return;

  loadingStudents.value = true;
  errorMessage.value = null;

  try {
    const res = await teacher.teacher.listStudentsInClass(classId, {
      showError: false,
    });

    const raw = (res.items ?? []) as BackendStudentDTO[];
    students.value = raw.map(toStudentRow);
  } catch (err: any) {
    const msg = err?.message ?? "Failed to load students.";
    errorMessage.value = msg;
    ElMessage.error(msg);
  } finally {
    loadingStudents.value = false;
  }
};

watch(selectedClassId, (newVal) => {
  loadStudentsForClass(newVal);
});

onMounted(async () => {
  await loadClasses();
  if (selectedClassId.value) {
    await loadStudentsForClass(selectedClassId.value);
  }
});

const handleRefresh = async () => {
  await loadClasses();
  if (selectedClassId.value) {
    await loadStudentsForClass(selectedClassId.value);
  }
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
};

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
};

/* ----------------- header stats ----------------- */

const { headerState } = useHeaderState({
  items: [
    {
      key: "classes",
      getValue: () => totalClasses.value,
      singular: "class",
      plural: "classes",
      suffix: "assigned",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "students",
      getValue: () => totalStudentsInSelected.value,
      singular: "student",
      plural: "students",
      suffix: "in this class",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
  ],
});
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="My Students"
      description="Quickly see which students belong to each of your classes."
      :loading="loadingClasses || loadingStudents"
      :showRefresh="false"
      :stats="headerState"
    >
      <template #filters>
        <div class="flex flex-wrap items-center gap-3">
          <!-- Class select pill -->
          <div
            class="flex items-center gap-2 px-3 py-1.5 rounded-full border shadow-sm"
            style="
              background: var(--color-card);
              border-color: var(--color-primary-light-7);
            "
          >
            <span
              class="text-xs font-medium"
              style="color: var(--color-primary)"
            >
              Class:
            </span>

            <TeacherClassSelect
              v-model="selectedClassId"
              placeholder="Select class"
              style="min-width: 220px"
              class="header-class-select"
            />
          </div>
        </div>
      </template>

      <template #actions>
        <BaseButton
          plain
          :loading="loadingClasses || loadingStudents"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="handleRefresh"
        >
          Refresh
        </BaseButton>
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

    <TableCard
      title="Student list"
      :description="
        selectedClass
          ? `Students enrolled in: ${selectedClass.name ?? 'Selected class'}`
          : 'Students enrolled in the selected class.'
      "
      :rightText="`Showing ${pagedStudents.length} / ${filteredStudents.length} students`"
    >
      <el-table
        v-if="filteredStudents.length || loadingClasses || loadingStudents"
        v-loading="loadingClasses || loadingStudents"
        :data="pagedStudents"
        size="default"
        stripe
        highlight-current-row
        class="rounded-lg overflow-hidden w-full"
        :header-cell-style="{
          background: 'var(--color-card)',
          color: 'var(--text-color)',
          fontWeight: '600',
          fontSize: '13px',
          borderBottom: '1px solid var(--border-color)',
        }"
      >
        <el-table-column type="index" label="#" width="70" align="center" />

        <!-- Student (name + code) -->
        <el-table-column label="Student" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold"
                style="
                  background: var(--color-primary-light-7);
                  color: var(--color-primary);
                "
              >
                {{ (row.name || "?").charAt(0).toUpperCase() }}
              </div>

              <div class="flex flex-col leading-tight">
                <span class="font-medium" style="color: var(--text-color)">
                  {{ row.name }}
                </span>
                <span class="text-xs" style="color: var(--muted-color)">
                  {{ row.code }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="gender" label="Gender" width="120" />

        <el-table-column label="DOB" width="140">
          <template #default="{ row }">
            <span style="color: var(--muted-color)">{{
              formatDob(row.dob)
            }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Status" width="140">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="light">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          prop="phone"
          label="Phone"
          min-width="160"
          show-overflow-tooltip
        />

        <el-table-column
          label="Record ID"
          min-width="260"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="font-mono text-xs" style="color: var(--muted-color)">
              {{ row.id }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="filteredStudents.length > 0" class="mt-4 flex justify-end">
        <el-pagination
          background
          layout="prev, pager, next, jumper, sizes, total"
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="filteredStudents.length"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>

      <div v-else class="py-10">
        <el-empty
          v-if="!loadingStudents && selectedClassId"
          :description="
            students.length === 0
              ? 'No students enrolled yet'
              : 'No students match your search'
          "
          :image-size="120"
        >
          <template #extra>
            <p
              class="text-sm max-w-md mx-auto"
              style="color: var(--muted-color)"
            >
              {{
                students.length === 0
                  ? "Students will appear here once they are added to this class."
                  : "Check spelling or clear the search box to see all students."
              }}
            </p>
          </template>
        </el-empty>
      </div>
    </TableCard>
  </div>
</template>

<style scoped>
:deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}
:deep(.el-select:focus-within .el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}
</style>
