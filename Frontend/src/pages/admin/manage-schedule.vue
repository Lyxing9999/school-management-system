<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from "vue";
import { storeToRefs } from "pinia";

definePageMeta({ layout: "default" });

/* Base components */
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import SmartFormDialog from "~/components/form/SmartFormDialog.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import ActionButtons from "~/components/buttons/ActionButtons.vue";
import TeacherSelect from "~/components/selects/teacher/TeacherSelect.vue";
import ClassSelect from "~/components/selects/class/ClassSelect.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";

/* Element Plus */
import {
  ElRadioGroup,
  ElRadioButton,
  ElEmpty,
  ElSkeleton,
  ElMessageBox,
  ElTag,
} from "element-plus";

/* Services & types */
import { adminService } from "~/api/admin";
import type { AdminScheduleSlotData } from "~/api/admin/schedule/schedule.dto";

/* Helpers */
import { useLabelMap } from "~/composables/common/useLabelMap";
import { createScheduleColumns } from "~/modules/tables/columns/admin/scheduleColumns";
import { reportError } from "~/utils/errors/errors";

/* Dynamic forms */
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
} from "~/form-system/useDynamicForm.ts/useAdminForms";

/* Pagination + header stats */
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { useHeaderState } from "~/composables/ui/useHeaderState";

/* Preferences store (page size) */
import { usePreferencesStore } from "~/stores/preferencesStore";

const adminApi = adminService();

/* ---------------------- store ---------------------- */
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

/* ---------------------- types ---------------------- */
type ViewMode = "class" | "teacher";
type ActiveFilter =
  | { mode: "class"; classId: string }
  | { mode: "teacher"; teacherId: string };
type ScheduleFilter = ActiveFilter | null;

/* ---------------------- mode + selection ---------------------- */
const viewMode = ref<ViewMode>("class");
const selectedClassId = ref<string | null>(null);
const selectedTeacherId = ref<string | null>(null);

const activeFilter = computed<ActiveFilter | null>(() => {
  if (viewMode.value === "class" && selectedClassId.value) {
    return { mode: "class", classId: selectedClassId.value };
  }
  if (viewMode.value === "teacher" && selectedTeacherId.value) {
    return { mode: "teacher", teacherId: selectedTeacherId.value };
  }
  return null;
});

const hasSelectedFilter = computed(() => activeFilter.value !== null);

/* ---------------------- teacher label map (for columns) ---------------------- */
const teacherOptions = ref<{ value: string; label: string }[]>([]);
const optionsLoading = ref({ teachers: false });
const teacherLabelMap = useLabelMap(teacherOptions);

async function fetchTeacherOptions() {
  if (optionsLoading.value.teachers) return;
  optionsLoading.value.teachers = true;

  try {
    const res: any = await adminApi.staff.listTeacherSelect();
    const items = res?.items ?? [];
    teacherOptions.value = items
      .filter((s: any) => s.role === "teacher" || s.role === "academic")
      .map((t: any) => ({
        value: String(t.id),
        label:
          t.full_name ?? `${t.first_name ?? ""} ${t.last_name ?? ""}`.trim(),
      }));
  } catch (err: unknown) {
    reportError(err, "schedule.fetchTeacherOptions", "log");
  } finally {
    optionsLoading.value.teachers = false;
  }
}

/* ---------------------- columns ---------------------- */
const scheduleColumns = computed(() => createScheduleColumns(teacherLabelMap));

/* ---------------------- paginated fetch ---------------------- */
const {
  data: slots,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  initialLoading,
  fetching,
  fetchPage,
  goPage,
} = usePaginatedFetch<AdminScheduleSlotData, ScheduleFilter>(
  async (filter, page, size, _signal) => {
    if (!filter) return { items: [], total: 0 };

    const params = { page, page_size: size };

    if (filter.mode === "class") {
      const res = await adminApi.scheduleSlot.getClassSchedule(
        filter.classId,
        params
      );
      return { items: res.items ?? [], total: res.total ?? 0 };
    }

    const res = await adminApi.scheduleSlot.getTeacherSchedule(
      filter.teacherId,
      params
    );
    return { items: res.items ?? [], total: res.total ?? 0 };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: activeFilter,
  }
);

const tableLoading = computed(() => initialLoading.value || fetching.value);

/* ---------------------- derived UI states ---------------------- */
const showTable = computed(
  () => hasSelectedFilter.value && !tableLoading.value && slots.value.length > 0
);
const showEmptyState = computed(
  () =>
    hasSelectedFilter.value && !tableLoading.value && slots.value.length === 0
);
const showInitialEmptyState = computed(
  () => !hasSelectedFilter.value && !tableLoading.value
);

async function fetchSchedule(page = currentPage.value || 1) {
  if (!activeFilter.value) return;
  await fetchPage(page);
}

