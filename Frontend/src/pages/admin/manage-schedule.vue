<script setup lang="ts">
import { ref, computed, onMounted, h } from "vue";

definePageMeta({
  layout: "admin",
});

// --------------------
// Base Components
// --------------------
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";

// Element Plus components
import {
  ElInput,
  ElOption,
  ElSelect,
  ElTimeSelect,
  ElRadioGroup,
  ElRadioButton,
} from "element-plus";

// --------------------
// Services & Types
// --------------------
import { adminService } from "~/api/admin";
import type {
  AdminScheduleSlotDataDTO,
  AdminCreateScheduleSlotDTO,
  AdminUpdateScheduleSlotDTO,
  AdminScheduleListDTO,
} from "~/api/admin/schedule/dto";
import type {
  AdminClassDataDTO,
  AdminClassListDTO,
} from "~/api/admin/class/dto";

const adminApi = adminService();

/* ---------------------- state ---------------------- */

// view mode: show schedule by class OR by teacher
const mode = ref<"class" | "teacher">("class");

// currently selected filter
const selectedClassId = ref<string>("");
const selectedTeacherId = ref<string>("");

const slots = ref<AdminScheduleSlotDataDTO[]>([]);
const tableLoading = ref(false);

// day labels (1-7)
const dayOfWeekLabels = ["", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const filteredSlots = computed(() => slots.value);

/* ---------------------- dropdown options ---------------------- */

const classOptions = ref<{ value: string; label: string }[]>([]);
const teacherOptions = ref<{ value: string; label: string }[]>([]);
const optionsLoading = ref({
  classes: false,
  teachers: false,
});

// quick map for displaying class / teacher names instead of raw id
const classLabelMap = computed<Record<string, string>>(() =>
  classOptions.value.reduce((acc, c) => {
    acc[c.value] = c.label;
    return acc;
  }, {} as Record<string, string>)
);

const teacherLabelMap = computed<Record<string, string>>(() =>
  teacherOptions.value.reduce((acc, t) => {
    acc[t.value] = t.label;
    return acc;
  }, {} as Record<string, string>)
);

async function fetchClassOptions() {
  if (classOptions.value.length > 0) return;
  optionsLoading.value.classes = true;
  try {
    const res: AdminClassListDTO | undefined =
      await adminApi.class.getClasses();
    const items: AdminClassDataDTO[] = res?.items ?? [];
    classOptions.value = items.map((c) => ({
      value: c.id,
      label: c.name,
    }));
  } catch (err) {
    console.error("Failed to load class options", err);
  } finally {
    optionsLoading.value.classes = false;
  }
}

async function fetchTeacherOptions() {
  if (teacherOptions.value.length > 0) return;
  optionsLoading.value.teachers = true;
  try {
    // Adjust this to your real staff endpoint
    const res: any = await adminApi.staff.getTeacherSelect();
    const items = res?.items ?? [];

    teacherOptions.value = items
      .filter((s: any) => s.role === "teacher" || s.role === "academic")
      .map((t: any) => ({
        value: t.id,
        label: t.full_name ?? `${t.first_name} ${t.last_name ?? ""}`,
      }));
  } catch (err) {
    console.error("Failed to load teacher options", err);
  } finally {
    optionsLoading.value.teachers = false;
  }
}

/* ---------------------- table columns (read-only) ---------------------- */

const scheduleColumns = computed(
  () =>
    [
      {
        label: "Day",
        field: "day_of_week",
        align: "center",
        width: "80px",
        render: (row: AdminScheduleSlotDataDTO) =>
          h("span", dayOfWeekLabels[row.day_of_week] ?? row.day_of_week),
      },
      {
        label: "Time",
        field: "start_time",
        align: "center",
        minWidth: "160px",
        render: (row: AdminScheduleSlotDataDTO) =>
          h(
            "span",
            `${row.start_time?.slice(0, 5)} - ${row.end_time?.slice(0, 5)}`
          ),
      },
      {
        label: "Room",
        field: "room",
        align: "center",
        minWidth: "100px",
      },
      {
        label: "Class",
        field: "class_id",
        align: "left",
        minWidth: "160px",
        render: (row: AdminScheduleSlotDataDTO) =>
          h("span", classLabelMap.value[row.class_id] ?? row.class_id),
      },
      {
        label: "Teacher",
        field: "teacher_id",
        align: "left",
        minWidth: "180px",
        render: (row: AdminScheduleSlotDataDTO) =>
          h("span", teacherLabelMap.value[row.teacher_id] ?? row.teacher_id),
      },
      {
        label: "Actions",
        slotName: "operation",
        operation: true,
        fixed: "right",
        width: "160",
        align: "center",
      },
    ] as const
);

/* ---------------------- create form state ---------------------- */

const createDialogVisible = ref(false);
const createFormLoading = ref(false);

const createFormData = ref<AdminCreateScheduleSlotDTO>({
  class_id: "",
  teacher_id: "",
  day_of_week: 1,
  start_time: "08:00:00",
  end_time: "09:00:00",
  room: "",
});

/* ---------------------- edit form state ---------------------- */

const editDialogVisible = ref(false);
const editFormLoading = ref(false);
const editingSlotId = ref<string | null>(null);

const editFormData = ref<AdminUpdateScheduleSlotDTO>({
  day_of_week: 1,
  start_time: "08:00:00",
  end_time: "09:00:00",
  room: "",
});

/* ---------------------- form fields (SmartFormDialog) ---------------------- */

const dayOptions = [
  { value: 1, label: "Monday" },
  { value: 2, label: "Tuesday" },
  { value: 3, label: "Wednesday" },
  { value: 4, label: "Thursday" },
  { value: 5, label: "Friday" },
  { value: 6, label: "Saturday" },
  { value: 7, label: "Sunday" },
];

/**
 * Create form:
 * - if mode = "class"   → class is taken from selectedClassId, user only picks teacher + time
 * - if mode = "teacher" → teacher is from selectedTeacherId, user only picks class + time
 */
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";
const createFormFields = computed(() => {
  const fields: any[] = [];

  if (mode.value === "teacher") {
    // choose class, teacher comes from top filter
    fields.push({
      key: "class_id",
      label: "Class",
      component: ElSelect,
      childComponent: ElOption,
      formItemProps: {
        required: true,
        prop: "class_id",
        label: "Class",
      },
      componentProps: {
        placeholder: "Select class",
        filterable: true,
        clearable: false,
        loading: optionsLoading.value.classes,
      },
      childComponentProps: {
        options: () => classOptions.value,
        valueKey: "value",
        labelKey: "label",
      },
    });
  }

  if (mode.value === "class") {
    // choose teacher, class comes from top filter
    fields.push({
      key: "teacher_id",
      label: "Teacher",
      component: TeacherSelect,
      formItemProps: {
        required: true,
        prop: "teacher_id",
        label: "Teacher",
      },
      componentProps: {
        placeholder: "Select teacher",
        clearable: true,
      },
    });
  }

  fields.push(
    {
      key: "day_of_week",
      label: "Day of Week",
      component: ElSelect,
      childComponent: ElOption,
      formItemProps: {
        required: true,
        prop: "day_of_week",
        label: "Day of Week",
      },
      componentProps: {
        placeholder: "Select day",
      },
      childComponentProps: {
        options: () => dayOptions,
        valueKey: "value",
        labelKey: "label",
      },
    },
    {
      key: "start_time",
      label: "Start Time",
      component: ElTimeSelect,
      formItemProps: {
        required: true,
        prop: "start_time",
        label: "Start Time",
      },
      componentProps: {
        start: "07:00",
        step: "00:30",
        end: "18:00",
        placeholder: "Start time",
      },
    },
    {
      key: "end_time",
      label: "End Time",
      component: ElTimeSelect,
      formItemProps: {
        required: true,
        prop: "end_time",
        label: "End Time",
      },
      componentProps: {
        start: "07:00",
        step: "00:30",
        end: "18:00",
        placeholder: "End time",
      },
    },
    {
      key: "room",
      label: "Room",
      component: ElInput,
      formItemProps: {
        required: false,
        prop: "room",
        label: "Room",
      },
      componentProps: {
        placeholder: "Room (optional)",
        clearable: true,
      },
    }
  );

  return fields;
});

/**
 * Edit form: only day/time/room (no class/teacher change here)
 */
const editFormFields = computed(() => [
  {
    key: "day_of_week",
    label: "Day of Week",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      required: true,
      prop: "day_of_week",
      label: "Day of Week",
    },
    componentProps: {
      placeholder: "Select day",
    },
    childComponentProps: {
      options: () => dayOptions,
      valueKey: "value",
      labelKey: "label",
    },
  },
  {
    key: "start_time",
    label: "Start Time",
    component: ElTimeSelect,
    formItemProps: {
      required: true,
      prop: "start_time",
      label: "Start Time",
    },
    componentProps: {
      start: "07:00",
      step: "00:30",
      end: "18:00",
      placeholder: "Start time",
    },
  },
  {
    key: "end_time",
    label: "End Time",
    component: ElTimeSelect,
    formItemProps: {
      required: true,
      prop: "end_time",
      label: "End Time",
    },
    componentProps: {
      start: "07:00",
      step: "00:30",
      end: "18:00",
      placeholder: "End time",
    },
  },
  {
    key: "room",
    label: "Room",
    component: ElInput,
    formItemProps: {
      required: false,
      prop: "room",
      label: "Room",
    },
    componentProps: {
      placeholder: "Room (optional)",
      clearable: true,
    },
  },
]);

