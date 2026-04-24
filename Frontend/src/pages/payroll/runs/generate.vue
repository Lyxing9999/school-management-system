<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import {
  ElButton,
  ElCard,
  ElCol,
  ElDatePicker,
  ElDescriptions,
  ElDescriptionsItem,
  ElForm,
  ElFormItem,
  ElRow,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type { PayrollRunGenerateResponseDTO } from "~/api/hr_admin/payroll";
import { ROUTES } from "~/constants/routes";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

definePageMeta({ layout: "default" });

const router = useRouter();
const payrollService = hrmsAdminService().payrollRun;

const formRef = ref<FormInstance>();
const submitting = ref(false);
const result = ref<PayrollRunGenerateResponseDTO | null>(null);

const form = reactive({
  month: "",
});

const rules: FormRules = {
  month: [
    {
      required: true,
      message: "Month is required",
      trigger: "change",
    },
    {
      pattern: /^\d{4}-\d{2}$/,
      message: "Month must be in YYYY-MM format",
      trigger: "change",
    },
  ],
};

const canSubmit = computed(() => Boolean(form.month));

const generatedRun = computed(() => result.value?.payroll_run ?? null);
const resultMeta = computed(() => result.value?.meta ?? null);

const formattedGeneratedAt = computed(() => {
  const value =
    generatedRun.value?.lifecycle?.created_at ?? result.value?.generated_at;
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
});

const generatedRunLabel = computed(() => {
  return displayRelation(
    generatedRun.value?.payroll_run_label ?? result.value?.payroll_run_label,
    generatedRun.value?.payroll_month ??
      generatedRun.value?.month ??
      result.value?.payroll_month ??
      result.value?.month ??
      form.month,
  );
});

const resultMonth = computed(() => {
  const value =
    generatedRun.value?.payroll_month ??
    generatedRun.value?.month ??
    result.value?.payroll_month ??
    result.value?.month ??
    form.month;
  return String(value ?? "").trim() || "-";
});

const resultStatus = computed(() => {
  const status = String(
    generatedRun.value?.status ?? result.value?.status ?? "",
  ).toLowerCase();
  if (!status) return "-";
  return status.toUpperCase();
});

const resultStatusTagType = computed<"warning" | "success" | "info">(() => {
  const status = String(
    generatedRun.value?.status ?? result.value?.status ?? "",
  ).toLowerCase();
  if (status === "draft") return "warning";
  if (status === "paid") return "success";
  return "info";
});

const resultStatusClass = computed(() => {
  const status = String(
    generatedRun.value?.status ?? result.value?.status ?? "",
  ).toLowerCase();
  if (status === "draft") return "status-pill status-pill--draft";
  if (status === "paid") return "status-pill status-pill--paid";
  return "status-pill status-pill--finalized";
});

const resultEmployeeCount = computed(() => {
  const value =
    resultMeta.value?.employee_count ?? result.value?.total_employees ?? 0;
  return Number(value);
});

const resultGeneratedCount = computed(() => {
  return Number(
    resultMeta.value?.generated_count ??
      result.value?.generated_count ??
      result.value?.payslips?.length ??
      0,
  );
});

const resultTotalAmount = computed(() => {
  const metaTotal = Number(
    resultMeta.value?.total_amount ?? result.value?.total_amount ?? NaN,
  );
  if (Number.isFinite(metaTotal)) return metaTotal;
  const payslipRows = result.value?.payslips ?? [];
  return payslipRows.reduce(
    (sum, row) => sum + Number(row?.net_salary ?? 0),
    0,
  );
});

function resetForm() {
  form.month = "";
  result.value = null;
  formRef.value?.clearValidate();
}

async function submitGenerate() {
  try {
    await formRef.value?.validate();
  } catch {
    return;
  }

  submitting.value = true;
  try {
    const data = await payrollService.generateRun({ month: form.month });
    result.value = data;
  } catch {
    // API notifications are handled by service layer
  } finally {
    submitting.value = false;
  }
}

function goToRuns() {
  void router.push(ROUTES.PAYROLL_MANAGER.PAYROLL_RUNS);
}

function goToPayslips() {
  void router.push(ROUTES.PAYROLL_MANAGER.PAYSLIPS);
}
</script>

<template>
  <OverviewHeader
    :title="'Generate Payroll Run'"
    :description="'Create a payroll run for a specific month using finalized attendance and payroll rules'"
    :backPath="'/payroll/runs'"
  >
    <template #actions>
      <BaseButton plain :disabled="submitting" @click="goToRuns">
        Back To Runs
      </BaseButton>
    </template>
  </OverviewHeader>

  <el-row :gutter="16" class="generate-layout">
    <el-col :xs="24" :lg="14">
      <ElCard shadow="never" class="generate-card">
        <template #header>
          <div class="generate-card__header">
            <h3 class="generate-card__title">Payroll Generation Form</h3>
            <p class="generate-card__subtitle">
              Select the payroll month and submit to generate a payroll run.
            </p>
          </div>
        </template>

        <ElForm
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent
        >
          <ElFormItem label="Payroll Month" prop="month">
            <ElDatePicker
              v-model="form.month"
              type="month"
              class="w-full"
              value-format="YYYY-MM"
              placeholder="Select month"
              :disabled="submitting"
            />
          </ElFormItem>

          <div class="form-actions">
            <BaseButton
              type="primary"
              :loading="submitting"
              :disabled="!canSubmit"
              @click="submitGenerate"
            >
              Generate Payroll
            </BaseButton>

            <BaseButton plain :disabled="submitting" @click="resetForm">
              Reset
            </BaseButton>
          </div>
        </ElForm>
      </ElCard>
    </el-col>

    <el-col :xs="24" :lg="10">
      <ElCard shadow="never" class="result-card">
        <template #header>
          <div class="result-card__header">
            <h3 class="result-card__title">Latest Result</h3>
          </div>
        </template>

        <div v-if="result">
          <ElDescriptions :column="1" border>
            <ElDescriptionsItem label="Payroll Run">
              {{ generatedRunLabel }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Month">
              {{ resultMonth }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Status">
              <ElTag
                :type="resultStatusTagType"
                effect="plain"
                round
                size="small"
                :class="resultStatusClass"
              >
                {{ resultStatus }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Total Employees">
              {{ resultEmployeeCount }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Generated Payslips">
              {{ resultGeneratedCount }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Total Amount">
              {{
                resultTotalAmount.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })
              }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Generated At">
              {{ formattedGeneratedAt }}
            </ElDescriptionsItem>
          </ElDescriptions>

          <div class="result-actions">
            <ElButton type="primary" plain @click="goToRuns">
              Open Runs
            </ElButton>
            <ElButton type="success" plain @click="goToPayslips">
              Open Payslips
            </ElButton>
          </div>
        </div>

        <div v-else class="result-empty">
          <p class="result-empty__title">No payroll run generated yet</p>
          <p class="result-empty__desc">
            Submit the form to generate a payroll run and preview output
            summary.
          </p>
        </div>
      </ElCard>
    </el-col>
  </el-row>
</template>

<style scoped>
.generate-layout {
  margin-top: 4px;
}

.generate-card__header,
.result-card__header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.generate-card__title,
.result-card__title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.generate-card__subtitle {
  margin: 0;
  color: var(--muted-color, var(--el-text-color-secondary));
  font-size: 13px;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.result-empty {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 6px;
  color: var(--muted-color, var(--el-text-color-secondary));
}

.result-empty__title {
  margin: 0;
  font-weight: 700;
  color: var(--text-color, var(--el-text-color-primary));
}

.result-empty__desc {
  margin: 0;
  line-height: 1.5;
}

.status-pill {
  font-weight: 600;
  letter-spacing: 0.01em;
}

.status-pill--draft {
  border-color: var(--button-warning-bg, var(--el-color-warning));
  color: var(--color-warning-dark-2, var(--el-color-warning-dark-2));
  background: color-mix(
    in srgb,
    var(--button-warning-bg, var(--el-color-warning)) 12%,
    var(--color-card, #fff) 88%
  );
}

.status-pill--finalized {
  border-color: var(--button-default-border, var(--el-border-color));
  color: var(--muted-color, var(--el-text-color-secondary));
  background: color-mix(
    in srgb,
    var(--button-default-bg, var(--el-fill-color-light)) 72%,
    var(--color-card, #fff) 28%
  );
}

.status-pill--paid {
  border-color: var(--button-success-bg, var(--el-color-success));
  color: var(--color-success-dark-2, var(--el-color-success-dark-2));
  background: color-mix(
    in srgb,
    var(--button-success-bg, var(--el-color-success)) 12%,
    var(--color-card, #fff) 88%
  );
}
</style>
