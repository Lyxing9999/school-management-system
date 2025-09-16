# smartTable

## Overview

SmartTable is a component that allows you to create a table with editable cells.

## Props

| Name    | Type  | Description                              |
| ------- | ----- | ---------------------------------------- |
| data    | Array | The data to be displayed in the table    |
| columns | Array | The columns to be displayed in the table |

## Events

| Name     | Type     | Description                                                    |
| -------- | -------- | -------------------------------------------------------------- |
| save     | Function | The function to be called when the save button is clicked      |
| cancel   | Function | The function to be called when the cancel button is clicked    |
| autoSave | Function | The function to be called when the auto save button is clicked |

## Slots

| Name      | Type | Description                      |
| --------- | ---- | -------------------------------- |
| operation | Slot | The operation slot for the table |
| default   | Slot | The default slot for the table   |
| header    | Slot | The header slot for the table    |
| footer    | Slot | The footer slot for the table    |

## Column Props

| Name             | Type      | Description                                         |
| ---------------- | --------- | --------------------------------------------------- |
| field            | String    | The field to be displayed in the table              |
| label            | String    | The label to be displayed in the table              |
| component        | Component | The component to be used for the cell               |
| componentProps   | Object    | The props to be passed to the component             |
| inlineEditActive | Boolean   | Whether the cell is in inline edit mode             |
| controls         | Boolean   | Whether to show the controls                        |
| autoSave         | Boolean   | Whether to auto save the cell                       |
| debounceMs       | Number    | The debounce time in milliseconds                   |
| operation        | Boolean   | Whether to show the operation column                |
| render           | Function  | The function to be called when the cell is rendered |
| align            | String    | The alignment of the cell                           |

## Usage

```ts
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import type { ColumnConfig } from "~/components/TableEdit/types/columnConfig";
import { ElInput, ElDatePicker } from "element-plus";
const columns: ColumnConfig<User>[] = [
  {
    label: "Name",
    field: "name",
    inlineEditActive: false,
    component: ElInput,
    componentProps: {
      // this is the props to be passed to the component
      placeholder: "Enter name",
    },
    controls: true,
    autoSave: true,
    debounceMs: 300,
  },
  {
    label: "Created At",
    field: "created_at",
    component: ElDatePicker, // this is what component in Element Plus we want to use for the cell dont forget to import it
    componentProps: {
      // this is the props to be passed to the component
      format: "DD-MM-YYYY",
      type: "date",
      valueFormat: "YYYY-MM-DD",
    },
    controls: true,
    autoSave: true,
    debounceMs: 300,
  },
];
```
