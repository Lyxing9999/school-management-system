# 🏛️ Frontend Architecture: Admin Module Flow

## 🌟 Overview

This frontend utilizes a **modular and consistent architecture** designed to support small-to-large scale applications. It strictly follows a **Registry → Service → API pattern** for maintainable and scalable code across all entity modules.

The primary goal is to **separate concerns** and ensure that components, services, and APIs are consistent. This allows new modules or entities to be added with minimal (or zero) changes to existing components.

---

## 📂 Folder Structure

The core structure is organized to reflect the architectural layers:

```

src/
├─ api/                 \# Low-level API interfaces (Axios) for each module
│  ├─ admin/
│  │  ├─ class/
│  │  │  ├─ api.ts      \# Axios calls for class module
│  │  │  ├─ dto.ts      \# Data transfer types for class module
│  │  │  └─ service.ts  \# Optional: additional business logic/pre-processing
│  │  ├─ staff/
│  │  ├─ student/
│  │  ├─ subject/
│  │  └─ user/
├─ services/            \# High-level service layer (business logic, safe API wrapping)
│  └─ formServices/
│     └─ adminFormService.ts
├─ schemas/             \# Form schemas (Yup/Zod) and default data initializers
│  └─ forms/admin/
├─ utils/               \# Utilities, e.g., centralized safe API call wrapper
└─ components/          \# Vue/UI components (view layer)

```

---

## 🔄 Service Flow Explained

### 1️⃣ API Layer (Lowest Level)

- **Function:** Handles raw **HTTP requests** via Axios.
- **Structure:** Each module (User, Class, Staff, Subject, Student) has its own dedicated API class (e.g., `ClassApi`).
- **Example:** `ClassApi` methods include `createClass`, `updateClass`, `getClassById`, `assignStudent`, etc.

### 2️⃣ Service Layer (Business Logic)

- **Function:** Wraps the raw API calls with crucial features.
- **Key Responsibilities:**
  - **Safe API Handling:** Implements success/error notifications or logging.
  - **Business Logic:** Handles any domain-specific data manipulation or checks needed before or after the API call.
- **Example:** `ClassService` wraps `ClassApi` methods:
  ```typescript
  const { data } = await this.safeApiCall(this.classApi.createClass(classData));
  return data!;
  ```

### 3️⃣ Registry Layer (Decoupling)

- **Function:** Serves as the central mapping layer, preventing components from needing to know specific service names.
- **Mapping:** Maps entity types (**`USER`**, **`STAFF`**, **`CLASS`**, etc.) to:
  - The Service instance.
  - The Form Schema (Yup/Zod).
  - The Form Data Initializer.
- **Implementation:** Uses two main registry objects:
  - `formRegistryCreate` (for creating new entities)
  - `formRegistryEdit` (for editing existing entities)

### 4️⃣ Component Usage (Highest Level)

- **Rule:** Components **must not** call the API or Service directly.
- **Process:** Components retrieve the necessary service and data structures from the Registry.
- **Example Usage:**

  ```typescript
  // Component is requesting resources for a 'CLASS' entity
  const registryItem = formRegistryCreate['CLASS'];

  // Get default data and service instance from the registry
  const formData = registryItem.formData();
  const service = registryItem.service;

  // Use the service retrieved from the registry
  service.createClass(formData).then(...)
  ```

---

## ✅ Benefits of this Architecture

| Principle           | Description                                                                                                                      |
| :------------------ | :------------------------------------------------------------------------------------------------------------------------------- |
| **Consistency**     | All modules follow the same predictable flow (`API` → `Service` → `Registry` → `Component`), easing developer onboarding.        |
| **Scalability**     | The clear structure benefits small projects and ensures large projects can grow without side effects or breaking changes.        |
| **Maintainability** | Services centralize business logic and error handling. The Registry decouples the component from service implementation details. |
| **Testability**     | Services can be easily mocked for unit testing, and APIs can be tested independently.                                            |
| **Decoupling**      | Components are only aware of the Registry, not the specific service implementations, leading to cleaner code.                    |

---

## 🏗️ Procedure: Adding a New Module

Adding a new entity (e.g., `COURSE`) is a predictable, four-step process:

1.  **Create API:** Define the raw HTTP calls.
    - `src/api/admin/course/api.ts`
    - `src/api/admin/course/dto.ts`
2.  **Create Service:** Wrap the API with safe handling and business logic.
    - `src/services/formServices/courseService.ts`
3.  **Add Form Assets:** Define the validation and initial data.
    - `src/schemas/forms/admin/courseForm.ts`
4.  **Register:** Link all assets in the central registry.
    ```typescript
    formRegistryCreate["COURSE"] = {
      service: serviceCourse,
      schema: courseFormSchema,
      formData: () => ({
        /* initial data object */
      }),
    };
    ```

---
