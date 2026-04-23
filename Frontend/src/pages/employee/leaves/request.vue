<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import {
  ElButton,
  ElCard,
  ElCol,
  ElDatePicker,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElRow,
  ElSelect,
  ElOption,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  LeaveBalanceDTO,
  LeaveSubmitDTO,
  LeaveType,
} from "~/api/hr_admin/leave/dto";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const router = useRouter();
const leaveService = hrmsAdminService().leaveRequest;

const loadingBalance = ref(false);
const submitting = ref(false);

const balance = ref<LeaveBalanceDTO | null>(null);
const formRef = ref<FormInstance>();

type LeaveSubmitFormModel = Omit<LeaveSubmitDTO, "leave_type"> & {
  leave_type: LeaveType | "";
};

const form = reactive<LeaveSubmitFormModel>({
  leave_type: "",
  start_date: "",
  end_date: "",
  reason: "",
});

const rules: FormRules = {
  leave_type: [
    {
      required: true,
      message: "Leave type is required",
      trigger: "change",
    },
  ],
  start_date: [
    {
      required: true,
      message: "Start date is required",
      trigger: "change",
    },
  ],
  end_date: [
    {
      required: true,
      message: "End date is required",
      trigger: "change",
    },
    {
      validator: (_rule, value: string, callback) => {
        if (!value || !form.start_date) {
          callback();
          return;
        }

        if (new Date(value).getTime() < new Date(form.start_date).getTime()) {
          callback(new Error("End date cannot be earlier than start date"));
          return;
        }

        callback();
      },
      trigger: "change",
    },
  ],
  reason: [
    {
      required: true,
      message: "Reason is required",
      trigger: "blur",
    },
    {
      min: 5,
      message: "Reason should be at least 5 characters",
      trigger: "blur",
    },
  ],
};

const totalRequestedDays = computed(() => {
  if (!form.start_date || !form.end_date) return 0;

  const start = new Date(form.start_date);
  const end = new Date(form.end_date);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 0;

  const days = Math.floor((end.getTime() - start.getTime()) / 86_400_000) + 1;
  return days > 0 ? days : 0;
});

const leaveTypePreview = computed(() => {
  if (!form.leave_type) return "Not selected";
  return form.leave_type
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
});

const balanceCards = computed(() => [
  {
    label: "Annual Entitlement",
    value: balance.value?.annual_entitlement ?? 0,
    hint: "Total annual leave allocation",
  },
  {
    label: "Used Days",
    value: balance.value?.used_days ?? 0,
    hint: "Days already consumed",
  },
  {
    label: "Remaining Days",
    value: balance.value?.remaining_days ?? 0,
    hint: "Available leave balance",
  },
  {
    label: "This Request",
    value: totalRequestedDays.value,
    hint: "Calculated from selected date range",
  },
]);

const balanceStateTag = computed<"success" | "warning" | "danger">(() => {
  const remain = Number(balance.value?.remaining_days ?? 0);
  if (remain > 5) return "success";
  if (remain > 0) return "warning";
  return "danger";
});

function disablePastDates(date: Date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date.getTime() < today.getTime();
}

async function loadBalance() {
  loadingBalance.value = true;
  try {
    balance.value = await leaveService.getMyBalance();
  } catch {
    // Service layer already handles API error messages.
  } finally {
    loadingBalance.value = false;
  }
}

function resetForm() {
  form.leave_type = "";
  form.start_date = "";
  form.end_date = "";
  form.reason = "";
  formRef.value?.clearValidate();
}

async function submitRequest() {
  try {
    await formRef.value?.validate();
  } catch {
    ElMessage.error("Please complete the form before submitting");
    return;
  }

  submitting.value = true;
  try {
    await leaveService.submitRequest({
      leave_type: form.leave_type as LeaveType,
      start_date: form.start_date,
      end_date: form.end_date,
      reason: form.reason.trim(),
    });

    resetForm();
    await loadBalance();
  } catch {
    // Service layer already handles API error messages.
  } finally {
    submitting.value = false;
  }
}

async function refreshPage() {
  await loadBalance();
}

onMounted(() => {
  void loadBalance();
});
</script>

