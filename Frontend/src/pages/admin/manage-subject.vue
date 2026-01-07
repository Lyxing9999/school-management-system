<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { storeToRefs } from "pinia";

definePageMeta({ layout: "default" });

/* ------------------------------------
 * Base components
 * ---------------------------------- */
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import SmartFormDialog from "~/components/form/SmartFormDialog.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import ActionButtons from "~/components/buttons/ActionButtons.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";

/* ------------------------------------
 * Element Plus
 * ---------------------------------- */
import {
  ElMessageBox,
  ElMessage,
  ElRadioGroup,
  ElRadioButton,
  ElSwitch,
} from "element-plus";
import { Refresh } from "@element-plus/icons-vue";

/* ------------------------------------
 * Services & types
 * ---------------------------------- */
import { adminService } from "~/api/admin";
import type {
  AdminSubjectDataDTO,
  AdminCreateSubject,
  AdminUpdateSubject,
  SubjectStatus,
} from "~/api/admin/subject/subject.dto";
import type { ColumnConfig } from "~/components/types/tableEdit";

/* ------------------------------------
 * Dynamic create form system
 * ---------------------------------- */
import { useDynamicCreateFormReactive } from "~/form-system/useDynamicForm.ts/useAdminForms";

/* ------------------------------------
 * Table columns
 * ---------------------------------- */
import { subjectColumns } from "~/modules/tables/columns/admin/subjectColumns";
import { applyInlineEditMode } from "~/utils/table/applyInlineEditMode";

/* ------------------------------------
 * Pagination composable
 * ---------------------------------- */
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";

/* ------------------------------------
 * Header stats composable
 * ---------------------------------- */
import { useHeaderState } from "~/composables/ui/useHeaderState";

/* ------------------------------------
 * Preferences (Pinia)
 * ---------------------------------- */
import { usePreferencesStore } from "~/stores/preferencesStore";

/* ------------------------------------
 * Inline edit
 * ---------------------------------- */
import { useInlineEdit } from "~/composables/table-edit/useInlineEdit";

/* ------------------------------------
 * Utils
 * ---------------------------------- */
import { reportError } from "~/utils/errors/errors";

const adminApi = adminService();

/* ===========================
 *  STATE
 * =========================== */
type SubjectFilter = SubjectStatus; // "all" | "active" | "inactive"

const prefs = usePreferencesStore();
const { tablePageSize, inlineEditMode } = storeToRefs(prefs);

const activeFilter = ref<SubjectFilter>("active");
const searchModel = ref(""); // OverviewHeader search model

/* ---------------------- columns (inline edit mode) ---------------------- */
const resolvedSubjectColumns = computed(() =>
  applyInlineEditMode(
    subjectColumns as ColumnConfig<AdminSubjectDataDTO>[],
    inlineEditMode.value
  )
);

/* ===========================
 *  PAGINATED FETCH (SERVER)
 * =========================== */
const {
  data: subjects,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  initialLoading,
  fetching,
  fetchPage,
  goPage,
} = usePaginatedFetch<AdminSubjectDataDTO, SubjectFilter>(
  async (filter, page, pageSize, _signal) => {
    const search = searchModel.value.trim();

    const res = await adminApi.subject.getSubjects({
      status: filter,
      page,
      page_size: pageSize,
      search: search.length ? search : null,
    });

    return { items: res.items ?? [], total: res.total ?? 0 };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: activeFilter,
  }
);

const tableLoading = computed(() => initialLoading.value || fetching.value);

/* ===========================
 *  HEADER STATS
 * =========================== */
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

/* ===========================
 *  CREATE SUBJECT (DYNAMIC FORM)
 * =========================== */
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

const createFormDialogWidth = computed(() => "40%");

async function openCreateDialog() {
  await openCreateForm();
}

async function handleSaveCreateForm(payload: Partial<AdminCreateSubject>) {
  const created = await saveCreateForm(payload);
  if (!created) return;
  await fetchPage(1);
}

