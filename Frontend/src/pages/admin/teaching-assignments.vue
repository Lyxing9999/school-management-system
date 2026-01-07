<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { storeToRefs } from "pinia";

definePageMeta({ layout: "default" });

/* Base components */
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import SmartFormDialog from "~/components/form/SmartFormDialog.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import ActionButtons from "~/components/buttons/ActionButtons.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";

/* Selects */
import AdminClassSelect from "~/components/selects/class/ClassSelect.vue";

/* Element Plus */
import {
  ElEmpty,
  ElSkeleton,
  ElMessage,
  ElMessageBox,
  ElTag,
} from "element-plus";

/* Services */
import { adminService } from "~/api/admin";

/* Helpers */
import { reportError } from "~/utils/errors/errors";
import { formatDate } from "~/utils/date/formatDate";

/* Pagination + header stats */
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { useHeaderState } from "~/composables/ui/useHeaderState";

/* Preferences store (page size) */
import { usePreferencesStore } from "~/stores/preferencesStore";

/* Form schema */
import {
  teachingAssignmentFormSchema,
  type AdminAssignTeachingAssignmentForm,
} from "~/modules/forms/admin/teacher-assignment/teacherAssignment.schema";

/* ---------------- service ---------------- */
const api = adminService();

/* ---------------- prefs ---------------- */
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

/* ---------------- types ---------------- */
type AssignmentRow = {
  id: string;
  class_id: string;
  subject_id: string;
  teacher_id: string;

  subject_label?: string | null;
  teacher_name?: string | null;

  lifecycle?: {
    created_at?: string | null;
    updated_at?: string | null;
    deleted_at?: string | null;
  };
};

/* ---------------- selection ---------------- */
const selectedClassId = ref<string | null>(null);
const hasClassSelected = computed(() => !!selectedClassId.value);

/* ---------------- paginated fetch (client-side paging) ---------------- */
const {
  data: assignments,
  currentPage,
  pageSize,
  totalRows,
  initialLoading,
  fetching,
  fetchPage,
  goPage,
} = usePaginatedFetch<AssignmentRow, { classId: string | null }>(
  async (filter, page, size) => {
    const classId = filter?.classId;
    if (!classId) return { items: [], total: 0 };

    const res: any = await api.teachingAssignment.listForClass(
      classId,
      { show_deleted: "active" },
      { showError: false } as any
    );

    const items = (res?.items ?? []) as AssignmentRow[];

    // sort newest first
    const sorted = items.slice().sort((a, b) => {
      const ad = new Date(a?.lifecycle?.created_at ?? 0).getTime();
      const bd = new Date(b?.lifecycle?.created_at ?? 0).getTime();
      return bd - ad;
    });

    const total = sorted.length;
    const start = (page - 1) * size;
    const end = start + size;

    return { items: sorted.slice(start, end), total };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: computed(() => ({ classId: selectedClassId.value })),
  }
);

const tableLoading = computed(() => initialLoading.value || fetching.value);

/* ---------------- derived UI states ---------------- */
const showTable = computed(
  () =>
    hasClassSelected.value &&
    !tableLoading.value &&
    assignments.value.length > 0
);
const showEmptyState = computed(
  () =>
    hasClassSelected.value &&
    !tableLoading.value &&
    assignments.value.length === 0
);
const showInitialEmptyState = computed(
  () => !hasClassSelected.value && !tableLoading.value
);

/* ---------------- header stats ---------------- */
const { headerState } = useHeaderState({
  items: [
    {
      key: "assignments",
      getValue: () => totalRows.value ?? 0,
      singular: "assignment",
      plural: "assignments",
      variant: "primary",
      hideWhenZero: false,
    },
  ],
});

/* ---------------- dialog + form ---------------- */
const formDialogVisible = ref(false);
const formLoading = ref(false);

const formModel = ref<AdminAssignTeachingAssignmentForm>({
  class_id: "",
  subject_id: "",
  teacher_id: "",
  overwrite: true,
});

const formFields = computed(() => teachingAssignmentFormSchema.map((f) => f));

function openAssignDialog(row?: AssignmentRow) {
  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }

  formModel.value = {
    class_id: selectedClassId.value,
    subject_id: row?.subject_id ? String(row.subject_id) : "",
    teacher_id: row?.teacher_id ? String(row.teacher_id) : "",
    overwrite: true,
  };

  formDialogVisible.value = true;
}

function cancelDialog() {
  formDialogVisible.value = false;
}

async function saveDialog(payload: Partial<AdminAssignTeachingAssignmentForm>) {
  formModel.value = { ...formModel.value, ...payload };

  const classId = selectedClassId.value;
  if (!classId) return;

  if (!formModel.value.subject_id || !formModel.value.teacher_id) {
    ElMessage.warning("Subject and Teacher are required.");
    return;
  }

  formLoading.value = true;
  try {
    await api.teachingAssignment.assignForClass(
      classId,
      {
        subject_id: formModel.value.subject_id,
        teacher_id: formModel.value.teacher_id,
        overwrite: !!formModel.value.overwrite,
      },
      { showError: false, showSuccess: true } as any
    );

    formDialogVisible.value = false;
    await fetchPage(1);
  } catch (err: unknown) {
    reportError(err, "admin.teachingAssignments.assign", "log");
  } finally {
    formLoading.value = false;
  }
}

