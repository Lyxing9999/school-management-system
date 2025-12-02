# School Management System – Backend

A Flask-based backend for managing schools, built with MongoDB and a clean, context-driven architecture. Designed for maintainability and scalability.

---

## Overview

This backend provides APIs for managing:
- **Students** – enrollment, profiles, academic records
- **Teachers** – assignments, schedules, class management
- **Classes & Subjects** – sections, capacities, subject metadata
- **Schedules** – timetables, slots, teacher assignments
- **Attendance & Grades** – tracking and reporting
- **Users & Staff** – authentication, roles, permissions

---

## Architecture

### Context-Based Design

The system is organized into bounded contexts, each owning its domain:

- **`admin/`** – Admin dashboard APIs (CRUD for users, staff, classes, schedules)
- **`school/`** – Core domain (ClassSection, Schedule, Attendance, Grade, Enrollment)
- **`teacher/`** – Teacher-facing features
- **`student/`** – Student-facing features
- **`iam/`** – Identity & Access Management (JWT, roles, permissions)
- **`staff/`** – Staff profiles and metadata
- **`auth/`** – Authentication utilities
- **`shared/`** – Cross-cutting concerns (DTOs, display names, decorators)
- **`core/`** – Security, error handling
- **`infra/`** – Database, configuration
- **`jobs/`** – Background tasks

### Separation of Concerns

Each context follows a layered structure:

```
context/
  routes/         # HTTP layer (Flask blueprints)
  services/       # Application logic (orchestration)
  domain/         # Business rules (aggregates, entities)
  repositories/   # Data persistence (MongoDB)
  read_models/    # Optimized queries for views
  data_transfer/  # Request/response DTOs
  mapper/         # Domain ↔ DTO conversion
  errors/         # Context-specific exceptions
```

**Key principles:**
- Routes handle HTTP only – no business logic
- Services orchestrate use cases
- Domain enforces business rules
- Read models optimize queries without mixing business logic
- Soft delete for core entities (users, classes, staff)

---

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

2. **Configure environment:**  
   Create `.env` in `Backend/`:
   ```env
   FLASK_ENV=development
   MONGO_URI=mongodb://localhost:27017/school_db
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   ```

3. **Run the server:**
   ```bash
   python run.py
   ```

   API available at `http://localhost:5001`

### Docker

From the repository root:

```bash
docker-compose up --build
```

This starts:
- Flask backend
- Nuxt frontend (admin panel)
- MongoDB

---

## Project Structure

```
Backend/
  app/
    contexts/       # Bounded contexts
      admin/
      school/
      teacher/
      student/
      iam/
      staff/
      ...
  run.py            # Application entry point
  requirements.txt
  Dockerfile
  admin.http        # HTTP request samples (admin)
  teacher.http      # HTTP request samples (teacher)
  pytest.ini
```

---

## Adding Features

1. **Domain logic** → `app/contexts/{context}/domain/`
2. **Application logic** → `app/contexts/{context}/services/`
3. **HTTP endpoints** → `app/contexts/{context}/routes/`
4. **Queries** → `app/contexts/{context}/read_models/`
5. **Enrich views** → Use `AdminReadModel` + `DisplayNameService` for joined data

**Never:**
- Put database queries in routes
- Put business logic in repositories
- Skip DTOs when returning data to clients

---

## Testing

Run tests with pytest:

```bash
pytest
```

Test files are co-located within each context under `tests/`.

---

## API Documentation

Sample requests are provided in:
- `admin.http` – Admin operations
- `teacher.http` – Teacher operations

Use tools like REST Client (VS Code) or Postman to test endpoints.

---

## Design Goals

- **Separation of concerns** – HTTP, application, domain, and data layers are isolated
- **Testability** – Each layer can be tested independently
- **Scalability** – Add contexts and features without restructuring
- **Read/write separation** – Commands (writes) and queries (reads) use different paths
- **Soft delete** – Preserve data integrity with logical deletes

---

## Contributing

When adding features:
1. Follow the existing context structure
2. Use DTOs for all API boundaries
3. Keep domain logic pure (no I/O)
4. Enrich read views via `AdminReadModel` when cross-context data is needed
5. Write tests for services and domain logic

---

