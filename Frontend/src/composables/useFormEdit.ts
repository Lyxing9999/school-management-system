// composables/useFormEdit.ts
import {
  ref,
  computed,
  unref,
  watch,
  toRaw,
  type Ref,
  type ComputedRef,
} from "vue";
import type { FormInstance } from "element-plus";
import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";

export type InitialData<I> =
  | Partial<I>
  | Ref<Partial<I>>
  | ComputedRef<Partial<I>>;

type WithResult<T> = { result: T };
/**
 * useFormEdit
 * Handles dynamic edit/detail forms with patch/put/update support.
 * Defaults to PATCH on save.
 */
export function useFormEdit<I extends object, O extends I = I>(
  getService: () => UseFormService<any, I, any, O, any>,
  getDefaultData: () => I,
  getFields: () => Field<I>[]
) {
  const service = computed(() => getService());
  const formDialogVisible = ref(false);
  const loading = ref(false);
  const elFormRef = ref<FormInstance>();
  const saveId = ref<string | number>("");
  const formData = ref<Partial<I>>({});
  const reactiveInitialData = ref<Partial<I>>({});
  const patchData = ref<Partial<I>>({});
  const schema = computed(() => unref(getFields()));
  const defaultData = computed(() => unref(getDefaultData()));

  watch(
    formData,
    (newVal) => {
      if (!newVal || typeof newVal !== "object") return;
      const fields = schema.value;
      fields.forEach((field) => {
        const key = field.key as keyof I;
        if (!key) return;

        const newValue = newVal[key];
        const oldValue = reactiveInitialData.value[key];

        if (newValue !== oldValue) patchData.value[key] = newValue;
        else delete patchData.value[key];
      });
    },
    { deep: true }
  );

  /** Reset form data (defaults to reactiveInitialData) */
  const resetFormData = (data?: Partial<I>) => {
    const safeInitial = reactiveInitialData.value || {};
    Object.keys(formData.value).forEach((key) => {
      if (!(key in safeInitial)) delete (formData.value as any)[key];
    });
    Object.assign(formData.value, { ...safeInitial, ...data });
  };
  /** Open form and load detail by ID */
  const openForm = async (id: string | number) => {
    if (!service.value?.getDetail) return;
    loading.value = true;
    saveId.value = id;

    try {
      const detail = await service.value.getDetail(saveId.value.toString());
      console.log("Detail:", detail);

      // Normalize the payload: use `result` if exists, otherwise use detail
      const data = (
        detail && "result" in detail ? (detail as WithResult<O>).result : detail
      ) as Partial<I>;

      if (!data || Object.keys(data).length === 0) {
        resetFormData(defaultData.value);
        formData.value = defaultData.value;
        reactiveInitialData.value = defaultData.value;
        return;
      }

      reactiveInitialData.value = toRaw(data);
      resetFormData(data);
    } finally {
      loading.value = false;
    }
  };
  /** Save form — PATCH by default, PUT if method is explicitly set */
  const saveForm = async (
    payload: Partial<I>,
    method: "PATCH" | "PUT" = "PATCH"
  ): Promise<boolean> => {
    if (!service.value.update) return false;
    loading.value = true;

    try {
      // Validate form
      if (elFormRef.value) await elFormRef.value.validate();
      let response: I | null = null;

      // Merge payload into formData
      if (payload) Object.assign(formData.value, payload);

      // Collect fields based on form schema
      const fields = schema.value as Field<I>[];
      const filteredData: Partial<I> = {};

      const collectKeys = (fields: Field<I>[]) => {
        fields.forEach((field) => {
          if (field.row) {
            collectKeys(field.row);
          } else if (field.key != null && field.key in formData.value) {
            filteredData[field.key] = formData.value[field.key];
          }
        });
      };

      collectKeys(fields);

      // --- Handle file upload ---
      if (
        "photo_file" in formData.value &&
        (formData.value as any).photo_file
      ) {
        const file = (formData.value as any).photo_file as File;
        console.log("Appending photo_file to filteredData:", file.name);
        (filteredData as any).photo_file = file;
      }

      // --- Send request ---
      try {
        if (method === "PUT" && service.value.update) {
          response = await service.value.update(
            saveId.value.toString(),
            formData as unknown as I
          );
        } else {
          response = await service.value.update(
            saveId.value.toString(),
            filteredData as I
          );
        }
      } catch (err) {
        console.error("Update failed:", err);
        return false; // do NOT close dialog
      }

      // --- Update local state ---
      if (response) {
        resetFormData(response);
        formDialogVisible.value = false;
        return true;
      }

      return false;
    } finally {
      loading.value = false;
    }
  };
  /** Cancel and reset */
  const cancelForm = () => {
    formDialogVisible.value = false;
    resetFormData();
  };

  return {
    formDialogVisible,
    loading,
    elFormRef,
    formData,
    schema,
    patchData,
    openForm,
    saveForm,
    cancelForm,
    resetFormData,
  } as const;
}