/* ---------------- unassign ---------------- */
async function unassign(row: AssignmentRow) {
  const classId = selectedClassId.value;
  if (!classId) return;

  try {
    await ElMessageBox.confirm("Unassign this subject teacher?", "Confirm", {
      type: "warning",
      confirmButtonText: "Yes",
      cancelButtonText: "No",
    });

    await api.teachingAssignment.unassignForClass(
      classId,
      { subject_id: String(row.subject_id) },
      { showError: false, showSuccess: true } as any
    );

    await fetchPage(currentPage.value || 1);
  } catch (err: any) {
    if (err === "cancel" || err === "close") return;
    reportError(err, "admin.teachingAssignments.unassign", "log");
  }
}

/* ---------------- table columns ---------------- */
function tagTypeForTeacher(v: any) {
  return v ? "success" : "info";
}

const columns = computed(() => [
  {
    label: "Subject",
    field: "subject_label",
    render: (row: AssignmentRow) => row.subject_label || row.subject_id,
  },
  {
    label: "Teacher",
    field: "teacher_name",
    render: (row: AssignmentRow) => ({
      component: ElTag,
      componentProps: {
        type: tagTypeForTeacher(row.teacher_name),
        effect: "plain",
        size: "small",
      },
      value: row.teacher_name || row.teacher_id || "Unassigned",
    }),
  },
  {
    label: "Created",
    field: "lifecycle.created_at",
    render: (row: AssignmentRow) => formatDate(row?.lifecycle?.created_at),
  },
  {
    label: "Updated",
    field: "lifecycle.updated_at",
    render: (row: AssignmentRow) => formatDate(row?.lifecycle?.updated_at),
  },
  {
    field: "id",
    operation: true,
    label: "Operation",
    align: "center",
    width: "220px",
    smartProps: {},
  },
]);

/* ---------------- actions ---------------- */
async function handleRefresh() {
  if (!selectedClassId.value) return;
  await fetchPage(1);
}

const handlePageSizeChange = (size: number) => {
  prefs.setTablePageSize(size);
};

/* ---------------- reactive: class change ---------------- */
watch(
  () => selectedClassId.value,
  async (cid) => {
    goPage(1);

    // close dialog when class changes (prevents wrong subject list)
    formDialogVisible.value = false;

    if (!cid) return;
    await fetchPage(1);
  },
  { immediate: true }
);
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="Teaching Assignments"
      description="Assign subject teachers per class. This controls who can grade."
      :loading="tableLoading"
      :showRefresh="false"
      :stats="headerState"
    >
      <template #filters>
        <div class="flex flex-col gap-1 w-full md:max-w-xs">
          <span class="text-xs muted">Class:</span>
          <AdminClassSelect
            v-model="selectedClassId"
            placeholder="Select class"
            class="w-full"
            clearable
          />
        </div>
      </template>

      <template #actions>
        <BaseButton
          plain
          :loading="tableLoading"
          :disabled="!hasClassSelected"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="handleRefresh"
        >
          Refresh
        </BaseButton>

        <BaseButton
          type="primary"
          :disabled="!hasClassSelected"
          @click="openAssignDialog()"
        >
          Assign Subject Teacher
        </BaseButton>
      </template>
    </OverviewHeader>

    <TableCard
      title="Assignments"
      description="One subject can have one teacher per class (overwrite supported)."
      :rightText="hasClassSelected ? `Total: ${totalRows ?? 0}` : ''"
      padding="16px"
    >
      <div v-if="tableLoading" class="py-4">
        <ElSkeleton :rows="4" animated />
      </div>

      <SmartTable
        v-if="showTable"
        :data="assignments"
        :columns="columns"
        :loading="tableLoading"
      >
        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            detailContent="Change teacher"
            deleteContent="Unassign"
            @detail="() => openAssignDialog(row)"
            @delete="() => unassign(row)"
          />
        </template>
      </SmartTable>

      <div v-if="showEmptyState" class="py-10">
        <ElEmpty
          description="No teaching assignments for this class."
          :image-size="100"
        >
          <BaseButton type="primary" @click="openAssignDialog()">
            Assign first subject teacher
          </BaseButton>
        </ElEmpty>
      </div>

      <div v-if="showInitialEmptyState" class="py-10">
        <ElEmpty
          description="Select a class to manage teaching assignments."
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

    <SmartFormDialog
      v-model:visible="formDialogVisible"
      v-model="formModel"
      :fields="formFields"
      title="Assign Subject Teacher"
      :loading="formLoading"
      :width="'520px'"
      @save="saveDialog"
      @cancel="cancelDialog"
      :useElForm="true"
    />
  </div>
</template>

<style scoped>
.muted {
  color: var(--muted-color);
}
</style>
