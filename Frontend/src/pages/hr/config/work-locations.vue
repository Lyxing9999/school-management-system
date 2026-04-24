<template>
  <div class="work-locations-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Work Locations</h1>
        <p class="page-description">
          Manage work locations for employee attendance tracking
        </p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Plus"
          class="header-btn"
          @click="openCreateDialog"
        >
          Add Location
        </el-button>
      </div>
    </div>

    <!-- Connection Error Banner -->
    <el-alert
      v-if="connectionError"
      title="Connection Error"
      type="error"
      :closable="false"
      show-icon
      class="mb-4"
    >
      <template #default>
        Unable to connect to the server. Please check your internet connection.
        <el-button
          type="primary"
          size="small"
          plain
          @click="refreshData"
          :loading="isLoading"
          class="ml-2"
        >
          Retry
        </el-button>
      </template>
    </el-alert>

    <!-- Filters Toolbar -->
    <div class="filters-toolbar">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-input
            v-model="filters.q"
            placeholder="Search locations..."
            :prefix-icon="Search"
            clearable
            @input="debouncedSearch"
          />
        </el-col>

        <el-col :xs="12" :sm="6" :md="4" :lg="3">
          <el-select
            v-model="filters.status"
            placeholder="Status"
            @change="applyFilters"
          >
            <el-option label="All" value="all" />
            <el-option label="Active" value="active" />
            <el-option label="Inactive" value="inactive" />
          </el-select>
        </el-col>

        <el-col :xs="12" :sm="6" :md="4" :lg="4">
          <el-select
            v-model="filters.deleted_mode"
            placeholder="View Mode"
            @change="applyFilters"
          >
            <el-option label="Normal" value="normal" />
            <el-option label="Include Deleted" value="include_deleted" />
            <el-option label="Deleted Only" value="deleted_only" />
          </el-select>
        </el-col>

        <el-col :xs="24" :sm="24" :md="8" :lg="11">
          <div class="toolbar-actions">
            <el-button
              :icon="Refresh"
              class="header-btn header-btn--refresh"
              @click="refreshData"
              :loading="isLoading"
            >
              Refresh
            </el-button>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="meta-strip">
      <el-tag type="info" effect="plain">
        Active Location:
        {{ activeLocation?.name || "Not configured" }}
      </el-tag>
      <el-tag type="success" effect="plain">
        Select Options: {{ selectOptions.length }}
      </el-tag>
    </div>

    <!-- Data Table -->
    <div class="table-container">
      <el-table
        v-loading="isLoading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
        :empty-text="emptyText"
        @sort-change="handleSortChange"
      >
        <el-table-column
          prop="name"
          label="Location Name"
          sortable="custom"
          min-width="180"
        >
          <template #default="{ row }">
            <div class="location-name">
              <span :class="{ 'deleted-item': row.lifecycle.deleted_at }">
                {{ row.name }}
              </span>
              <el-tag
                v-if="row.lifecycle.deleted_at"
                type="danger"
                size="small"
                class="ml-2"
              >
                Deleted
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="address"
          label="Address"
          min-width="250"
          show-overflow-tooltip
        />

        <el-table-column label="Coordinates" min-width="160">
          <template #default="{ row }">
            <div class="coordinates">
              <code class="coordinate-text">
                {{ formatCoordinates(row.latitude, row.longitude) }}
              </code>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="radius_meters"
          label="Radius"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ formatRadius(row.radius_meters) }}
          </template>
        </el-table-column>

        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :disabled="!!row.lifecycle.deleted_at || isUpdatingStatus[row.id]"
              :loading="isUpdatingStatus[row.id]"
              @change="toggleStatus(row)"
            />
          </template>
        </el-table-column>

        <el-table-column
          label="Actions"
          width="200"
          align="center"
          fixed="right"
        >
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="Edit Location" placement="top">
                <el-button
                  :icon="Edit"
                  size="small"
                  type="primary"
                  plain
                  @click="openEditDialog(row)"
                  :disabled="!!row.lifecycle.deleted_at"
                />
              </el-tooltip>

              <el-tooltip content="Open in Google Maps" placement="top">
                <el-button
                  :icon="MapLocation"
                  size="small"
                  type="success"
                  plain
                  @click="openInGoogleMaps(row)"
                />
              </el-tooltip>

              <el-tooltip
                :content="
                  row.lifecycle.deleted_at
                    ? 'Restore Location'
                    : 'Delete Location'
                "
                placement="top"
              >
                <el-button
                  :icon="row.lifecycle.deleted_at ? RefreshRight : Delete"
                  size="small"
                  :type="row.lifecycle.deleted_at ? 'warning' : 'danger'"
                  plain
                  @click="
                    row.lifecycle.deleted_at
                      ? restoreLocation(row)
                      : deleteLocation(row)
                  "
                  :loading="isDeletingOrRestoring[row.id]"
                />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.limit"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="90%"
      :max-width="1200"
      :close-on-click-modal="false"
      @close="closeDialog"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        label-position="top"
      >
        <el-row :gutter="24">
          <!-- Left Column - Form Fields -->
          <el-col :xs="24" :lg="12">
            <el-form-item label="Location Name" prop="name">
              <el-input
                v-model="formData.name"
                placeholder="Enter location name"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="Address" prop="address">
              <el-input
                v-model="formData.address"
                type="textarea"
                :rows="3"
                placeholder="Enter address"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="Latitude" prop="latitude">
                  <el-input-number
                    v-model="formData.latitude"
                    :precision="6"
                    :min="-90"
                    :max="90"
                    :step="0.000001"
                    style="width: 100%"
                    placeholder="Latitude"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Longitude" prop="longitude">
                  <el-input-number
                    v-model="formData.longitude"
                    :precision="6"
                    :min="-180"
                    :max="180"
                    :step="0.000001"
                    style="width: 100%"
                    placeholder="Longitude"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Radius (meters)" prop="radius_meters">
              <el-input-number
                v-model="formData.radius_meters"
                :min="1"
                :max="10000"
                :step="10"
                style="width: 100%"
              />
              <div class="form-help-text">
                Attendance tracking radius:
                {{ formatRadius(formData.radius_meters || 0) }}
              </div>
            </el-form-item>

            <el-form-item label="Status">
              <el-switch
                v-model="formData.is_active"
                active-text="Active"
                inactive-text="Inactive"
              />
            </el-form-item>
          </el-col>

          <!-- Right Column - Map Picker -->
          <el-col :xs="24" :lg="12">
            <el-form-item label="Location Picker">
              <ClientOnly>
                <GoogleLocationPicker
                  :latitude="formData.latitude"
                  :longitude="formData.longitude"
                  :radius-meters="formData.radius_meters || 100"
                  :address="formData.address"
                  :auto-detect-location="!isEditMode"
                  height="450px"
                  @update:latitude="formData.latitude = $event"
                  @update:longitude="formData.longitude = $event"
                  @update:address="formData.address = $event"
                  @picked="handleLocationPicked"
                />
                <template #fallback>
                  <div class="map-fallback">
                    <el-skeleton :rows="8" animated />
                  </div>
                </template>
              </ClientOnly>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDialog">Cancel</el-button>
          <el-button type="primary" @click="submitForm" :loading="isSubmitting">
            {{ isEditMode ? "Update" : "Create" }} Location
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessageBox } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import {
  Plus,
  Search,
  Refresh,
  Edit,
  Delete,
  MapLocation,
  RefreshRight,
} from "@element-plus/icons-vue";
import { debounce } from "lodash-es";

