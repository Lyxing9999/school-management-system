<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, computed, watch, onMounted } from "vue";
import { storeToRefs } from "pinia";
import { ElMessage, ElInput, ElAlert, ElEmpty, ElTag } from "element-plus";

import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";
import type { TeacherStudentDataDTO } from "~/api/teacher/dto";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import TeacherClassSelect from "~/components/selects/class/TeacherClassSelect.vue";
import TableCard from "~/components/cards/TableCard.vue";
import { useHeaderState } from "~/composables/ui/useHeaderState";

import { usePreferencesStore } from "~/stores/preferencesStore";

const teacherApi = teacherService();
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

/* ----------------- helpers ----------------- */
function unwrapApi<T = any>(res: any): T {
  // axios usually: res.data
  const d = res?.data ?? res;
  // your common response: { success, message, data: {...} }
  return (d?.data ?? d) as T;
}

function fullNameEn(s: TeacherStudentDataDTO) {
  return `${s.first_name_en ?? ""} ${s.last_name_en ?? ""}`.trim();
}
function fullNameKh(s: TeacherStudentDataDTO) {
  return `${s.first_name_kh ?? ""} ${s.last_name_kh ?? ""}`.trim();
}
function displayName(s: TeacherStudentDataDTO) {
  return fullNameEn(s) || fullNameKh(s) || "-";
}

function initials(s: TeacherStudentDataDTO) {
  const n = displayName(s);
  return (n?.[0] ?? "?").toUpperCase();
}

function statusTagType(status: string) {
  const v = String(status || "").toLowerCase();
  if (v === "active") return "success";
  if (v === "inactive") return "info";
  if (v === "suspended") return "warning";
  return "info";
}

function formatDob(dob?: string) {
  const v = String(dob ?? "-");
  return v && v !== "-" ? v : "-";
}

/* ----------------- state ----------------- */
const loadingClasses = ref(false);
const loadingStudents = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<ClassSectionDTO[]>([]);
const selectedClassId = ref<string | null>(null);

const students = ref<TeacherStudentDataDTO[]>([]);
const searchTerm = ref("");

const selectedClass = computed(
  () => classes.value.find((c) => c.id === selectedClassId.value) ?? null
);

const totalClasses = computed(() => classes.value.length);
const totalStudentsInSelected = computed(() => students.value.length);

/* ----------------- filtering ----------------- */
const filteredStudents = computed(() => {
  const term = searchTerm.value.trim().toLowerCase();
  if (!term) return students.value;

  return students.value.filter((s) => {
    const nameEn = fullNameEn(s).toLowerCase();
    const nameKh = fullNameKh(s).toLowerCase();
    const code = String(s.student_id_code ?? "").toLowerCase();
    const phone = String(s.phone_number ?? "").toLowerCase();
    const id = String(s.id ?? "").toLowerCase();

    return (
      nameEn.includes(term) ||
      nameKh.includes(term) ||
      code.includes(term) ||
      phone.includes(term) ||
      id.includes(term)
    );
  });
});

/* ----------------- pagination (client-side) ----------------- */
const currentPage = ref(1);
const pageSize = ref<number>(Number(tablePageSize.value || 10));

watch(tablePageSize, (v) => {
  const next = Number(v || 10);
  if (!Number.isFinite(next) || next <= 0) return;
  pageSize.value = next;
  currentPage.value = 1;
});

watch(searchTerm, () => {
  currentPage.value = 1;
});

const pagedStudents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredStudents.value.slice(start, end);
});

/* ----------------- API: classes ----------------- */
async function loadClasses() {
  loadingClasses.value = true;
  errorMessage.value = null;

  try {
    const res: any = await teacherApi.teacher.listMyClasses({
      showError: false,
    });
    const payload = unwrapApi<{ items: ClassSectionDTO[] }>(res);

    classes.value = payload?.items ?? [];

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
}

/* ----------------- API: students ----------------- */
async function loadStudentsForClass(classId: string | null) {
  students.value = [];
  currentPage.value = 1;
  searchTerm.value = "";

  if (!classId) return;

  loadingStudents.value = true;
  errorMessage.value = null;

  try {
    const res: any = await teacherApi.teacher.listStudentsInClass(classId, {
      showError: false,
    });

    const payload = unwrapApi<{ items: TeacherStudentDataDTO[] }>(res);
    students.value = payload?.items ?? [];
  } catch (err: any) {
    const msg = err?.message ?? "Failed to load students.";
    errorMessage.value = msg;
    ElMessage.error(msg);
  } finally {
    loadingStudents.value = false;
  }
}

watch(selectedClassId, (id) => {
  loadStudentsForClass(id);
});

/* ----------------- actions ----------------- */
async function handleRefresh() {
  await loadClasses();
  if (selectedClassId.value) await loadStudentsForClass(selectedClassId.value);
}

function handlePageChange(page: number) {
  currentPage.value = page;
}

function handlePageSizeChange(size: number) {
  // persist globally (your existing store pattern)
  prefs.setTablePageSize(size);
}

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

/* ----------------- mount ----------------- */
onMounted(async () => {
  await loadClasses();
  if (selectedClassId.value) {
    await loadStudentsForClass(selectedClassId.value);
  }
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
      <ElAlert
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
      <!-- Search -->
      <div class="mb-4 flex items-center justify-between gap-3 flex-wrap">
        <ElInput
          v-model="searchTerm"
          clearable
          placeholder="Search name, code, phone, or record ID..."
          style="max-width: 420px"
        />
      </div>

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
        <el-table-column label="Student" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold"
                style="
                  background: var(--color-primary-light-7);
                  color: var(--color-primary);
                "
              >
                {{ initials(row) }}
              </div>

              <div class="flex flex-col leading-tight min-w-0">
                <span
                  class="font-medium truncate"
                  style="color: var(--text-color)"
                >
                  {{ displayName(row) }}
                </span>
                <span
                  class="text-xs truncate"
                  style="color: var(--muted-color)"
                >
                  {{ row.student_id_code || "-" }}
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
            <ElTag :type="statusTagType(row.status)" effect="light">
              {{ row.status }}
            </ElTag>
          </template>
        </el-table-column>

        <el-table-column
          prop="phone_number"
          label="Phone"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span>{{ row.phone_number || "-" }}</span>
          </template>
        </el-table-column>

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
        <ElEmpty
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
        </ElEmpty>
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
