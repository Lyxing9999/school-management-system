<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from "vue";

definePageMeta({ layout: "admin" });

/* ------------------------------------
 * Base components
 * ---------------------------------- */
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";

/* ------------------------------------
 * Element Plus
 * ---------------------------------- */
import {
  ElOption,
  ElSelect,
  ElRadioGroup,
  ElRadioButton,
  ElEmpty,
  ElSkeleton,
  ElMessageBox,
} from "element-plus";

/* ------------------------------------
 * Services & types
 * ---------------------------------- */
import { adminService } from "~/api/admin";
import type { AdminScheduleSlotData } from "~/api/admin/schedule/schedule.dto";
import type {
  AdminClassDataDTO,
  AdminClassListDTO,
} from "~/api/admin/class/class.dto";

/* ------------------------------------
 * Helpers / columns / forms
 * ---------------------------------- */
import { useLabelMap } from "~/composables/common/useLabelMap";
import { createScheduleColumns } from "~/modules/tables/columns/admin/scheduleColumns";
import { reportError } from "~/utils/errors";
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
} from "~/form-system/useDynamicForm.ts/useAdminForms";
import { usePaginatedFetch } from "~/composables/usePaginatedFetch";
import { useHeaderState } from "~/composables/useHeaderState";

const adminApi = adminService();

/* ---------------------- mode ---------------------- */
const viewMode = ref<"class" | "teacher">("class");

/* ---------------------- selection state ---------------------- */
const selectedClassId = ref<string>("");
const selectedTeacherId = ref<string>("");

/* ---------------------- pagination filter model ---------------------- */
type ScheduleFilter = {
  mode: "class" | "teacher";
  classId?: string;
  teacherId?: string;
};

const scheduleFilter = ref<ScheduleFilter>({
  mode: "class",
  classId: "",
  teacherId: "",
});

// keep filter in sync with viewMode + selected IDs
watch(
  [viewMode, selectedClassId, selectedTeacherId],
  ([mode, classId, teacherId]) => {
    scheduleFilter.value = {
      mode,
      classId: classId || undefined,
      teacherId: teacherId || undefined,
    };
  },
  { immediate: true }
);