const createDialogWidth = computed(() => "45%");
const editDialogWidth = computed(() => "40%");

/* ---------------------- fetch schedule ---------------------- */

async function fetchSchedule() {
  console.log(mode.value, selectedClassId.value, selectedTeacherId.value);
  if (mode.value === "class" && !selectedClassId.value) return;
  if (mode.value === "teacher" && !selectedTeacherId.value) return;
  console.log(mode.value, selectedClassId.value, selectedTeacherId.value);
  tableLoading.value = true;
  try {
    let res: AdminScheduleListDTO | AdminScheduleSlotDataDTO[] | undefined;

    if (mode.value === "class") {
      res = await adminApi.scheduleSlot.getClassSchedule(selectedClassId.value);
      console.log(res);
    } else {
      res = await adminApi.scheduleSlot.getTeacherSchedule(
        selectedTeacherId.value
      );
      console.log(res);
    }

    const items = Array.isArray(res)
      ? res
      : Array.isArray(res?.items)
      ? res.items
      : [];

    slots.value = items;
  } catch (err) {
    console.error("Failed to fetch schedule", err);
  } finally {
    tableLoading.value = false;
  }
}

/* ---------------------- create ---------------------- */

async function openCreateDialog() {
  await Promise.all([fetchClassOptions(), fetchTeacherOptions()]);

  createFormData.value = {
    class_id: mode.value === "class" ? selectedClassId.value || "" : "",
    teacher_id: mode.value === "teacher" ? selectedTeacherId.value || "" : "",
    day_of_week: 1,
    start_time: "08:00:00",
    end_time: "09:00:00",
    room: "",
  };
  createDialogVisible.value = true;
}