import GoogleLocationPicker from "~/components/hr/location/GoogleLocationPicker.vue";
import type {
  WorkLocationDTO,
  WorkLocationCreateDTO,
  WorkLocationUpdateDTO,
} from "~/api/hr_admin/workLocations/dto";
import { hrmsAdminService } from "~/api/hr_admin";

// Page meta
definePageMeta({
  title: "Work Locations",
  layout: "default",
});

// Services
const workLocationService = hrmsAdminService().workLocation;

// Reactive data
const tableData = ref<WorkLocationDTO[]>([]);
const isLoading = ref(false);
const isSubmitting = ref(false);
const isUpdatingStatus = ref<Record<string, boolean>>({});
const isDeletingOrRestoring = ref<Record<string, boolean>>({});
const connectionError = ref(false);
const activeLocation = ref<WorkLocationDTO | null>(null);
const selectOptions = ref<{ value: string; label: string }[]>([]);

// Filters
const filters = reactive({
  q: "",
  status: "all" as "all" | "active" | "inactive",
  deleted_mode: "normal" as "normal" | "include_deleted" | "deleted_only",
});

// Pagination
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0,
});

// Dialog state
const dialogVisible = ref(false);
const isEditMode = ref(false);
const currentEditId = ref<string | null>(null);

// Form
const formRef = ref<FormInstance>();
const formData = reactive<WorkLocationCreateDTO>({
  name: "",
  address: "",
  latitude: 0,
  longitude: 0,
  radius_meters: 100,
  is_active: true,
});

