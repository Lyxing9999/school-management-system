<script lang="ts" setup>
import type { Field } from "~/constants/fields/types/Field";

const props = defineProps<{
  modelValue: boolean;
  loading: boolean;
  title: string;
  infoObject: Record<string, any>;
  fields: Field[];
  width: string;
}>();

const emit = defineEmits<{
  (event: "update:modelValue", value: boolean): void;
}>();

function getNestedValue(obj: any, key: string) {
  if (!obj || !key) return null;
  const keys = key.split(".");
  let result = obj;
  for (const k of keys) {
    if (result == null) {
      return null;
    }
    result = result[k];
  }
  return result;
}
const nestedValues = computed(() => {
  if (!props.infoObject) return {};
  const result: Record<string, any> = {};
  for (const field of props.fields) {
    if (field.children && field.children.length) {
      for (const child of field.children) {
        result[child.key] = getNestedValue(props.infoObject, child.key);
      }
    } else {
      result[field.key] = getNestedValue(props.infoObject, field.key);
    }
  }
  return result;
});
watch(
  () => props.infoObject,
  (val) => {
    console.log("props.infoObject changed in dialog:", val);
  },
  { deep: true, immediate: true }
);
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    :width="width"
    @close="emit('update:modelValue', false)"
  >
    <el-skeleton :loading="loading" animated>
      <template v-if="infoObject">
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(item, index) in fields"
            :key="index"
            :label="item.label"
          >
            <template v-if="item.children && item.children.length">
              <el-descriptions :column="1" border>
                <el-descriptions-item
                  v-for="(child, idx) in item.children"
                  :key="idx"
                  :label="child.label"
                >
                  <template v-if="$slots.custom">
                    <slot
                      name="custom"
                      :item="child"
                      :infoObject="infoObject"
                      :value="nestedValues[child.key]"
                      :fields="fields"
                    />
                  </template>
                  <template v-else>
                    {{ nestedValues[child.key] || "N/A" }}
                  </template>
                </el-descriptions-item>
              </el-descriptions>
            </template>

            <template v-else-if="$slots.custom">
              <slot
                name="custom"
                :item="item"
                :infoObject="infoObject"
                :value="nestedValues[item.key]"
                :fields="fields"
              />
            </template>

            <template v-else>
              {{ nestedValues[item.key] || "N/A" }}
            </template>
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-skeleton>
  </el-dialog>
</template>
