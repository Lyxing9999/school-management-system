<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from "vue";

definePageMeta({ layout: "admin" });

import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";

import {
  ElOption,
  ElSelect,
  ElRadioGroup,
  ElRadioButton,
  ElEmpty,
  ElSkeleton,
} from "element-plus";

import { adminService } from "~/api/admin";
import type { AdminScheduleSlotDataDTO } from "~/api/admin/schedule/dto";
import type {
  AdminClassDataDTO,
  AdminClassListDTO,
} from "~/api/admin/class/dto";

import { useLabelMap } from "~/composables/common/useLabelMap";
import { createScheduleColumns } from "~/tables/columns/admin/scheduleColumns";
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
} from "~/forms/dynamic/useAdminForms";

const adminApi = adminService();

/* ---------------------- mode ---------------------- */

const viewMode = ref<"class" | "teacher">("class");

/* ---------------------- state ---------------------- */

const selectedClassId = ref<string>("");
const selectedTeacherId = ref<string>("");

const slots = ref<AdminScheduleSlotDataDTO[]>([]);
const tableLoading = ref(false);

const filteredSlots = computed(() => slots.value);

/* ---------------------- filters / visibility ---------------------- */

const hasSelectedFilter = computed(
  () =>
    (viewMode.value === "class" && !!selectedClassId.value) ||
    (viewMode.value === "teacher" && !!selectedTeacherId.value)
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
    const res: any = await adminApi.staff.getTeacherSelect();
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

const handleSaveCreateForm = (payload: Partial<any>) => {
  saveCreateForm(payload);
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

const handleOpenEditForm = async (row: AdminScheduleSlotDataDTO) => {
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
async function handleDeleteSlot(row: AdminScheduleSlotDataDTO) {
  deleteLoading.value[row.id] = true;
  try {
    await adminApi.scheduleSlot.deleteScheduleSlot(row.id);
    await fetchSchedule();
  } finally {
    deleteLoading.value[row.id] = false;
  }
}

/* ---------------------- schedule fetch ---------------------- */

async function fetchSchedule() {
  if (!hasSelectedFilter.value) return;

  tableLoading.value = true;
  try {
    if (viewMode.value === "class") {
      const res = await adminApi.scheduleSlot.getClassSchedule(
        selectedClassId.value
      );
      slots.value = res.items ?? [];
    } else {
      const res = await adminApi.scheduleSlot.getTeacherSchedule(
        selectedTeacherId.value
      );
      slots.value = res.items ?? [];
    }
  } finally {
    tableLoading.value = false;
  }
}

/* ---------------------- lifecycle ---------------------- */

onMounted(async () => {
  await Promise.all([fetchClassOptions(), fetchTeacherOptions()]);
  await fetchSchedule();
});

/* ---------------------- watch: viewMode / filters ---------------------- */

watch(viewMode, async (newMode) => {
  slots.value = [];

  if (newMode === "class") {
    if (classOptions.value.length === 0) {
      await fetchClassOptions();
    }
    selectedTeacherId.value = "";
  } else {
    if (teacherOptions.value.length === 0) {
      await fetchTeacherOptions();
    }
    selectedClassId.value = "";
  }

  await fetchSchedule();
});

watch([selectedClassId, selectedTeacherId], async () => {
  if (hasSelectedFilter.value) {
    await fetchSchedule();
  }
});
</script>

<template>
  <el-row class="m-2" justify="space-between">
    <el-col :span="6">
      <ElRadioGroup v-model="viewMode">
        <ElRadioButton label="class" class="mr-2">By Class</ElRadioButton>
        <ElRadioButton label="teacher" class="ml-2">By Teacher</ElRadioButton>
      </ElRadioGroup>

      <ElSelect
        v-if="viewMode === 'class'"
        v-model="selectedClassId"
        placeholder="Select class"
        filterable
        class="mt-6 w-full"
        clearable
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
        class="mt-6 w-full"
        clearable
        :loading="optionsLoading.teachers"
        @visible-change="(open: boolean) => open && fetchTeacherOptions()"
      />
    </el-col>

    <el-col :span="12" class="text-right">
      <BaseButton
        type="default"
        :loading="tableLoading"
        :disabled="!hasSelectedFilter"
        @click="fetchSchedule"
      >
        Refresh
      </BaseButton>

      <BaseButton
        type="primary"
        class="ml-2"
        :disabled="!hasSelectedFilter"
        @click="handleOpenCreateForm"
      >
        Add Slot
      </BaseButton>
    </el-col>
  </el-row>

  <div class="mx-2 mt-4 p-4 bg-white rounded-lg shadow-sm">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <h2 class="text-base font-medium">
          {{ viewMode === "class" ? "Class Schedule" : "Teacher Schedule" }}
        </h2>
        <p class="text-xs text-gray-500 mt-1">
          {{
            viewMode === "class"
              ? "Select a class to view and manage its weekly schedule."
              : "Select a teacher to view and manage their weekly schedule."
          }}
        </p>
      </div>
    </div>

    <div v-if="tableLoading" class="py-4">
      <ElSkeleton :rows="4" animated />
    </div>

    <ErrorBoundary>
      <template #="defaults">
        <SmartTable
          v-if="showTable"
          :data="filteredSlots"
          :columns="scheduleColumns"
          :loading="false"
        >
          <template #operation="{ row }">
            <ActionButtons
              :rowId="row.id"
              detailContent="Edit Schedule Slot"
              deleteContent="Delete schedule slot"
              :detailLoading="detailLoading[row.id] ?? false"
              :deleteLoading="deleteLoading[row.id] ?? false"
              @detail="() => handleOpenEditForm(row)"
              @delete="() => handleDeleteSlot(row)"
            />
          </template>
        </SmartTable>
      </template>
    </ErrorBoundary>

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
  <ErrorBoundary>
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
  </ErrorBoundary>
</template>