async function handleSaveCreateForm(
  payload: Partial<AdminCreateScheduleSlotDTO>
) {
  createFormLoading.value = true;
  try {
    const dataToSend: AdminCreateScheduleSlotDTO = {
      class_id:
        mode.value === "class"
          ? selectedClassId.value
          : payload.class_id ?? createFormData.value.class_id,
      teacher_id:
        mode.value === "teacher"
          ? selectedTeacherId.value
          : payload.teacher_id ?? createFormData.value.teacher_id,
      day_of_week: payload.day_of_week ?? createFormData.value.day_of_week,
      start_time: payload.start_time ?? createFormData.value.start_time,
      end_time: payload.end_time ?? createFormData.value.end_time,
      room: payload.room ?? createFormData.value.room ?? "",
    };

    await adminApi.scheduleSlot.createScheduleSlot(dataToSend);
    createDialogVisible.value = false;
    await fetchSchedule();
  } catch (err) {
    console.error("Failed to create schedule slot", err);
  } finally {
    createFormLoading.value = false;
  }
}

function handleCancelCreateForm() {
  createDialogVisible.value = false;
}

/* ---------------------- edit ---------------------- */

function openEditDialog(row: AdminScheduleSlotDataDTO) {
  editingSlotId.value = row.id;
  editFormData.value = {
    day_of_week: row.day_of_week,
    start_time: row.start_time,
    end_time: row.end_time,
    room: row.room ?? "",
  };
  editDialogVisible.value = true;
}