function handleCancelCreateForm() {
  cancelCreateForm();
}

/* ===========================
 *  ACTIONS
 * =========================== */
async function fetchSubjects() {
  await fetchPage(currentPage.value || 1);
}

const statusLoading = ref<Record<string | number, boolean>>({});

async function toggleSubjectActive(row: AdminSubjectDataDTO) {
  const id = String(row.id);
  const previous = row.is_active;

  statusLoading.value[id] = true;

  try {
    if (row.is_active) await adminApi.subject.activateSubject(id);
    else await adminApi.subject.deactivateSubject(id);

    await fetchPage(currentPage.value || 1);
  } catch (err) {
    reportError(err, `subject.toggleActive id=${id}`, "log");
    row.is_active = previous;
    ElMessage.error("Failed to update subject status.");
  } finally {
    statusLoading.value[id] = false;
  }
}

/* ===========================
 *  INLINE EDIT
 * =========================== */
const inlineSubjectService = {
  update: async (id: string, payload: Partial<AdminSubjectDataDTO>) =>
    await adminApi.subject.updateSubject(
      id,
      payload as unknown as AdminUpdateSubject,
      { showError: false }
    ),
  delete: async (id: string) => {
    await adminApi.subject.softDeleteSubject(id);
    await fetchPage(currentPage.value || 1);
  },
};

const {
  data: rows,
  save,
  cancel,
  remove: removeSubject,
  deleteLoading,
  inlineEditLoading,
  autoSave,
  getPreviousValue,
  revertField,
  setData: setInlineData,
} = useInlineEdit<AdminSubjectDataDTO, AdminSubjectDataDTO>([], {
  value: inlineSubjectService,
});

watch(subjects, (newRows) => setInlineData(newRows ?? []), { immediate: true });

function asEditable(
  field: keyof AdminSubjectDataDTO
): keyof AdminSubjectDataDTO | null {
  if (field === "id") return null;
  return field;
}

/* ===========================
 *  DELETE (WITH CONFIRM)
 * =========================== */
async function handleSoftDelete(row: AdminSubjectDataDTO) {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to soft delete this subject?",
      "Warning",
      { confirmButtonText: "Yes", cancelButtonText: "No", type: "warning" }
    );
    await removeSubject(row);
  } catch {
    // canceled => do nothing
  }
}

/* ===========================
 *  LIFECYCLE
 * =========================== */
onMounted(() => fetchPage(1));
watch(activeFilter, () => fetchPage(1));

let searchTimer: any = null;
watch(searchModel, () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => fetchPage(1), 350);
});

