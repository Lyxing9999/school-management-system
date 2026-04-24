<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import {
  ElButton,
  ElCol,
  ElInput,
  ElMessageBox,
  ElOption,
  ElPagination,
  ElRow,
  ElSelect,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  OvertimeRequestDTO,
  OvertimeRequestListParams,
  OvertimeRequestStatus,
} from "~/api/hr_admin/overtime/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { overtimeColumns } from "~/modules/tables/columns/hr_admin/overtimeColumns";

definePageMeta({ layout: "default" });

const overtimeService = hrmsAdminService().overtimeRequest;

const loading = ref(false);
const rows = ref<OvertimeRequestDTO[]>([]);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  employee_id: string;
  status: OvertimeRequestStatus | undefined;
}>({
  employee_id: "",
  status: undefined,
});

const activeFilterBadge = computed(() => {
  return [Boolean(filters.employee_id.trim()), Boolean(filters.status)].filter(
    Boolean,
  ).length;
});

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): OvertimeRequestListParams {
  return {
    page,
    limit,
    employee_id: filters.employee_id.trim() || undefined,
    status: filters.status,
  };
}

async function fetchOvertimeRequests(
  page = pagination.page,
  limit = pagination.limit,
) {
  loading.value = true;
  try {
    const response = await overtimeService.getRequests(
      buildParams(page, limit),
    );
    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.limit ?? limit;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchOvertimeRequests(1, pagination.limit);
}

function resetFilters() {
  filters.employee_id = "";
  filters.status = undefined;
  applyFilters();
}

async function handlePageChange(page: number) {
  pagination.page = page;
  await fetchOvertimeRequests(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchOvertimeRequests(1, size);
}

function getStatusTagType(
  status: string,
): "warning" | "success" | "danger" | "info" {
  const typeMap: Record<string, "warning" | "success" | "danger" | "info"> = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
    cancelled: "info",
  };
  return typeMap[status] || "info";
}

function getStatusClass(status: string): string {
  const classMap: Record<string, string> = {
    pending: "status-pill status-pill--pending",
    approved: "status-pill status-pill--approved",
    rejected: "status-pill status-pill--rejected",
    cancelled: "status-pill status-pill--cancelled",
  };
  return classMap[status] || "status-pill";
}

async function showDetails(row: OvertimeRequestDTO) {
  await ElMessageBox.alert(
    `Employee: ${displayRelation(
      row.employee_name,
      row.employee_id,
    )}\nDate: ${
      row.request_date
    }\nStart: ${row.start_time}\nEnd: ${row.end_time}\nStatus: ${
      row.status
    }\nReason: ${row.reason}\nManager comment: ${row.manager_comment || "-"}`,
    "Overtime details",
    { type: "info" },
  );
}

import { onMounted } from "vue";
onMounted(() => {
  fetchOvertimeRequests(1, pagination.limit);
});
</script>

<template>
  <OverviewHeader
    :title="'Overtime Overview'"
    :description="'Review all overtime requests across employees'"
    :backPath="'/hr'"
  >
    <template #actions>
      <BaseButton
        plain
        :loading="loading"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="fetchOvertimeRequests(pagination.page, pagination.limit)"
      >
        Refresh
      </BaseButton>
    </template>
  </OverviewHeader>

  <el-row :gutter="12" class="mb-4">
    <el-col :xs="24" :sm="12" :md="8" :lg="6">
      <ElInput
        v-model="filters.employee_id"
        clearable
        placeholder="Filter by employee"
      />
    </el-col>

    <el-col :xs="24" :sm="12" :md="8" :lg="6">
      <ElSelect
        v-model="filters.status"
        clearable
        class="w-full"
        placeholder="Status"
      >
        <ElOption label="Pending" value="pending" />
        <ElOption label="Approved" value="approved" />
        <ElOption label="Rejected" value="rejected" />
        <ElOption label="Cancelled" value="cancelled" />
      </ElSelect>
    </el-col>

    <el-col :xs="24" :sm="24" :md="8" :lg="12">
      <div class="filter-actions">
        <BaseButton type="primary" :loading="loading" @click="applyFilters">
          Apply Filters
          <span v-if="activeFilterBadge" class="filter-badge">{{
            activeFilterBadge
          }}</span>
        </BaseButton>
        <BaseButton plain :disabled="loading" @click="resetFilters">
          Reset
        </BaseButton>
      </div>
    </el-col>
  </el-row>

  <SmartTable
    :columns="overtimeColumns"
    :data="rows"
    :loading="loading"
    :total="pagination.total"
    :page="pagination.page"
    :page-size="pagination.limit"
    @page="handlePageChange"
    @page-size="handlePageSizeChange"
  >
    <template #status="{ row }">
      <ElTag
        :type="getStatusTagType(row.status)"
        effect="plain"
        round
        size="small"
        :class="getStatusClass(row.status)"
      >
        {{ row.status.charAt(0).toUpperCase() + row.status.slice(1) }}
      </ElTag>
    </template>

    <template #operation="{ row }">
      <ElButton
        type="info"
        size="small"
        link
        @click="showDetails(row as OvertimeRequestDTO)"
      >
        View
      </ElButton>
    </template>
  </SmartTable>

  <el-row v-if="pagination.total > 0" justify="end" class="m-4">
    <ElPagination
      :current-page="pagination.page"
      :page-size="pagination.limit"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      background
      @current-change="handlePageChange"
      @size-change="handlePageSizeChange"
    />
  </el-row>
</template>

<style scoped>
.filter-actions {
  height: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-badge {
  margin-left: 6px;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 11px;
  line-height: 18px;
  background: color-mix(in srgb, var(--color-primary) 20%, white 80%);
}

.status-pill {
  font-weight: 600;
  letter-spacing: 0.01em;
}

.status-pill--pending {
  border-color: #e6a23c;
  color: #b88230;
  background: #fff8eb;
}

.status-pill--approved {
  border-color: #67c23a;
  color: #3b8f1d;
  background: #f1faec;
}

.status-pill--rejected {
  border-color: #f56c6c;
  color: #c74141;
  background: #fff2f2;
}

.status-pill--cancelled {
  border-color: #909399;
  color: #61656d;
  background: #f5f6f7;
}
</style>
