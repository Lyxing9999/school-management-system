<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";

definePageMeta({
  layout: "admin",
});

// --------------------
// Base Components
// --------------------
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";

// Element Plus
import { ElRadioGroup, ElRadioButton, ElSwitch } from "element-plus";

// --------------------
// Services & Types
// --------------------
import { adminService } from "~/api/admin";
import type {
  AdminSubjectDataDTO,
  AdminSubjectListDTO,
  AdminCreateSubject,
} from "~/api/admin/subject/subject.dto";
// For grade labels in table
import { gradeOptions } from "~/modules/forms/admin/subject/subject.schema";

// Dynamic form system
import { useDynamicCreateFormReactive } from "~/form-system/useDynamicForm.ts/useAdminForms";
import { subjectColumns } from "~/modules/tables/columns/admin/subjectColumns";

// Pagination composable
import { usePaginatedFetch } from "~/composables/usePaginatedFetch";
import { useHeaderState } from "~/composables/useHeaderState";

const adminApi = adminService();

/* ---------------------- filter state ---------------------- */

type SubjectFilter = "all" | "active" | "inactive";
const activeFilter = ref<SubjectFilter>("all");

/* ---------------------- paginated fetch (reusing composable) ---------------------- */

const {
  data: subjects,
  loading: tableLoading,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<AdminSubjectDataDTO, SubjectFilter>(
  async (filter, page, pageSize, _signal) => {
    const res: AdminSubjectListDTO | undefined =
      await adminApi.subject.getSubjects();

    const allItems = res?.items ?? [];

    const filtered =
      filter === "all"
        ? allItems
        : filter === "active"
        ? allItems.filter((s) => s.is_active)
        : allItems.filter((s) => !s.is_active);

    const total = filtered.length;
    const start = (page - 1) * pageSize;
    const items = filtered.slice(start, start + pageSize);

    return { items, total };
  },
  1,
  10,
  activeFilter
);

/* ---------------------- grade options display helper ---------------------- */

function formatAllowedGrades(levels?: number[]) {
  if (!levels || !levels.length) return "-";
  return levels
    .map(
      (lvl) =>
        gradeOptions.value.find((g) => g.value === lvl)?.label || `Grade ${lvl}`
    )
    .join(", ");
}

/* ---------------------- CREATE FORM (dynamic) ---------------------- */

const createMode = ref<"SUBJECT">("SUBJECT");

const {
  formDialogVisible: createFormVisible,
  formData: createFormData,
  schema: baseCreateFormSchema,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
  openForm: openCreateForm,
  loading: createFormLoading,
} = useDynamicCreateFormReactive(createMode);

const createDialogWidth = computed(() => "40%");
const createDialogKey = ref(0);

async function openCreateDialog() {
  createDialogKey.value++;
  await openCreateForm();
}

async function handleSaveCreateForm(payload: Partial<AdminCreateSubject>) {
  await saveCreateForm(payload);
  await fetchPage(1);
}

function handleCancelCreateForm() {
  cancelCreateForm();
}

/* ---------------------- actions: refresh + toggle ---------------------- */

async function fetchSubjects() {
  await fetchPage(currentPage.value || 1);
}

const statusLoading = ref<Record<string, boolean>>({});

async function toggleSubjectActive(row: AdminSubjectDataDTO) {
  const id = row.id;
  const previous = row.is_active;

  statusLoading.value[id] = true;

  try {
    if (row.is_active) {
      await adminApi.subject.activateSubject(id);
    } else {
      await adminApi.subject.deactivateSubject(id);
    }
    await fetchPage(currentPage.value || 1);
  } catch (err) {
    console.error("Failed to toggle subject active state", err);
    row.is_active = previous;
  } finally {
    statusLoading.value[id] = false;
  }
}

/* ---------------------- header stats ---------------------- */

const totalSubjects = computed(() => totalRows.value ?? 0);

const { headerState: subjectHeaderStats } = useHeaderState({
  items: [
    {
      key: "subjects",
      getValue: () => totalSubjects.value,
      singular: "subject",
      plural: "subjects",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "filter",
      getValue: () => (activeFilter.value === "all" ? 0 : 1),
      label: () =>
        activeFilter.value === "all"
          ? "All statuses"
          : `Filter: ${activeFilter.value}`,
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});

/* ---------------------- watch filter ---------------------- */

watch(activeFilter, () => {
  fetchPage(1);
});

/* ---------------------- lifecycle ---------------------- */

onMounted(() => {
  fetchPage(1);
});
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="Subjects"
      description="Manage subjects and their availability across the school."
      :loading="tableLoading"
      :showRefresh="false"
      :stats="subjectHeaderStats"
    >
      <template #filters>
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Status:</span>
            <ElRadioGroup v-model="activeFilter" size="small">
              <ElRadioButton label="all">All</ElRadioButton>
              <ElRadioButton label="active">Active</ElRadioButton>
              <ElRadioButton label="inactive">Inactive</ElRadioButton>
            </ElRadioGroup>
          </div>
        </div>
      </template>

      <template #actions>
        <BaseButton
          plain
          :loading="tableLoading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="fetchSubjects"
        >
          Refresh
        </BaseButton>

        <BaseButton type="primary" @click="openCreateDialog">
          Add Subject
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-card>
      <SmartTable
        :data="subjects"
        :columns="subjectColumns"
        :loading="tableLoading"
      >
        <template #description="{ row }">
          <div class="description-cell">
            <span
              v-if="row.description"
              class="description-text"
              :title="row.description"
            >
              {{ row.description }}
            </span>

            <span v-else class="description-empty">
              <span>No description</span>
            </span>
          </div>
        </template>

        <template #allowedGrades="{ row }">
          <span>{{ formatAllowedGrades(row.allowed_grade_levels) }}</span>
        </template>

        <template #operation="{ row }">
          <ElSwitch
            v-model="row.is_active"
            :loading="statusLoading[row.id]"
            @change="() => toggleSubjectActive(row)"
          />
        </template>
      </SmartTable>
    </el-card>

    <el-row v-if="totalRows > 0" justify="end" class="m-4">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="totalRows"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="goPage"
        @size-change="
          (size: number) => {
            pageSize = size;
            fetchPage(1);
          }
        "
      />
    </el-row>

    <SmartFormDialog
      :key="createDialogKey"
      v-model:visible="createFormVisible"
      v-model="createFormData"
      :fields="baseCreateFormSchema"
      title="Add Subject"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createDialogWidth"
    />
  </div>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}

.description-cell {
  display: flex;
  align-items: center;
  max-width: 260px;
}

.description-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.description-empty {
  font-size: 12px;
  color: #9ca3af;
  font-style: italic;
}
</style>