/* ---------------------- mode / selection reactions ---------------------- */
watch(
  viewMode,
  async (mode) => {
    if (mode === "class") selectedTeacherId.value = null;
    else selectedClassId.value = null;

    if (mode === "teacher" && teacherOptions.value.length === 0) {
      await fetchTeacherOptions();
    }

    if (activeFilter.value) {
      await fetchPage(1);
    }
  },
  { immediate: true }
);

watch(
  activeFilter,
  async (next, prev) => {
    const prevKey = prev
      ? `${prev.mode}:${"classId" in prev ? prev.classId : prev.teacherId}`
      : null;
    const nextKey = next
      ? `${next.mode}:${"classId" in next ? next.classId : next.teacherId}`
      : null;

    if (prevKey !== nextKey && next) {
      await fetchPage(1);
    }
  },
  { immediate: true }
);

/* ---------------------- create slot ---------------------- */
type CreateMode = "SCHEDULE_SLOT";
const formEntity = ref<CreateMode>("SCHEDULE_SLOT");

const {
  formDialogVisible: createFormVisible,
  formData: createFormData,
  schema: createFormSchema,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
  openForm: openCreateForm,
  loading: createFormLoading,
  resetFormData: resetCreateFormData,
} = useDynamicCreateFormReactive(formEntity);

const createDialogKey = ref(0);

const handleOpenCreateForm = async () => {
  if (!activeFilter.value) return;

  createDialogKey.value++;

  const payload =
    activeFilter.value.mode === "class"
      ? { class_id: activeFilter.value.classId, __lock_class_id: true }
      : { teacher_id: activeFilter.value.teacherId, __lock_teacher_id: true };

  await openCreateForm(payload);
};

watch(formEntity, () => resetCreateFormData());

const handleSaveCreateForm = async (payload: Partial<any>) => {
  await saveCreateForm(payload);
  await fetchPage(1);
};

const handleCancelCreateForm = () => cancelCreateForm();

/* ---------------------- edit slot (includes subject assignment) ---------------------- */
const {
  formDialogVisible: editFormVisible,
  formData: editFormData,
  schema: editFormSchema,
  openForm: openEditForm,
  saveForm: saveEditForm,
  cancelForm: cancelEditForm,
  loading: editFormLoading,
} = useDynamicEditFormReactive(formEntity);

const detailLoading = ref<Record<string | number, boolean>>({});
const editFormDataKey = ref("");

const handleOpenEditForm = async (row: AdminScheduleSlotData) => {
  try {
    detailLoading.value[row.id] = true;
    editFormDataKey.value = row.id?.toString() ?? "new";

    await nextTick();
    await openEditForm(row.id);
    editFormVisible.value = true;
  } catch (err: unknown) {
    reportError(err, `scheduleSlot.openEdit id=${row.id}`, "log");
  } finally {
    detailLoading.value[row.id] = false;
  }
};

const handleSaveEditForm = async (payload: Partial<any>) => {
  await saveEditForm(payload, "PUT");
  await fetchSchedule(currentPage.value || 1);
};

const handleCancelEditForm = () => cancelEditForm();

/* ---------------------- delete ---------------------- */
const deleteLoading = ref<Record<string | number, boolean>>({});

async function handleSoftDelete(row: AdminScheduleSlotData) {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to delete this schedule slot?",
      "Warning",
      { confirmButtonText: "Yes", cancelButtonText: "No", type: "warning" }
    );

    deleteLoading.value[row.id] = true;
    await adminApi.scheduleSlot.deleteScheduleSlot(row.id);

    const page = currentPage.value || 1;
    await fetchSchedule(page);

    if (page > 1 && (slots.value?.length ?? 0) === 0) {
      await fetchSchedule(page - 1);
    }
  } catch (err: any) {
    if (err === "cancel" || err === "close") return;
    reportError(err, `scheduleSlot.softDelete id=${row.id}`, "log");
  } finally {
    deleteLoading.value[row.id] = false;
  }
}

/* ---------------------- header stats ---------------------- */
const totalSlots = computed(() => totalRows.value ?? 0);