<template>
  <div class="employee-leave-request-page">
    <OverviewHeader
      title="Request Leave"
      description="Submit leave request and track remaining balance"
      :backPath="ROUTES.EMPLOYEE.LEAVE_HISTORY"
    >
      <template #actions>
        <BaseButton plain :loading="loadingBalance" @click="refreshPage">
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loadingBalance || submitting"
          @click="router.push(ROUTES.EMPLOYEE.LEAVE_HISTORY)"
        >
          Leave History
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="balance-row">
      <el-col
        v-for="item in balanceCards"
        :key="item.label"
        :xs="24"
        :sm="12"
        :lg="6"
      >
        <el-card class="balance-card" shadow="never" v-loading="loadingBalance">
          <p class="balance-card__label">{{ item.label }}</p>
          <p class="balance-card__value">{{ item.value }}</p>
          <p class="balance-card__hint">{{ item.hint }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="request-card" shadow="never" v-loading="submitting">
      <template #header>
        <div class="request-card__header">
          <div>
            <h2 class="request-card__title">Leave Request Form</h2>
            <p class="request-card__subtitle">
              Endpoint: POST /api/hrms/leave-requests
            </p>
          </div>

          <ElTag :type="balanceStateTag" effect="plain" round>
            Remaining: {{ balance?.remaining_days ?? 0 }} day(s)
          </ElTag>
        </div>
      </template>

      <ElForm ref="formRef" :model="form" :rules="rules" label-width="130px">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <ElFormItem label="Leave Type" prop="leave_type">
              <ElSelect
                v-model="form.leave_type"
                class="w-full"
                placeholder="Select leave type"
              >
                <ElOption label="Annual" value="annual" />
                <ElOption label="Sick" value="sick" />
                <ElOption label="Unpaid" value="unpaid" />
                <ElOption label="Other" value="other" />
              </ElSelect>
            </ElFormItem>
          </el-col>

          <el-col :xs="24" :md="12">
            <ElFormItem label="Selected Type">
              <ElInput :model-value="leaveTypePreview" readonly />
            </ElFormItem>
          </el-col>

          <el-col :xs="24" :md="12">
            <ElFormItem label="Start Date" prop="start_date">
              <ElDatePicker
                v-model="form.start_date"
                type="date"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                placeholder="Choose start date"
                class="w-full"
                :disabled-date="disablePastDates"
              />
            </ElFormItem>
          </el-col>

          <el-col :xs="24" :md="12">
            <ElFormItem label="End Date" prop="end_date">
              <ElDatePicker
                v-model="form.end_date"
                type="date"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                placeholder="Choose end date"
                class="w-full"
                :disabled-date="disablePastDates"
              />
            </ElFormItem>
          </el-col>
        </el-row>

        <ElFormItem label="Reason" prop="reason">
          <ElInput
            v-model="form.reason"
            type="textarea"
            :rows="4"
            placeholder="Explain the reason for this leave request"
            maxlength="500"
            show-word-limit
          />
        </ElFormItem>

        <div class="request-preview">
          <p class="request-preview__label">Request preview</p>
          <p class="request-preview__value">
            {{ totalRequestedDays }} day(s) for {{ leaveTypePreview }}
          </p>
        </div>

        <div class="form-actions">
          <ElButton type="primary" :loading="submitting" @click="submitRequest">
            Submit Request
          </ElButton>
          <ElButton :disabled="submitting" @click="resetForm">Reset</ElButton>
        </div>
      </ElForm>
    </el-card>
  </div>
</template>

<style scoped>
.employee-leave-request-page {
  padding: 20px;
  max-width: 1320px;
  margin: 0 auto;
}

.balance-row {
  margin-bottom: 16px;
}

.balance-card {
  border-radius: 16px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  background: linear-gradient(
    180deg,
    var(--color-card) 0%,
    color-mix(in srgb, var(--hover-bg) 28%, var(--color-card) 72%) 100%
  );
  height: 100%;
}

.balance-card__label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted-color);
}

.balance-card__value {
  margin: 8px 0 4px;
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--color-dark);
}

.balance-card__hint {
  margin: 0;
  font-size: 12px;
  color: var(--muted-color);
}

.request-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  box-shadow: 0 14px 36px var(--card-shadow);
}

.request-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.request-card__title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-dark);
}

.request-card__subtitle {
  margin: 4px 0 0;
  color: var(--muted-color);
  font-size: 13px;
}

.request-preview {
  margin-top: 4px;
  margin-bottom: 12px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--hover-bg);
}

.request-preview__label {
  margin: 0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-color);
}

.request-preview__value {
  margin: 6px 0 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-color);
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .request-card__header,
  .form-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