/* ---------------------- paginated fetch ---------------------- */
const {
  data: slots,
  loading: tableLoading,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<AdminScheduleSlotData, ScheduleFilter>(
  async (filter, page, pageSize, _signal) => {
    // no selection -> no fetch
    if (
      !filter ||
      (filter.mode === "class" && !filter.classId) ||
      (filter.mode === "teacher" && !filter.teacherId)
    ) {
      return { items: [], total: 0 };
    }

    if (filter.mode === "class") {
      const res = await adminApi.scheduleSlot.getClassSchedule(
        filter.classId as string
      );
      const allSlots = res?.items ?? [];
      const total = allSlots.length;
      const start = (page - 1) * pageSize;
      const items = allSlots.slice(start, start + pageSize);
      return { items, total };
    } else {
      const res = await adminApi.scheduleSlot.getTeacherSchedule(
        filter.teacherId as string
      );
      const allSlots = res?.items ?? [];
      const total = allSlots.length;
      const start = (page - 1) * pageSize;
      const items = allSlots.slice(start, start + pageSize);
      return { items, total };
    }
  },
  1,
  10,
  scheduleFilter
);

const filteredSlots = computed(() => slots.value);

/* ---------------------- filters / visibility ---------------------- */
const hasSelectedFilter = computed(
  () =>
    (scheduleFilter.value.mode === "class" && !!scheduleFilter.value.classId) ||
    (scheduleFilter.value.mode === "teacher" &&
      !!scheduleFilter.value.teacherId)
);

const showTable = computed(
  () =>
    hasSelectedFilter.value &&
    !tableLoading.value &&
    filteredSlots.value.length > 0
);

const showEmptyState = computed(
  () =>
    hasSelectedFilter.value &&
    !tableLoading.value &&
    filteredSlots.value.length === 0
);

const showInitialEmptyState = computed(
  () => !hasSelectedFilter.value && !tableLoading.value
);

/* ---------------------- dropdown options ---------------------- */
const classOptions = ref<{ value: string; label: string }[]>([]);
const teacherOptions = ref<{ value: string; label: string }[]>([]);
const optionsLoading = ref({ classes: false, teachers: false });

const teacherLabelMap = useLabelMap(teacherOptions);

async function fetchClassOptions() {
  optionsLoading.value.classes = true;
  try {
    const res: AdminClassListDTO | undefined =
      await adminApi.class.getClasses();
    const items: AdminClassDataDTO[] = res?.items ?? [];

    classOptions.value = items.map((c) => ({
      value: c.id,
      label: c.name,
    }));

    if (!selectedClassId.value && classOptions.value.length > 0) {
      selectedClassId.value = classOptions.value[0].value;
    }
  } finally {
    optionsLoading.value.classes = false;
  }
}

async function fetchTeacherOptions() {
  optionsLoading.value.teachers = true;
  try {
    const res: any = await adminApi.staff.listTeacherSelect();
    const items = res?.items ?? [];

    teacherOptions.value = items
      .filter((s: any) => s.role === "teacher" || s.role === "academic")
      .map((t: any) => ({
        value: t.id,
        label: t.full_name ?? `${t.first_name} ${t.last_name ?? ""}`,
      }));

    if (!selectedTeacherId.value && teacherOptions.value.length > 0) {
      selectedTeacherId.value = teacherOptions.value[0].value;
    }
  } finally {
    optionsLoading.value.teachers = false;
  }
}

/* ---------------------- columns ---------------------- */
const scheduleColumns = createScheduleColumns(teacherLabelMap);

/* ---------------------- dynamic create form ---------------------- */
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
  if (!hasSelectedFilter.value) return;

  createDialogKey.value++;

  if (viewMode.value === "class") {
    await openCreateForm({
      class_id: selectedClassId.value,
    });
  } else {
    await openCreateForm({
      teacher_id: selectedTeacherId.value,
    });
  }
};

watch(formEntity, () => {
  resetCreateFormData();
});

const handleSaveCreateForm = async (payload: Partial<any>) => {
  await saveCreateForm(payload);
  await fetchSchedule(1);
};

const handleCancelCreateForm = () => {
  cancelCreateForm();
};

/* ---------------------- dynamic edit form ---------------------- */
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
  } finally {
    detailLoading.value[row.id] = false;
  }
};

const handleSaveEditForm = (payload: Partial<any>) => {
  saveEditForm(payload, "PUT");
};

const handleCancelEditForm = () => {
  cancelEditForm();
};

/* ---------------------- delete ---------------------- */
const deleteLoading = ref<Record<string | number, boolean>>({});

async function handleSoftDelete(row: AdminScheduleSlotData) {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to delete this schedule slot?",
      "Warning",
      {
        confirmButtonText: "Yes",
        cancelButtonText: "No",
        type: "warning",
      }
    );

    deleteLoading.value[row.id] = true;
    await adminApi.scheduleSlot.deleteScheduleSlot(row.id);
    await fetchSchedule(currentPage.value || 1);
  } catch (err: any) {
    if (err === "cancel" || err === "close") return;

    reportError(err, `scheduleSlot.softDelete id=${row.id}`, "log");
  } finally {
    deleteLoading.value[row.id] = false;
  }
}

/* ---------------------- schedule fetch wrapper ---------------------- */
async function fetchSchedule(page: number = currentPage.value || 1) {
  if (!hasSelectedFilter.value) return;
  await fetchPage(page);
}

/* ---------------------- lifecycle ---------------------- */
onMounted(async () => {
  await Promise.all([fetchClassOptions(), fetchTeacherOptions()]);
  await fetchSchedule(1);
});