const { headerState: scheduleHeaderStats } = useHeaderState({
  items: [
    {
      key: "slots",
      getValue: () => totalSlots.value,
      singular: "slot",
      plural: "slots",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "view",
      getValue: () => (hasSelectedFilter.value ? 1 : 0),
      label: () =>
        viewMode.value === "class" ? "View: by class" : "View: by teacher",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});

/* ---------------------- pagination handlers ---------------------- */
const handleRefresh = async () => {
  await fetchSchedule(currentPage.value || 1);
};

const handlePageSizeChange = (size: number) => {
  prefs.setTablePageSize(size);
};

/* ---------------------- card header text ---------------------- */
const cardTitle = computed(() =>
  viewMode.value === "class" ? "Class schedule" : "Teacher schedule"
);

const cardDescription = computed(() =>
  hasSelectedFilter.value
    ? "Manage weekly schedule slots for the selected filter."
    : "Select a class or teacher to view the schedule."
);

const cardRightText = computed(() =>
  hasSelectedFilter.value ? `Total: ${totalRows.value ?? 0}` : ""
);

/* ---------------------- initial mount ---------------------- */
onMounted(async () => {
  if (viewMode.value === "teacher") await fetchTeacherOptions();
});
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="Schedule"
      description="View and manage weekly schedule by class or by teacher."
      :loading="tableLoading"
      :showRefresh="false"
      :stats="scheduleHeaderStats"
    >
      <template #filters>
        <div
          class="flex flex-col md:flex-row md:items-end md:justify-between gap-3 w-full"
        >
          <div class="flex flex-col gap-1">
            <span class="text-xs schedule-muted">View by:</span>
            <ElRadioGroup v-model="viewMode" size="small">
              <ElRadioButton label="class" class="mr-2">By Class</ElRadioButton>
              <ElRadioButton label="teacher" class="ml-2"
                >By Teacher</ElRadioButton
              >
            </ElRadioGroup>
          </div>

          <div class="flex flex-col gap-1 w-full md:w-auto md:max-w-xs">
            <span class="text-xs schedule-muted">
              {{ viewMode === "class" ? "Class:" : "Teacher:" }}
            </span>

            <ClassSelect
              v-if="viewMode === 'class'"
              v-model="selectedClassId"
              placeholder="Select class"
              class="w-full"
              clearable
            />

            <!-- Product-ready: TeacherSelect loads options internally on open.
                 We keep fetchTeacherOptions only for label map used by columns. -->
            <TeacherSelect
              v-else
              v-model="selectedTeacherId"
              placeholder="Select teacher"
              class="w-full"
              clearable
              @visible-change="(open: boolean) => open && fetchTeacherOptions()"
            />
          </div>
        </div>
      </template>

      <template #actions>
        <BaseButton
          plain
          :loading="tableLoading"
          :disabled="!hasSelectedFilter"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="handleRefresh"
        >
          Refresh
        </BaseButton>

        <BaseButton
          type="primary"
          :disabled="!hasSelectedFilter"
          @click="handleOpenCreateForm"
        >
          Add Slot
        </BaseButton>
      </template>
    </OverviewHeader>

    <TableCard
      :title="cardTitle"
      :description="cardDescription"
      :rightText="cardRightText"
      padding="16px"
    >
      <div v-if="tableLoading" class="py-4">
        <ElSkeleton :rows="4" animated />
      </div>

      <SmartTable
        v-if="showTable"
        :data="slots"
        :columns="scheduleColumns"
        :loading="tableLoading"
      >
        <template #subject="{ row }">
          <div class="flex items-center justify-between gap-3 w-full">
            <div class="min-w-0 flex items-center gap-2">
              <ElTag
                size="small"
                effect="plain"
                class="shrink-0"
                :type="row.subject_label ? 'success' : 'info'"
              >
                {{ row.subject_label ? "Assigned" : "None" }}
              </ElTag>

              <div class="min-w-0">
                <div class="truncate font-medium">
                  {{ row.subject_label || "—" }}
                </div>
                <div class="text-xs schedule-muted truncate">
                  {{ row.class_name }}
                </div>
              </div>
            </div>

            <BaseButton
              plain
              class="!px-2 !py-1 !text-xs shrink-0"
              :disabled="tableLoading"
              @click="() => handleOpenEditForm(row)"
            >
              Edit
            </BaseButton>
          </div>
        </template>

        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            detailContent="Edit schedule slot"
            deleteContent="Delete schedule slot"
            :detailLoading="detailLoading[row.id] ?? false"
            :deleteLoading="deleteLoading[row.id] ?? false"
            @detail="() => handleOpenEditForm(row)"
            @delete="() => handleSoftDelete(row)"
          />
        </template>
      </SmartTable>

      <div v-if="showEmptyState" class="py-10">
        <ElEmpty
          description="No schedule slots found for this selection."
          :image-size="100"
        >
          <BaseButton type="primary" @click="handleOpenCreateForm">
            Add first slot
          </BaseButton>
        </ElEmpty>
      </div>

      <div v-if="showInitialEmptyState" class="py-10">
        <ElEmpty
          description="Select a class or teacher to view the schedule."
          :image-size="100"
        />
      </div>

      <el-row v-if="showTable && totalRows > 0" justify="end" class="mt-4">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalRows"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="goPage"
          @size-change="handlePageSizeChange"
        />
      </el-row>
    </TableCard>

    <!-- CREATE -->
    <SmartFormDialog
      :key="viewMode + '-' + createDialogKey"
      v-model:visible="createFormVisible"
      v-model="createFormData"
      :fields="createFormSchema"
      title="Add Schedule Slot"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
    />
    <!-- EDIT -->
    <SmartFormDialog
      :key="editFormDataKey"
      v-model:visible="editFormVisible"
      v-model="editFormData"
      :fields="editFormSchema"
      title="Edit Schedule Slot"
      :loading="editFormLoading"
      @save="handleSaveEditForm"
      @cancel="handleCancelEditForm"
      :useElForm="true"
      :width="'520px'"
    />
  </div>
</template>

<style scoped>
.schedule-muted {
  color: var(--muted-color);
}
</style>
