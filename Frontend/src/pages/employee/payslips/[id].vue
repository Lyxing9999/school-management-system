<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  ElCard,
  ElDescriptions,
  ElDescriptionsItem,
  ElMessage,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type { PayslipDTO } from "~/api/hr_admin/payroll/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const route = useRoute();
const router = useRouter();
const payrollService = hrmsAdminService().payrollRun;

const loading = ref(false);
const payslip = ref<PayslipDTO | null>(null);

const payslipId = computed(() => String(route.params.id || ""));

function formatMoney(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "-";
  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
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

function statusTagType(
  status?: string | null,
): "success" | "warning" | "danger" | "info" {
  const key = String(status || "").toLowerCase();
  if (key === "paid") return "success";
  if (key === "generated" || key === "draft") return "warning";
  if (key === "rejected") return "danger";
  return "info";
}

async function fetchPayslipDetail() {
  if (!payslipId.value) return;

  loading.value = true;
  try {
    payslip.value = await payrollService.getPayslip(payslipId.value);
  } catch {
    ElMessage.error("Failed to load payslip detail or you do not have access.");
    router.push(ROUTES.EMPLOYEE.PAYSLIPS);
  } finally {
    loading.value = false;
  }
}

function refreshPage() {
  void fetchPayslipDetail();
}

onMounted(() => {
  void fetchPayslipDetail();
});
</script>

<template>
  <div class="employee-payslip-detail-page">
    <OverviewHeader
      title="Payslip Detail"
      :description="`Payslip ID: ${payslipId}`"
      :backPath="ROUTES.EMPLOYEE.PAYSLIPS"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="refreshPage"
          >Refresh</BaseButton
        >
      </template>
    </OverviewHeader>

    <el-card shadow="hover" v-loading="loading" class="detail-card">
      <template v-if="payslip">
        <div class="detail-head">
          <h3>{{ displayRelation(payslip.payroll_month, payslip.month) }}</h3>
          <el-tag :type="statusTagType(payslip.status)" effect="plain" round>
            {{ String(payslip.status || "-").toUpperCase() }}
          </el-tag>
        </div>

        <el-descriptions :column="2" border class="detail-grid">
          <el-descriptions-item label="Payslip ID">{{
            payslip.id
          }}</el-descriptions-item>
          <el-descriptions-item label="Payroll Run">{{
            displayRelation(payslip.payroll_run_label, payslip.payroll_run_id)
          }}</el-descriptions-item>

          <el-descriptions-item label="Employee">{{
            displayRelation(payslip.employee_name, payslip.employee_id)
          }}</el-descriptions-item>
          <el-descriptions-item label="Month">{{
            displayRelation(payslip.payroll_month, payslip.month)
          }}</el-descriptions-item>

          <el-descriptions-item label="Base Salary">{{
            formatMoney(payslip.base_salary)
          }}</el-descriptions-item>
          <el-descriptions-item label="Payable Working Days">{{
            payslip.payable_working_days
          }}</el-descriptions-item>

          <el-descriptions-item label="Paid Holiday Days">{{
            payslip.paid_holiday_days
          }}</el-descriptions-item>
          <el-descriptions-item label="Unpaid Leave Days">{{
            payslip.unpaid_leave_days
          }}</el-descriptions-item>

          <el-descriptions-item label="Total OT Hours">{{
            payslip.total_ot_hours
          }}</el-descriptions-item>
          <el-descriptions-item label="OT Payment">{{
            formatMoney(payslip.ot_payment)
          }}</el-descriptions-item>

          <el-descriptions-item label="Total Deductions">{{
            formatMoney(payslip.total_deductions)
          }}</el-descriptions-item>
          <el-descriptions-item label="Net Salary">
            <strong class="net-salary">{{
              formatMoney(payslip.net_salary)
            }}</strong>
          </el-descriptions-item>

          <el-descriptions-item label="Created At">{{
            formatDateTime(payslip.lifecycle?.created_at)
          }}</el-descriptions-item>
          <el-descriptions-item label="Updated At">{{
            formatDateTime(payslip.lifecycle?.updated_at)
          }}</el-descriptions-item>
        </el-descriptions>
      </template>

      <template v-else>
        <p class="empty-note">Payslip not found.</p>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.employee-payslip-detail-page {
  padding: 16px;
  max-width: 1100px;
  margin: 0 auto;
}

.detail-card {
  border-radius: 14px;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.detail-head h3 {
  margin: 0;
  color: #222730;
}

.detail-grid {
  margin-top: 6px;
}

.net-salary {
  color: #186a3b;
}

.empty-note {
  margin: 0;
  color: #7f8793;
}

@media (max-width: 768px) {
  .employee-payslip-detail-page {
    padding: 10px;
  }

  .detail-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
