<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  ElCard,
  ElDatePicker,
  ElDrawer,
  ElInput,
  ElOption,
  ElPagination,
  ElSelect,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import PageToolbar from "~/components/page-toolbar/PageToolbar.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";
import { hrmsAdminService } from "~/api/hr_admin";
import type { AuditLogDTO } from "~/api/hr_admin/audit";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

const MONGO_OBJECT_ID_REGEX = /^[a-f0-9]{24}$/i;

const props = defineProps<{
  title: string;
  description: string;
  backPath: string;
}>();

const auditService = hrmsAdminService().auditLog;

const loading = ref(false);
const rows = ref<AuditLogDTO[]>([]);
const totalRows = ref(0);

const pagination = reactive({
  page: 1,
  limit: 20,
});

const filters = reactive({
  q: "",
  entity_type: "",
  action: "",
  start_date: "",
  end_date: "",
});

const detailsDrawerVisible = ref(false);
const selected = ref<AuditLogDTO | null>(null);

const entityTypeOptions = [
  { label: "All Entities", value: "" },
  { label: "Attendance", value: "attendance" },
  { label: "Employee", value: "employee" },
  { label: "Leave Request", value: "leave" },
  { label: "Overtime Request", value: "overtime" },
  { label: "Payroll Run", value: "payroll_run" },
  { label: "Payslip", value: "payslip" },
  { label: "Work Location", value: "work_location" },
  { label: "Working Schedule", value: "working_schedule" },
  { label: "Public Holiday", value: "public_holiday" },
  { label: "Deduction Rule", value: "deduction_rule" },
];

const actionOptions = [
  { label: "All Actions", value: "" },
  { label: "Check In", value: "attendance_check_in" },
  { label: "Check Out", value: "attendance_check_out" },
  {
    label: "Wrong Location Approved",
    value: "attendance_wrong_location_approved",
  },
  {
    label: "Wrong Location Rejected",
    value: "attendance_wrong_location_rejected",
  },
  {
    label: "Early Leave Approved",
    value: "attendance_early_leave_approved",
  },
  {
    label: "Early Leave Rejected",
    value: "attendance_early_leave_rejected",
  },
  {
    label: "Marked Missing Check Out",
    value: "attendance_marked_missing_check_out",
  },
  { label: "Overtime Submitted", value: "ot_submitted" },
  { label: "Overtime Approved", value: "ot_approved" },
  { label: "Overtime Rejected", value: "ot_rejected" },
  { label: "Overtime Cancelled", value: "ot_cancelled" },
  { label: "Leave Submitted", value: "leave_submitted" },
  { label: "Leave Approved", value: "leave_approved" },
  { label: "Leave Rejected", value: "leave_rejected" },
  { label: "Leave Cancelled", value: "leave_cancelled" },
  { label: "Payroll Generated", value: "payroll_generated" },
  { label: "Payroll Finalized", value: "payroll_finalized" },
  { label: "Payroll Marked Paid", value: "payroll_marked_paid" },
];

const columns: ColumnConfig<AuditLogDTO>[] = [
  {
    field: "action_at",
    label: "Action At",
    minWidth: "190px",
    visible: true,
    render: (row: AuditLogDTO) => formatDateTime(row.action_at),
  },
  {
    field: "entity_type",
    label: "Entity",
    minWidth: "140px",
    visible: true,
    render: (row: AuditLogDTO) => entityLabel(row.entity_type),
  },
  {
    field: "entity_name",
    label: "Record",
    minWidth: "220px",
    visible: true,
    render: (row: AuditLogDTO) =>
      displayRelation(row.entity_name, row.entity_id, "Record"),
  },
  {
    field: "action",
    label: "Action",
    minWidth: "180px",
    visible: true,
    slotName: "action",
  },
  {
    field: "actor_name",
    label: "Actor",
    minWidth: "170px",
    visible: true,
    render: (row: AuditLogDTO) =>
      displayRelation(row.actor_name, row.actor_id, "System"),
  },
  {
    field: "actor_email",
    label: "Actor Email",
    minWidth: "220px",
    visible: true,
    render: (row: AuditLogDTO) => String(row.actor_email || "-"),
  },
  {
    field: "id",
    label: "Details",
    width: "100px",
    operation: true,
    visible: true,
    slotName: "operation",
    fixed: "right",
  },
];

