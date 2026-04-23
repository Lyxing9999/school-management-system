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

const formattedGeneratedAt = computed(() => {
  const value = result.value?.generated_at;
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
    result.value?.payroll_run_label || result.value?.month,
    result.value?.month || form.month,
  );
});

const resultStatus = computed(() => {
  const status = String(result.value?.status || "").toLowerCase();
  if (!status) return "-";
  return status.toUpperCase();
});

const resultStatusTagType = computed<"warning" | "success" | "info">(() => {
  const status = String(result.value?.status || "").toLowerCase();
  if (status === "draft") return "warning";
  if (status === "paid") return "success";
  return "info";
});

const resultStatusClass = computed(() => {
  const status = String(result.value?.status || "").toLowerCase();
  if (status === "draft") return "status-pill status-pill--draft";
  if (status === "paid") return "status-pill status-pill--paid";
  return "status-pill status-pill--finalized";
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
  void router.push(ROUTES.HR_ADMIN.PAYROLL_RUNS);
}

function goToPayslips() {
  void router.push(ROUTES.HR_ADMIN.PAYSLIPS);
}
</script>

<template>
  <OverviewHeader
    :title="'Generate Payroll Run'"
    :description="'Create a payroll run for a specific month using finalized attendance and payroll rules'"
    :backPath="'/hr/payroll/runs'"
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
              {{ result.month || form.month || "-" }}
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
              {{ Number(result.total_employees || 0) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Total Amount">
              {{
                Number(result.total_amount || 0).toLocaleString("en-US", {
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
  border-color: #e6a23c;
  color: #b88230;
  background: #fff8eb;
}

.status-pill--finalized {
  border-color: #909399;
  color: #5d6066;
  background: #f4f4f5;
}

.status-pill--paid {
  border-color: #67c23a;
  color: #3b8f1d;
  background: #f1faec;
}
</style>