const allowedGradesOnly = (grades: unknown): number[] => {
  if (!Array.isArray(grades)) return [];
  return grades
    .map(Number)
    .filter((n) => Number.isInteger(n) && n >= 0 && n <= 12)
    .sort((a, b) => a - b);
};
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="Subjects"
      description="Manage subjects and their availability across the school."
      :loading="tableLoading"
      :stats="subjectHeaderStats"
      :show-refresh="true"
      :show-search="true"
      :show-reset="true"
      :reset-disabled="activeFilter === 'active' && !searchModel.trim()"
      :search-model-value="searchModel"
      @update:searchModelValue="(v: string) => (searchModel = v)"
      @refresh="fetchSubjects"
      @reset="
        () => {
          activeFilter = 'active';
          searchModel = '';
          fetchPage(1);
        }
      "
    >
      <template #filters>
        <el-row :gutter="12" align="middle" class="w-full">
          <!-- Search label left (OverviewHeader renders the input) -->
          <el-col :xs="24" :sm="24" :md="12">
            <div class="flex flex-wrap items-center gap-2 w-full">
              <span class="text-xs text-gray-500 whitespace-nowrap"
                >Search:</span
              >
              <span class="text-xs text-gray-500 whitespace-nowrap">
                (type and pause)
              </span>
            </div>
          </el-col>

          <!-- Status right -->
          <el-col :xs="24" :sm="24" :md="12">
            <div
              class="flex flex-wrap items-center gap-2 md:justify-end w-full"
            >
              <span class="text-xs text-gray-500 whitespace-nowrap"
                >Status:</span
              >
              <ElRadioGroup
                v-model="activeFilter"
                size="small"
                :disabled="tableLoading"
              >
                <ElRadioButton label="all">All</ElRadioButton>
                <ElRadioButton label="active">Active</ElRadioButton>
                <ElRadioButton label="inactive">Inactive</ElRadioButton>
              </ElRadioGroup>
            </div>
          </el-col>
        </el-row>
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

        <BaseButton
          type="primary"
          :disabled="tableLoading"
          @click="openCreateDialog"
        >
          Add Subject
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-card>
      <SmartTable
        :data="rows"
        :columns="resolvedSubjectColumns"
        :loading="tableLoading"
        :inline-edit-loading="inlineEditLoading"
        @save="save"
        @cancel="cancel"
        @auto-save="autoSave"
      >
        <template #status="{ row }">
          <ElSwitch
            v-model="row.is_active"
            :loading="statusLoading[String(row.id)]"
            @change="toggleSubjectActive(row)"
          />
        </template>
        <template #allowedGrades="{ row }">
          <div class="flex flex-wrap gap-1">
            <el-tag
              v-for="g in allowedGradesOnly(row.allowed_grade_levels)"
              :key="g"
              size="small"
              class="tag-primary"
            >
              {{ g }}
            </el-tag>

            <el-tag
              v-if="!allowedGradesOnly(row.allowed_grade_levels).length"
              size="small"
              class="tag-muted"
            >
              None
            </el-tag>
          </div>
        </template>
        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            deleteContent="Delete subject"
            :deleteLoading="deleteLoading[row.id] ?? false"
            :detailLoading="false"
            :showDetail="false"
            :showDelete="true"
            @delete="handleSoftDelete(row)"
          />
        </template>

        <template #revertSlots="{ row, field }">
          <el-tooltip
            :content="
              (() => {
                const f = asEditable(field);
                return f ? `Previous: ${getPreviousValue(row, f)}` : '—';
              })()
            "
            placement="top"
          >
            <el-icon
              class="cursor-pointer"
              @click="
                (() => {
                  const f = asEditable(field);
                  if (f) revertField(row, f);
                })()
              "
            >
              <Refresh />
            </el-icon>
          </el-tooltip>
        </template>
      </SmartTable>

      <div v-if="(rows?.length ?? 0) === 0 && !tableLoading" class="p-6">
        <el-empty description="No subjects found" />
      </div>
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
        @size-change="(size: number) => prefs.setTablePageSize(size)"
      />
    </el-row>

    <SmartFormDialog
      v-model:visible="createFormVisible"
      v-model="createFormData"
      :fields="baseCreateFormSchema"
      title="Add Subject"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createFormDialogWidth"
    />
  </div>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}

.tag-primary {
  border-radius: 10px !important;

  background: color-mix(
    in srgb,
    var(--color-primary) 16%,
    var(--color-card) 84%
  ) !important;
  border: 1px solid
    color-mix(in srgb, var(--color-primary) 45%, var(--border-color) 55%) !important;
  color: var(--color-primary) !important;

  font-weight: 650;
}

.tag-muted {
  border-radius: 10px !important;

  background: color-mix(
    in srgb,
    var(--color-card) 92%,
    var(--color-bg) 8%
  ) !important;
  border: 1px solid color-mix(in srgb, var(--border-color) 75%, transparent) !important;
  color: color-mix(
    in srgb,
    var(--text-color) 70%,
    var(--muted-color) 30%
  ) !important;

  font-weight: 600;
}
</style>