// Form validation rules
const formRules: FormRules = {
  name: [
    { required: true, message: "Location name is required", trigger: "blur" },
    {
      min: 2,
      max: 100,
      message: "Name must be 2-100 characters",
      trigger: "blur",
    },
  ],
  address: [
    { required: true, message: "Address is required", trigger: "blur" },
    {
      min: 5,
      max: 500,
      message: "Address must be 5-500 characters",
      trigger: "blur",
    },
  ],
  latitude: [
    { required: true, message: "Latitude is required", trigger: "blur" },
    {
      type: "number",
      min: -90,
      max: 90,
      message: "Invalid latitude",
      trigger: "blur",
    },
  ],
  longitude: [
    { required: true, message: "Longitude is required", trigger: "blur" },
    {
      type: "number",
      min: -180,
      max: 180,
      message: "Invalid longitude",
      trigger: "blur",
    },
  ],
  radius_meters: [
    { required: true, message: "Radius is required", trigger: "blur" },
    {
      type: "number",
      min: 1,
      max: 10000,
      message: "Radius must be 1-10000 meters",
      trigger: "blur",
    },
  ],
};

// Computed
const dialogTitle = computed(() =>
  isEditMode.value ? "Edit Work Location" : "Create Work Location",
);

const emptyText = computed(() => {
  if (isLoading.value) return "Loading...";
  if (connectionError.value) return "Connection error - unable to load data";
  if (filters.q) return "No locations found matching your search";
  if (filters.deleted_mode === "deleted_only")
    return "No deleted locations found";
  return 'No work locations found. Click "Add Location" to create your first location.';
});

// Debounced search
const debouncedSearch = debounce(() => {
  applyFilters();
}, 300);

// Lifecycle
onMounted(() => {
  loadData();
});

// Methods
function handleLocationPicked(location: {
  latitude: number;
  longitude: number;
  address?: string;
}) {
  formData.latitude = location.latitude;
  formData.longitude = location.longitude;
  if (location.address) {
    formData.address = location.address;
  }
}

// Methods
async function loadData() {
  isLoading.value = true;
  try {
    // Map filters to API params
    const params: any = {};

    if (filters.q) {
      params.q = filters.q;
    }

    // Map status filter
    if (filters.status === "active") {
      params.is_active = true;
    } else if (filters.status === "inactive") {
      params.is_active = false;
    }

    // Map deleted mode
    if (filters.deleted_mode === "include_deleted") {
      params.include_deleted = true;
    } else if (filters.deleted_mode === "deleted_only") {
      params.deleted_only = true;
    }

    const response = await workLocationService.getWorkLocations(params);

    tableData.value = response || [];
    pagination.total = response?.length || 0;

    const [active, options] = await Promise.all([
      workLocationService.getActiveWorkLocation({ showError: false }),
      workLocationService.getWorkLocationSelectOptions({ showError: false }),
    ]);

    activeLocation.value = active;
    selectOptions.value = options;
    connectionError.value = false;
  } catch (error: any) {
    console.error("Error loading work locations:", error);
    connectionError.value = true;

    // Set empty data on error
    tableData.value = [];
    pagination.total = 0;
    activeLocation.value = null;
    selectOptions.value = [];
  } finally {
    isLoading.value = false;
  }
}

function applyFilters() {
  pagination.page = 1;
  loadData();
}

function refreshData() {
  void loadData();
}

function handleSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  loadData();
}

function handleCurrentChange(page: number) {
  pagination.page = page;
  loadData();
}

function handleSortChange(sort: any) {
  // Implement sorting if needed
  void sort;
}

function openCreateDialog() {
  isEditMode.value = false;
  currentEditId.value = null;
  resetForm();
  dialogVisible.value = true;
}

async function openEditDialog(location: WorkLocationDTO) {
  const detail = await workLocationService.getWorkLocation(location.id);

  isEditMode.value = true;
  currentEditId.value = detail.id;

  // Populate form
  Object.assign(formData, {
    name: detail.name,
    address: detail.address,
    latitude: detail.latitude,
    longitude: detail.longitude,
    radius_meters: detail.radius_meters,
    is_active: detail.is_active,
  });

  dialogVisible.value = true;
}

function closeDialog() {
  dialogVisible.value = false;
  resetForm();
}

function resetForm() {
  Object.assign(formData, {
    name: "",
    address: "",
    latitude: 0,
    longitude: 0,
    radius_meters: 100,
    is_active: true,
  });
  formRef.value?.clearValidate();
}

