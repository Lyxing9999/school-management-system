<script setup lang="ts">
import type { Role } from "~/api/types/enums/role.enum";
import StaffModePills from "~/components/filters/StaffModePills.vue";
type StaffMode = "default" | "user" | "staff";

const props = defineProps<{
  loading: boolean;
  stats: any;
  isDirty: boolean;
  staffMode: StaffMode;
  selectedRoles: Role[];
  currentRoleOptions: { label: string; value: Role }[];
  searchModelValue: string;
}>();

const emit = defineEmits<{
  (e: "update:staffMode", v: StaffMode): void;
  (e: "update:selectedRoles", v: Role[]): void;
  (e: "update:searchModelValue", v: string): void;
  (e: "refresh"): void;
  (e: "reset"): void;
  (e: "open-create"): void;
}>();
</script>

<template>
  <OverviewHeader
    title="Users"
    description="Manage all users, roles and staff accounts."
    :loading="loading"
    :stats="stats"
    :show-refresh="true"
    :show-search="true"
    :show-reset="true"
    :reset-disabled="!isDirty"
    :search-model-value="searchModelValue"
    @update:searchModelValue="(v: string) => emit('update:searchModelValue', v)"
    @refresh="emit('refresh')"
    @reset="emit('reset')"
  >
    <template #filters>
      <el-row :gutter="12" align="middle" class="w-full">
        <!-- Mode -->
        <el-col :xs="24" :sm="24" :md="12">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs text-gray-500 whitespace-nowrap">Mode:</span>
            <StaffModePills
              :model-value="staffMode"
              :disabled="loading"
              @update:model-value="(v: StaffMode) => emit('update:staffMode', v)"
            />
          </div>
        </el-col>

        <!-- Roles -->
        <el-col :xs="24" :sm="24" :md="12">
          <div class="flex flex-wrap items-center gap-2 md:justify-end w-full">
            <span class="text-xs text-gray-500 whitespace-nowrap">Roles:</span>

            <el-select
              :model-value="selectedRoles"
              multiple
              filterable
              clearable
              class="w-full md:w-[360px]"
              @update:model-value="(v) => emit('update:selectedRoles', v as Role[])"
            >
              <el-option
                v-for="opt in currentRoleOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>
        </el-col>
      </el-row>
    </template>

    <template #actions>
      <BaseButton
        plain
        :loading="loading"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="emit('refresh')"
      >
        Refresh
      </BaseButton>
      <BaseButton
        type="primary"
        :disabled="loading"
        @click="emit('open-create')"
      >
        Add {{ staffMode === "staff" ? "Staff" : "Student" }}
      </BaseButton>
    </template>
  </OverviewHeader>
</template>