/* ---------------------- watch: viewMode / filters ---------------------- */
watch(viewMode, async (newMode) => {
  if (newMode === "class") {
    if (classOptions.value.length === 0) await fetchClassOptions();
    selectedTeacherId.value = "";
  } else {
    if (teacherOptions.value.length === 0) await fetchTeacherOptions();
    selectedClassId.value = "";
  }

  if (hasSelectedFilter.value) {
    await fetchSchedule(1);
  }
});

watch([selectedClassId, selectedTeacherId], async () => {
  if (hasSelectedFilter.value) {
    await fetchSchedule(1);
  }
});

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
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- OVERVIEW HEADER -->
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
          <!-- Mode toggle -->
          <div class="flex flex-col gap-1">
            <span class="text-xs schedule-muted">View by:</span>
            <ElRadioGroup v-model="viewMode" size="small">
              <ElRadioButton label="class" class="mr-2">By Class</ElRadioButton>
              <ElRadioButton label="teacher" class="ml-2"
                >By Teacher</ElRadioButton
              >
            </ElRadioGroup>
          </div>

          <!-- Selector -->
          <div class="flex flex-col gap-1 w-full md:w-auto md:max-w-xs">
            <span class="text-xs schedule-muted">
              {{ viewMode === "class" ? "Class:" : "Teacher:" }}
            </span>

            <ElSelect
              v-if="viewMode === 'class'"
              v-model="selectedClassId"
              placeholder="Select class"
              filterable
              clearable
              class="w-full"
              :loading="optionsLoading.classes"
              @visible-change="(open) => open && fetchClassOptions()"
            >
              <ElOption
                v-for="opt in classOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </ElSelect>

            <TeacherSelect
              v-else
              v-model="selectedTeacherId"
              placeholder="Select teacher"
              class="w-full"
              clearable
              :loading="optionsLoading.teachers"
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
          @click="() => fetchSchedule(currentPage || 1)"
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

    <!-- MAIN CARD (token-driven: works in light + dark) -->
    <div class="mx-0 md:mx-1 p-4 rounded-2xl schedule-surface">
      <!-- Small contextual label -->
      <div class="mb-3 flex items-center justify-between">
        <span
          class="text-xs font-medium uppercase tracking-wide schedule-muted"
        >
          {{ viewMode === "class" ? "Class schedule" : "Teacher schedule" }}
        </span>
      </div>

      <!-- Loading skeleton -->
      <div v-if="tableLoading" class="py-4">
        <ElSkeleton :rows="4" animated />
      </div>

      <!-- Table / states -->
      <el-card>
        <template #default>
          <SmartTable
            v-if="showTable"
            :data="filteredSlots"
            :columns="scheduleColumns"
            :loading="tableLoading"
          >
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
        </template>
      </el-card>

      <!-- Pagination -->
      <el-row v-if="showTable && totalRows > 0" justify="end" class="mt-4">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalRows"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="goPage"
          @size-change="
            (size: number) => {
              pageSize = size;
              fetchSchedule(1);
            }
          "
        />
      </el-row>

      <!-- Empty when selection has no data -->
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

      <!-- Initial state: nothing selected -->
      <div v-if="showInitialEmptyState" class="py-10">
        <ElEmpty
          description="Select a class or teacher, then click 'Refresh'."
          :image-size="100"
        />
      </div>
    </div>

    <!-- CREATE DIALOG -->
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

    <!-- EDIT DIALOG -->
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
    />
  </div>
</template>

<style scoped>
/* Token-driven card surface */
.schedule-surface {
  background: var(--color-card);
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 22px var(--card-shadow);
  color: var(--text-color);
}

/* Muted text aligned with your system */
.schedule-muted {
  color: var(--muted-color);
}

/* Your existing append padding */
:deep(.el-input-group__append) {
  padding: 0 10px;
}

/* Make inner el-card not fight your outer surface */
:deep(.el-card) {
  background: transparent;
  border: 1px solid color-mix(in srgb, var(--border-color) 70%, transparent);
  box-shadow: none;
}

:deep(.el-card__body) {
  background: transparent;
  padding: 12px;
}
</style>
