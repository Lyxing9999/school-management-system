<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import type { AxiosInstance } from "axios";
import { TeacherService } from "~/src/services/teacherService";
import UserDetailDialog from "~/components/TableEdit/UserDetailDialog.vue";
import SmartTable from "~/components/TableEdit/SmartTable.vue";
import { ElMessage, ElMessageBox } from "element-plus";

const $api = useNuxtApp().$api as AxiosInstance;

interface ClassInfo {
  course_code: string;
  course_title: string;
  lecturer: string;
  email: string;
  phone_number: string;
  hybrid: boolean;
  credits: number;
  link_telegram: string;
  department: string;
  description: string;
  year: number;
}

interface ClassItem {
  _id: string;
  created_by: string;
  max_students: number;
  course_code: string;
  class_info: ClassInfo;
}

interface FieldConfig {
  key: string;
  label: string;
  type: string;
}

interface TableColumn {
  field: string;
  label: string;
  type: string;
  readonly?: boolean;
  showSaveCancelControls?: boolean;
  slot?: boolean;
}

// Reactive state
const classes = ref<ClassItem[]>([]);
const handleDialog = ref(false);
const handleDialogInfo = ref<ClassItem | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

// Service instance
const teacherService = new TeacherService($api);

// Configuration arrays with proper typing
const fieldInfo: FieldConfig[] = [
  { key: "class_info.course_code", label: "Course Code", type: "string" },
  { key: "class_info.course_title", label: "Course Title", type: "string" },
  { key: "class_info.lecturer", label: "Lecturer", type: "string" },
  { key: "class_info.email", label: "Email", type: "string" },
  { key: "class_info.phone_number", label: "Phone Number", type: "string" },
  { key: "class_info.hybrid", label: "Hybrid", type: "boolean" },
  { key: "class_info.credits", label: "Credits", type: "number" },
  { key: "class_info.link_telegram", label: "Telegram Link", type: "string" },
  { key: "class_info.department", label: "Department", type: "string" },
  { key: "class_info.description", label: "Description", type: "string" },
  { key: "class_info.year", label: "Year", type: "number" },
];

const fields: TableColumn[] = [
  {
    field: "created_by",
    label: "Created By",
    type: "string",
    readonly: true,
    showSaveCancelControls: false,
  },
  {
    field: "max_students",
    label: "Max Students",
    type: "string",
    readonly: true,
    showSaveCancelControls: false,
  },
  {
    field: "Operation",
    type: "operation",
    slot: true,
  },
];

// Computed properties
const hasClasses = computed(() => classes.value.length > 0);
const isEmpty = computed(() => !isLoading.value && classes.value.length === 0);

// Methods
const fetchClasses = async (): Promise<void> => {
  try {
    isLoading.value = true;
    error.value = null;

    const response = await teacherService.getTeacherClasses();
    classes.value = response || [];

    if (classes.value.length === 0) {
      ElMessage.info("No classes found");
    }
  } catch (err) {
    error.value = "Failed to fetch classes. Please try again.";
    ElMessage.error("Failed to fetch classes");
    console.error("Fetch classes error:", err);
  } finally {
    isLoading.value = false;
  }
};

const handleClassInfo = (id: string): void => {
  const classInfo = classes.value.find((c) => c._id === id);

  if (!classInfo) {
    ElMessage.error("Class not found");
    return;
  }

  handleDialogInfo.value = classInfo;
  handleDialog.value = true;
};

const handleDelete = async (row: ClassItem): Promise<void> => {
  try {
    // Enhanced confirmation dialog
    await ElMessageBox.confirm(
      `This will permanently delete the class "${
        row.class_info?.course_title || row.course_code
      }". Continue?`,
      "Warning",
      {
        confirmButtonText: "Delete",
        cancelButtonText: "Cancel",
        type: "warning",
        confirmButtonClass: "el-button--danger",
      }
    );

    isLoading.value = true;

    await teacherService.deleteClass(row._id);

    // Optimistic update - remove from local list immediately
    classes.value = classes.value.filter((c) => c._id !== row._id);

    ElMessage.success("Class deleted successfully");
  } catch (err) {
    // Handle both user cancellation and API errors
    if (err === "cancel") {
      ElMessage.info("Delete cancelled");
    } else {
      ElMessage.error("Failed to delete class");
      console.error("Delete class error:", err);
    }
  } finally {
    isLoading.value = false;
  }
};

const handleDialogClose = (): void => {
  handleDialog.value = false;
  handleDialogInfo.value = null;
};

const refreshData = async (): Promise<void> => {
  await fetchClasses();
};

// Lifecycle
onMounted(async () => {
  await fetchClasses();
});
</script>

<template>
  <div class="class-management">
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <el-alert :title="error" type="error" show-icon :closable="false">
        <template #default>
          <el-button size="small" type="primary" @click="refreshData">
            Retry
          </el-button>
        </template>
      </el-alert>
    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="empty-container">
      <el-empty description="No classes found">
        <el-button type="primary" @click="refreshData"> Refresh </el-button>
      </el-empty>
    </div>

    <!-- Data Table -->
    <div v-else class="table-container">
      <SmartTable :data="classes" :columns="fields" :loading="isLoading">
        <template #operation="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="handleClassInfo(row._id)"
            :disabled="isLoading"
          >
            Detail
          </el-button>

          <el-button
            type="danger"
            size="small"
            @click="handleDelete(row)"
            :disabled="isLoading"
          >
            Delete
          </el-button>
        </template>
      </SmartTable>
    </div>

    <!-- Detail Dialog -->
    <UserDetailDialog
      v-model="handleDialog"
      :info-object="handleDialogInfo"
      :fields="fieldInfo"
      @close="handleDialogClose"
    />
  </div>
</template>

<style scoped>
.class-management {
  padding: 20px;
}

.loading-container,
.error-container,
.empty-container {
  padding: 40px 20px;
  text-align: center;
}

.table-container {
  margin-top: 20px;
}

.error-container .el-alert {
  max-width: 500px;
  margin: 0 auto;
}

.empty-container {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