async function submitForm() {
  if (!formRef.value) return;

  try {
    const valid = await formRef.value.validate();
    if (!valid) return;

    isSubmitting.value = true;

    if (isEditMode.value && currentEditId.value) {
      const updateData: WorkLocationUpdateDTO = {
        name: formData.name,
        address: formData.address,
        latitude: formData.latitude,
        longitude: formData.longitude,
        radius_meters: formData.radius_meters,
        is_active: formData.is_active,
      };

      await workLocationService.updateWorkLocation(
        currentEditId.value,
        updateData,
      );
    } else {
      await workLocationService.createWorkLocation(formData);
    }

    closeDialog();
    loadData();
  } catch (error: any) {
    console.error("Error submitting form:", error);
  } finally {
    isSubmitting.value = false;
  }
}

async function toggleStatus(location: WorkLocationDTO) {
  const locationId = location.id;
  isUpdatingStatus.value[locationId] = true;

  try {
    if (location.is_active) {
      await workLocationService.activateWorkLocation(locationId);
    } else {
      await workLocationService.deactivateWorkLocation(locationId);
    }
  } catch (error) {
    console.error("Error toggling status:", error);
    // Revert the switch
    location.is_active = !location.is_active;
  } finally {
    isUpdatingStatus.value[locationId] = false;
  }
}

async function deleteLocation(location: WorkLocationDTO) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${location.name}"? This action can be undone.`,
      "Delete Work Location",
      {
        confirmButtonText: "Delete",
        cancelButtonText: "Cancel",
        type: "warning",
      },
    );

    const locationId = location.id;
    isDeletingOrRestoring.value[locationId] = true;

    await workLocationService.softDeleteWorkLocation(locationId);
    loadData();
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("Error deleting location:", error);
    }
  } finally {
    isDeletingOrRestoring.value[location.id] = false;
  }
}

async function restoreLocation(location: WorkLocationDTO) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to restore "${location.name}"?`,
      "Restore Work Location",
      {
        confirmButtonText: "Restore",
        cancelButtonText: "Cancel",
        type: "info",
      },
    );

    const locationId = location.id;
    isDeletingOrRestoring.value[locationId] = true;

    await workLocationService.restoreWorkLocation(locationId);
    loadData();
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("Error restoring location:", error);
    }
  } finally {
    isDeletingOrRestoring.value[location.id] = false;
  }
}

function openInGoogleMaps(location: WorkLocationDTO) {
  const url = `https://www.google.com/maps?q=${location.latitude},${location.longitude}`;
  window.open(url, "_blank");
}

function formatCoordinates(latitude: number, longitude: number): string {
  return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
}

function formatRadius(radiusMeters: number): string {
  if (radiusMeters >= 1000) {
    return `${(radiusMeters / 1000).toFixed(1)} km`;
  }
  return `${radiusMeters} m`;
}
</script>

<style scoped>
.work-locations-page {
  padding: 24px;
  background: var(--color-bg);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 24px;
  background: var(--color-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px var(--card-shadow);
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--color-dark);
}

.header-content p {
  margin: 0;
  color: var(--muted-color);
  font-size: 14px;
}

.filters-toolbar {
  margin-bottom: 16px;
  padding: 16px;
  background: var(--color-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px var(--card-shadow);
}

.meta-strip {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.toolbar-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.header-btn {
  min-height: 36px;
  border-radius: 10px;
  font-weight: 650;
}

.header-btn--refresh {
  border-color: color-mix(
    in srgb,
    var(--border-color) 60%,
    var(--color-primary) 40%
  ) !important;
  color: color-mix(
    in srgb,
    var(--text-color) 82%,
    var(--color-primary) 18%
  ) !important;
  background: color-mix(
    in srgb,
    var(--color-card) 94%,
    var(--color-bg) 6%
  ) !important;
}

.header-btn--refresh:hover {
  background: var(--hover-bg) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 48%,
    var(--color-primary) 52%
  ) !important;
}

.table-container {
  background: var(--color-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px var(--card-shadow);
  overflow: hidden;
}

.location-name {
  display: flex;
  align-items: center;
}

.deleted-item {
  text-decoration: line-through;
  opacity: 0.6;
}

.coordinates {
  font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
}

.coordinate-text {
  font-size: 12px;
  background: color-mix(in srgb, var(--color-card) 94%, var(--color-bg) 6%);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.table-actions {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.pagination-container {
  padding: 16px;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-color);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-help-text {
  font-size: 12px;
  color: var(--muted-color);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .work-locations-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    align-self: flex-start;
  }

  .toolbar-actions {
    justify-content: flex-start;
    margin-top: 12px;
  }

  .table-actions {
    flex-direction: column;
    gap: 2px;
  }
}

@media (max-width: 480px) {
  .coordinate-text {
    font-size: 10px;
  }
}

.map-fallback {
  width: 100%;
  height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--color-card) 94%, var(--color-bg) 6%);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}
</style>