async function handleSaveEditForm(
  payload: Partial<AdminUpdateScheduleSlotDTO>
) {
  if (!editingSlotId.value) return;

  editFormLoading.value = true;
  try {
    const dataToSend: AdminUpdateScheduleSlotDTO = {
      day_of_week: payload.day_of_week ?? editFormData.value.day_of_week,
      start_time: payload.start_time ?? editFormData.value.start_time,
      end_time: payload.end_time ?? editFormData.value.end_time,
      room: payload.room ?? editFormData.value.room ?? "",
    };

    await adminApi.scheduleSlot.updateScheduleSlot(
      editingSlotId.value,
      dataToSend
    );
    editDialogVisible.value = false;
    await fetchSchedule();
  } catch (err) {
    console.error("Failed to update schedule slot", err);
  } finally {
    editFormLoading.value = false;
  }
}

function handleCancelEditForm() {
  editDialogVisible.value = false;
}

/* ---------------------- delete ---------------------- */

async function handleDeleteSlot(row: AdminScheduleSlotDataDTO) {
  try {
    await adminApi.scheduleSlot.deleteScheduleSlot(row.id);
    await fetchSchedule();
  } catch (err) {
    console.error("Failed to delete schedule slot", err);
  }
}

/* ---------------------- lifecycle ---------------------- */

onMounted(() => {
  fetchClassOptions();
  fetchTeacherOptions();
});
</script>

<template>
  <el-row class="m-2" justify="space-between">
    <el-col :span="6">
      <ElRadioGroup v-model="mode">
        <ElRadioButton label="class">By Class</ElRadioButton>
        <ElRadioButton label="teacher">By Teacher</ElRadioButton>
      </ElRadioGroup>

      <ElSelect
        v-if="mode === 'class'"
        v-model="selectedClassId"
        placeholder="Select class"
        filterable
        class="mt-6"
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
        filterable
        class="mt-6"
        clearable
        :loading="optionsLoading.teachers"
        @visible-change="(open) => open && fetchTeacherOptions()"
      />
    </el-col>

    <el-col :span="12" class="text-right">
      <BaseButton type="default" :loading="tableLoading" @click="fetchSchedule">
        Load Schedule
      </BaseButton>

      <BaseButton
        type="primary"
        class="ml-2"
        :disabled="
          (mode === 'class' && !selectedClassId) ||
          (mode === 'teacher' && !selectedTeacherId)
        "
        @click="openCreateDialog"
      >
        Add Slot
      </BaseButton>
    </el-col>
  </el-row>

  <ErrorBoundary>
    <SmartTable
      :data="filteredSlots"
      :columns="scheduleColumns"
      :loading="tableLoading"
    >
      <template #operation="{ row }">
        <BaseButton size="small" @click="openEditDialog(row)">
          Edit
        </BaseButton>
        <BaseButton
          size="small"
          type="danger"
          class="ml-1"
          @click="handleDeleteSlot(row)"
        >
          Delete
        </BaseButton>
      </template>
    </SmartTable>
  </ErrorBoundary>

  <!-- CREATE DIALOG -->
  <ErrorBoundary>
    <SmartFormDialog
      v-model:visible="createDialogVisible"
      v-model="createFormData"
      :fields="createFormFields"
      title="Add Schedule Slot"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createDialogWidth"
    />
  </ErrorBoundary>

  <!-- EDIT DIALOG -->
  <ErrorBoundary>
    <SmartFormDialog
      v-model:visible="editDialogVisible"
      v-model="editFormData"
      :fields="editFormFields"
      title="Edit Schedule Slot"
      :loading="editFormLoading"
      @save="handleSaveEditForm"
      @cancel="handleCancelEditForm"
      :useElForm="true"
      :width="editDialogWidth"
    />
  </ErrorBoundary>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