const filteredRows = computed(() => {
  const q = filters.q.trim().toLowerCase();
  if (!q) return rows.value;
  return rows.value.filter((row) => {
    const haystack = [
      row.action,
      row.entity_type,
      row.entity_name,
      row.actor_name,
      row.actor_email,
    ]
      .map((item) => String(item || ""))
      .join(" ")
      .toLowerCase();
    return haystack.includes(q);
  });
});

const summary = computed(() => {
  const actionSet = new Set(filteredRows.value.map((row) => row.action));
  const actorSet = new Set(
    filteredRows.value.map((row) => String(row.actor_id || "").trim()),
  );
  return {
    rows: filteredRows.value.length,
    actions: actionSet.size,
    actors: Array.from(actorSet).filter(Boolean).length,
  };
});

function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isMongoObjectId(value: unknown): boolean {
  const text = String(value ?? "").trim();
  return Boolean(text) && MONGO_OBJECT_ID_REGEX.test(text);
}

function detailLabel(key: string): string {
  const map: Record<string, string> = {
    employee_name: "Employee",
    account_name: "Account",
    account_email: "Account Email",
    manager_name: "Manager",
    created_by_name: "Created By",
    deleted_by_name: "Deleted By",
    generated_by_name: "Generated By",
    reviewed_by_name: "Reviewed By",
    early_leave_reviewed_by_name: "Early Leave Reviewed By",
    location_reviewed_by_name: "Location Reviewed By",
    schedule_name: "Schedule",
    work_location_name: "Work Location",
    location_name: "Location",
    payroll_month: "Payroll Month",
    payroll_run_label: "Payroll Run",
  };
  const normalized = String(key || "").trim().toLowerCase();
  if (map[normalized]) return map[normalized];
  return normalized
    .replace(/_/g, " ")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

function shouldHideDetailKey(details: Record<string, unknown>, key: string): boolean {
  const normalized = String(key || "").trim().toLowerCase();
  if (!normalized.endsWith("_id")) return false;

  const base = normalized.slice(0, -3);
  if (`${base}_name` in details) return true;
  if (base === "user" && ("account_name" in details || "account_email" in details)) return true;
  if (
    base === "payroll_run" &&
    ("payroll_run_label" in details || "payroll_month" in details)
  ) {
    return true;
  }
  return isMongoObjectId(details[key]);
}

function sanitizeNestedValue(value: unknown): unknown {
  if (value == null) return null;

  if (typeof value === "string") {
    const text = value.trim();
    if (!text || isMongoObjectId(text)) return null;
    return text;
  }

  if (Array.isArray(value)) {
    const items = value
      .map((item) => sanitizeNestedValue(item))
      .filter((item) => item != null);
    return items.length > 0 ? items : null;
  }

  if (isObjectRecord(value)) {
    const output: Record<string, unknown> = {};
    for (const [key, item] of Object.entries(value)) {
      if (String(key).trim().toLowerCase().endsWith("_id") && isMongoObjectId(item)) {
        continue;
      }
      const normalized = sanitizeNestedValue(item);
      if (normalized != null) output[key] = normalized;
    }
    return Object.keys(output).length > 0 ? output : null;
  }

  return value;
}

function formatDetailValue(value: unknown): string {
  if (value == null) return "-";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "-";
  if (typeof value === "string") {
    const text = value.trim();
    if (!text) return "-";
    if (isMongoObjectId(text)) return "-";
    return text;
  }
  if (Array.isArray(value)) {
    const joined = value.map((item) => formatDetailValue(item)).filter((item) => item !== "-").join(", ");
    return joined || "-";
  }
  if (isObjectRecord(value)) {
    const normalized = sanitizeNestedValue(value);
    if (!normalized) return "-";
    return JSON.stringify(normalized);
  }
  return String(value);
}

const selectedDetailEntries = computed(() => {
  const details = selected.value?.details;
  if (!isObjectRecord(details)) return [];

  return Object.keys(details)
    .filter((key) => !shouldHideDetailKey(details, key))
    .map((key) => ({
      key,
      label: detailLabel(key),
      value: formatDetailValue(details[key]),
    }))
    .filter((item) => item.value !== "-");
});

function toIsoRangeStart(dateText?: string): string | undefined {
  const text = String(dateText || "").trim();
  if (!text) return undefined;
  return `${text}T00:00:00.000Z`;
}

function toIsoRangeEnd(dateText?: string): string | undefined {
  const text = String(dateText || "").trim();
  if (!text) return undefined;
  return `${text}T23:59:59.999Z`;
}

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function entityLabel(value?: string | null): string {
  const text = String(value || "").trim().toLowerCase();
  const found = entityTypeOptions.find((item) => item.value === text);
  if (found?.label) return found.label;
  if (!text) return "Unknown";
  return text.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
}

function actionLabel(value?: string | null): string {
  const text = String(value || "").trim().toLowerCase();
  const found = actionOptions.find((item) => item.value === text);
  if (found?.label) return found.label;
  if (!text) return "Unknown";
  return text.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
}

function actionTagType(
  value?: string | null,
): "success" | "warning" | "danger" | "info" {
  const action = String(value || "").trim().toLowerCase();
  if (action.includes("approved") || action.includes("finalized") || action.includes("paid")) {
    return "success";
  }
  if (action.includes("rejected") || action.includes("deleted")) {
    return "danger";
  }
  if (action.includes("cancelled")) {
    return "warning";
  }
  return "info";
}

async function fetchLogs(
  page = pagination.page,
  limit = pagination.limit,
) {
  loading.value = true;
  try {
    const response = await auditService.getLogs({
      page,
      limit,
      entity_type: filters.entity_type || undefined,
      action: filters.action || undefined,
      start_at: toIsoRangeStart(filters.start_date),
      end_at: toIsoRangeEnd(filters.end_date),
    });
    rows.value = response.items ?? [];
    totalRows.value = Number(response.total ?? rows.value.length);
    pagination.page = Number(response.page ?? page);
    pagination.limit = Number(response.page_size ?? limit);
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchLogs(1, pagination.limit);
}

function resetFilters() {
  filters.q = "";
  filters.entity_type = "";
  filters.action = "";
  filters.start_date = "";
  filters.end_date = "";
  void applyFilters();
}

async function handlePageChange(page: number) {
  pagination.page = page;
  await fetchLogs(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchLogs(1, size);
}

function openDetails(row: AuditLogDTO) {
  selected.value = row;
  detailsDrawerVisible.value = true;
}

onMounted(async () => {
  await fetchLogs(1, pagination.limit);
});
</script>

<template>
  <div class="audit-page">
    <OverviewHeader
      :title="props.title"
      :description="props.description"
      :backPath="props.backPath"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="fetchLogs(pagination.page, pagination.limit)">
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <PageToolbar class="page-tool-bar">
      <template #left>
        <ElInput
          v-model="filters.q"
          clearable
          class="toolbar-search"
          placeholder="Search action, entity, actor"
        />
      </template>
      <template #right>
        <ElSelect
          v-model="filters.entity_type"
          class="toolbar-select"
          placeholder="Entity"
          @change="applyFilters"
        >
          <ElOption
            v-for="opt in entityTypeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </ElSelect>
        <ElSelect
          v-model="filters.action"
          filterable
          clearable
          class="toolbar-select"
          placeholder="Action"
          @change="applyFilters"
        >
          <ElOption
            v-for="opt in actionOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </ElSelect>
        <ElDatePicker
          v-model="filters.start_date"
          type="date"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          placeholder="Start date"
          class="toolbar-date"
        />
        <ElDatePicker
          v-model="filters.end_date"
          type="date"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          placeholder="End date"
          class="toolbar-date"
        />
        <BaseButton plain @click="applyFilters">Apply</BaseButton>
        <BaseButton
          plain
          :disabled="!filters.q && !filters.entity_type && !filters.action && !filters.start_date && !filters.end_date"
          @click="resetFilters"
        >
          Reset
        </BaseButton>
      </template>
    </PageToolbar>

    <div class="summary-strip">
      <ElTag effect="plain" class="summary-strip__tag">Rows: {{ summary.rows }}</ElTag>
      <ElTag type="info" effect="plain" class="summary-strip__tag">Actions: {{ summary.actions }}</ElTag>
      <ElTag type="success" effect="plain" class="summary-strip__tag">Actors: {{ summary.actors }}</ElTag>
    </div>

    <ElCard class="table-shell" shadow="never">
      <SmartTable
        :data="filteredRows"
        :columns="columns"
        :loading="loading"
        :has-fetched-once="true"
      >
        <template #action="{ row }">
          <ElTag :type="actionTagType(row.action)" effect="plain" size="small">
            {{ actionLabel(row.action) }}
          </ElTag>
        </template>
        <template #operation="{ row }">
          <BaseButton size="small" plain @click="openDetails(row)">View</BaseButton>
        </template>
      </SmartTable>

      <div v-if="totalRows > 0" class="pagination-wrap">
        <ElPagination
          :current-page="pagination.page"
          :page-size="pagination.limit"
          :total="totalRows"
          :page-sizes="[10, 20, 50, 100]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </ElCard>

    <ElDrawer
      v-model="detailsDrawerVisible"
      title="Audit Details"
      size="42%"
      :with-header="true"
    >
      <template v-if="selected">
        <div class="detail-row">
          <span>Action</span>
          <strong>{{ actionLabel(selected.action) }}</strong>
        </div>
        <div class="detail-row">
          <span>Entity</span>
          <strong>{{ entityLabel(selected.entity_type) }}</strong>
        </div>
        <div class="detail-row">
          <span>Record</span>
          <strong>{{
            displayRelation(selected.entity_name, selected.entity_id, "Record")
          }}</strong>
        </div>
        <div class="detail-row">
          <span>Actor</span>
          <strong>{{
            displayRelation(selected.actor_name, selected.actor_id, "System")
          }}</strong>
        </div>
        <div class="detail-row">
          <span>Action At</span>
          <strong>{{ formatDateTime(selected.action_at) }}</strong>
        </div>
        <div class="detail-json">
          <div class="detail-json__title">Details</div>
          <div v-if="selectedDetailEntries.length > 0" class="detail-kv-list">
            <div
              v-for="entry in selectedDetailEntries"
              :key="entry.key"
              class="detail-row detail-row--inner"
            >
              <span>{{ entry.label }}</span>
              <strong>{{ entry.value }}</strong>
            </div>
          </div>
          <div v-else class="detail-empty">No additional details.</div>

          <details class="detail-raw">
            <summary>Raw payload (debug)</summary>
            <pre>{{ JSON.stringify(selected.details ?? {}, null, 2) }}</pre>
          </details>
        </div>
      </template>
    </ElDrawer>
  </div>
</template>

<style scoped>
.audit-page {
  padding: 16px;
  max-width: 1460px;
  margin: 0 auto;
  color: var(--text-color, var(--el-text-color-primary));
}

.page-tool-bar {
  margin-block: 12px;
}

.toolbar-search {
  min-width: min(400px, 100%);
}

.toolbar-select {
  min-width: 180px;
}

.toolbar-date {
  width: 150px;
}

.summary-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.summary-strip__tag {
  border-radius: 999px;
}

.table-shell {
  border: 1px solid var(--border-color, var(--el-border-color-light));
  background: var(--color-card, var(--el-bg-color));
  box-shadow: var(--shadow-sm, 0 6px 16px rgba(16, 24, 40, 0.05));
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border-color, var(--el-border-color-light));
}

.detail-row span {
  color: var(--muted-color, var(--el-text-color-secondary));
}

.detail-row strong {
  text-align: right;
  word-break: break-word;
}

.detail-json {
  margin-top: 12px;
}

.detail-json__title {
  font-weight: 600;
  margin-bottom: 8px;
}

.detail-kv-list {
  border: 1px solid var(--border-color, var(--el-border-color-light));
  border-radius: 10px;
  background: color-mix(in srgb, var(--color-card, #fff) 96%, var(--color-bg, #f7f8fa) 4%);
}

.detail-row--inner {
  margin: 0 10px;
}

.detail-empty {
  color: var(--muted-color, var(--el-text-color-secondary));
  font-size: 13px;
  margin-bottom: 8px;
}

.detail-raw {
  margin-top: 10px;
}

.detail-raw summary {
  cursor: pointer;
  color: var(--muted-color, var(--el-text-color-secondary));
  font-size: 12px;
  user-select: none;
}

.detail-json pre {
  margin: 0;
  max-height: 48vh;
  overflow: auto;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid var(--border-color, var(--el-border-color-light));
  background: color-mix(in srgb, var(--color-card, #fff) 92%, var(--color-bg, #f7f8fa) 8%);
  color: var(--text-color, var(--el-text-color-primary));
}

@media (max-width: 920px) {
  .toolbar-date {
    width: 100%;
  }

  .pagination-wrap {
    justify-content: flex-start;
  }
}
</style>
