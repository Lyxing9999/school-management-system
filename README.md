# School Management System - Complete Documentation

## System Overview

A comprehensive school management system built with Flask, MongoDB, and Nuxt 3, following Domain-Driven Design (DDD) principles.

### User Roles

- **Admin**: Manages users, classes, subjects, schedules, and system settings
- **Teacher**: Manages assigned classes, attendance, grades, and schedules
- **Student**: Views schedule, attendance, grades, and notifications

### Technology Stack

- **Backend**: Flask (Python) with DDD architecture
- **Frontend**: Nuxt 3 with pnpm
- **Database**: MongoDB
- **API**: REST API
- **Deployment**: Docker Compose

## Module Status

| Module               | Status   |
| -------------------- | -------- |
| IAM (Authentication) | Complete |
| Admin Module         | Complete |
| Teacher Module       | Complete |
| Student Module       | Complete |
| Classes & Subjects   | Complete |
| Attendance Module    | Complete |
| Grades Module        | Complete |
| Notifications Module | Complete |
| Scheduling Module    | Complete |

## Database Collections

### users

Core authentication and user profile data with role-based fields.

```javascript
{
  "_id": ObjectId,
  "email": String,
  "password": String (hashed with scrypt),
  "username": String,
  "role": String (admin|teacher|student),
  "status": String (active|inactive),
  "created_by": ObjectId,
  "lifecycle": {
    "created_at": ISODate,
    "updated_at": ISODate,
    "deleted_at": ISODate | null,
    "deleted_by": ObjectId | null
  }
}
```

### staff

Admin and teacher profiles with extended information.

```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId (ref: users),
  "staff_id": String,
  "staff_name": String,
  "phone_number": String,
  "address": String,
  "role": String (admin|teacher),
  "permissions": Array,
  "created_by": ObjectId,
  "lifecycle": { ... }
}
```

### students

Student profiles with enrollment history and class tracking.

```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId (ref: users),
  "student_id_code": String,
  "first_name_kh": String,
  "last_name_kh": String,
  "first_name_en": String,
  "last_name_en": String,
  "gender": String (Male|Female),
  "dob": ISODate,
  "current_grade_level": Number,
  "current_class_id": ObjectId (ref: classes),
  "photo_url": String | null,
  "phone_number": String,
  "address": Object,
  "guardians": Array,
  "status": String (active|inactive),
  "history": [
    {
      "event": String (STUDENT_CREATED|CLASS_JOINED|CLASS_LEFT),
      "at": ISODate,
      "meta": Object
    }
  ],
  "lifecycle": { ... }
}
```

### classes

Class definitions with student enrollment and subject assignments.

```javascript
{
  "_id": ObjectId,
  "name": String,
  "enrolled_count": Number,
  "subject_ids": [ObjectId] (ref: subjects),
  "max_students": Number,
  "status": String (active|inactive),
  "homeroom_teacher_id": ObjectId (ref: users),
  "lifecycle": { ... }
}
```

### subjects

Subject definitions with grade level restrictions.

```javascript
{
  "_id": ObjectId,
  "name": String,
  "code": String,
  "description": String,
  "allowed_grade_levels": [Number],
  "is_active": Boolean,
  "lifecycle": { ... }
}
```

### assignments

Subject-teacher-class relationships for teaching assignments.

```javascript
{
  "_id": ObjectId,
  "class_id": ObjectId (ref: classes),
  "subject_id": ObjectId (ref: subjects),
  "teacher_id": ObjectId (ref: users),
  "assigned_by": ObjectId (ref: users),
  "lifecycle": { ... }
}
```

### schedule_slots

Time-based schedule with subject and teacher assignments.

```javascript
{
  "_id": ObjectId,
  "class_id": ObjectId (ref: classes),
  "teacher_id": ObjectId (ref: users),
  "subject_id": ObjectId (ref: subjects),
  "day_of_week": Number (0-6, Monday=0),
  "start_time": String (HH:MM),
  "end_time": String (HH:MM),
  "room": String,
  "lifecycle": { ... }
}
```

### attendance

Daily attendance records linked to schedule slots.

```javascript
{
  "_id": ObjectId,
  "student_id": ObjectId (ref: students),
  "class_id": ObjectId (ref: classes),
  "subject_id": ObjectId (ref: subjects),
  "schedule_slot_id": ObjectId (ref: schedule_slots),
  "status": String (present|absent|excused),
  "record_date": String (YYYY-MM-DD),
  "marked_by_teacher_id": ObjectId (ref: users),
  "lifecycle": { ... }
}
```

### grades

Student grades with subject and term tracking.

```javascript
{
  "_id": ObjectId,
  "student_id": ObjectId (ref: students),
  "subject_id": ObjectId (ref: subjects),
  "class_id": ObjectId (ref: classes),
  "teacher_id": ObjectId (ref: users),
  "term": String | null,
  "type": String (exam|assignment|quiz),
  "score": Number (0-100),
  "lifecycle": { ... }
}
```

### notifications

User notifications with routing data.

```javascript
{
  "_id": ObjectId,
  "user_id": String (ref: users),
  "role": String (admin|teacher|student),
  "type": String (CLASS_ASSIGNMENT|GRADE_PUBLISHED|SCHEDULE_CHANGE),
  "title": String,
  "message": String,
  "entity_type": String (class|grade|schedule),
  "entity_id": String,
  "data": {
    "route": String,
    "class_id": String,
    "class_name": String
  },
  "read_at": ISODate | null,
  "created_at": ISODate
}
```

### password_reset_tokens

Temporary tokens for password reset functionality.

```javascript
{
  "_id": ObjectId,
  "user_id": String (ref: users),
  "token_hash": String,
  "created_by": String (ref: users),
  "created_at": ISODate,
  "expires_at": ISODate,
  "used_at": ISODate | null
}
```

### refresh_tokens

JWT refresh token management with revocation support.

```javascript
{
  "_id": ObjectId,
  "user_id": String (ref: users),
  "token_hash": String,
  "created_at": ISODate,
  "expires_at": ISODate,
  "revoked_at": ISODate | null,
  "replaced_by_hash": String | null
}
```

## Key Features

### Authentication & IAM

- JWT-based authentication with access and refresh tokens
- Secure cookie-based refresh token storage
- Password change and reset functionality
- Session management with token revocation
- Role-based access control

### Admin Module

- User management (CRUD, status, soft delete, restore)
- Staff and student profile management
- Class management with homeroom teacher assignment
- Subject management with grade level restrictions
- Subject-to-class assignment system
- Schedule slot creation and management
- Dashboard with system statistics
- Password reset for any user

### Teacher Module

- View assigned classes and students
- Mark attendance with schedule slot context
- Create and manage grades (exam, assignment, quiz)
- Update attendance status
- Soft delete and restore for attendance and grades
- View personal teaching schedule
- Auto-trigger notifications on grade publication

### Student Module

- View enrolled classes
- View personal grades with search and filter
- View attendance history
- View class schedule with teacher and room info
- Receive notifications for grades and class updates

### Notifications System

- Auto-triggered on grade publication (GRADE_PUBLISHED)
- Auto-triggered on class assignment (CLASS_ASSIGNMENT)
- Auto-triggered on schedule changes (SCHEDULE_CHANGE)
- Unread count tracking
- Mark as read functionality
- Read all notifications

### Data Management

- Soft delete with lifecycle tracking
- Restore deleted records
- Hard delete for permanent removal
- Audit history in student records
- Status management (active/inactive)

## API Endpoints

### Authentication (IAM)

```
POST   /api/iam/login
POST   /api/iam/logout
POST   /api/iam/refresh
GET    /api/iam/me
PATCH  /api/iam/me
POST   /api/iam/change-password
POST   /api/iam/reset-password/confirm
```

### Admin - Users & Profiles

```
GET    /api/admin/users
POST   /api/admin/users
PATCH  /api/admin/users/<user_id>
DELETE /api/admin/users/<user_id>
PATCH  /api/admin/users/<user_id>/status
POST   /api/admin/users/<user_id>/restore
DELETE /api/admin/users/<user_id>/hard
POST   /api/admin/users/<user_id>/password-reset

POST   /api/admin/staff
GET    /api/admin/staff/<user_id>
PATCH  /api/admin/staff/<user_id>
GET    /api/admin/staff/teacher-select

POST   /api/admin/students
GET    /api/admin/students/user/<user_id>
PATCH  /api/admin/students/user/<user_id>
GET    /api/admin/students/student-select
```

### Admin - Classes

```
POST   /api/admin/classes
GET    /api/admin/classes
PATCH  /api/admin/classes/<class_id>/teacher
DELETE /api/admin/classes/<class_id>/teacher
POST   /api/admin/classes/<class_id>/students
GET    /api/admin/classes/<class_id>/students
DELETE /api/admin/classes/<class_id>/students/<student_id>
PATCH  /api/admin/classes/<class_id>/status
DELETE /api/admin/classes/<class_id>/soft-delete
GET    /api/admin/classes/names-select
GET    /api/admin/classes/<class_id>/subjects/select
GET    /api/admin/classes/<class_id>/enrollment-student-select/search
PUT    /api/admin/classes/<class_id>/relations
```

### Admin - Subjects & Assignments

```
GET    /api/admin/subjects
POST   /api/admin/subjects
GET    /api/admin/subjects/<subject_id>
PATCH  /api/admin/subjects/<subject_id>
PATCH  /api/admin/subjects/<subject_id>/activate
PATCH  /api/admin/subjects/<subject_id>/deactivate
PATCH  /api/admin/subjects/<subject_id>/soft-delete
GET    /api/admin/subjects/names-select

GET    /api/admin/classes/<class_id>/assignments
POST   /api/admin/classes/<class_id>/assignments
DELETE /api/admin/classes/<class_id>/assignments
```

### Admin - Schedule

```
POST   /api/admin/schedule/slots
GET    /api/admin/schedule/slots/<slot_id>
PATCH  /api/admin/schedule/slots/<slot_id>
DELETE /api/admin/schedule/slots/<slot_id>
PATCH  /api/admin/schedule/slots/<slot_id>/subject
GET    /api/admin/schedule/classes/<class_id>
GET    /api/admin/schedule/teachers/<teacher_id>
GET    /api/admin/schedule/teacher-select
```

### Admin - Dashboard

```
GET    /api/admin/dashboard
```

### Teacher

```
GET    /api/teacher/me/classes
GET    /api/teacher/me/classes/summary
GET    /api/teacher/me/classes/<class_id>/students
GET    /api/teacher/classes/name-select
GET    /api/teacher/me/classes/<class_id>/students/name-select
GET    /api/teacher/me/classes/<class_id>/subjects/name-select

POST   /api/teacher/attendance
PATCH  /api/teacher/attendance/<attendance_id>/status
DELETE /api/teacher/attendance/<attendance_id>
POST   /api/teacher/attendance/<attendance_id>/restore
GET    /api/teacher/classes/<class_id>/attendance

POST   /api/teacher/grades
PATCH  /api/teacher/grades/<grade_id>/score
PATCH  /api/teacher/grades/<grade_id>/type
DELETE /api/teacher/grades/<grade_id>
POST   /api/teacher/grades/<grade_id>/restore
GET    /api/teacher/classes/<class_id>/grades

GET    /api/teacher/schedule
GET    /api/teacher/schedule/slot-select
```

### Student

```
GET    /api/student/me/classes
GET    /api/student/me/attendance
GET    /api/student/me/grades
GET    /api/student/me/schedule
```

### Notifications

```
GET    /api/notifications
GET    /api/notifications/unread-count
POST   /api/notifications/<id>/read
POST   /api/notifications/read-all
POST   /api/notifications/test
```

## Docker Setup

### Docker Compose Configuration

```yaml
version: "3.9"

services:
  frontend:
    container_name: nuxt-frontend-lite-DDD-clean
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - node_modules:/app/node_modules
    environment:
      - NODE_ENV=development
    env_file:
      - ./frontend/.env
    command: ["pnpm", "dev", "--host", "0.0.0.0"]

  backend:
    container_name: flask-backend-lite-DDD-clean
    build: ./backend
    ports:
      - "5001:5000"
    volumes:
      - ./backend:/app
    env_file:
      - ./backend/.env
    environment:
      - PYTHONUNBUFFERED=1
      - FLASK_RUN_HOST=0.0.0.0
    command: ["python", "run.py"]

volumes:
  node_modules:
```

### Running with Docker

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop services
docker-compose down

# Rebuild containers
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- pnpm package manager
- Docker & Docker Compose (optional)

### Local Development Setup

**Backend**:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

**Frontend**:

```bash
cd frontend
pnpm install
cp .env.example .env
pnpm dev
```

**With Docker**:

```bash
docker-compose up
```

Access:

- Frontend: http://localhost:3000
- Backend: http://localhost:5001
- API Docs: http://localhost:5001/api/docs/

## Business Rules

### Attendance

- Only assigned teacher can mark attendance
- Must be linked to a schedule slot
- Cannot mark future dates
- Status: present, absent, excused
- Soft delete with restore capability

### Grading

- Only assigned teacher can create/update grades
- Score range: 0-100
- Type: exam, assignment, quiz
- Auto-triggers GRADE_PUBLISHED notification
- Soft delete with restore capability

### Class Enrollment

- Student can only be enrolled in one class per grade level
- Class has max_students capacity
- Enrollment tracked in student history
- Triggers CLASS_ASSIGNMENT notification

### Schedule Slots

- Conflict detection for teacher availability
- Conflict detection for room booking
- Linked to class, teacher, and subject
- Used for attendance context

### Subject Assignment

- Subject must be active
- Teacher must be active
- One teacher per subject per class
- Managed through assignments collection

## Production Checklist

### Security

- Change all default credentials
- Use strong JWT secrets
- Enable HTTPS/SSL
- Configure CORS properly
- Set secure cookie flags
- Remove debug mode
- Enable rate limiting

### Database

- Create indexes on frequently queried fields
- Setup regular backups
- Configure replica set (recommended)
- Monitor query performance

### Monitoring

- Application logs
- Error tracking (Sentry recommended)
- Performance monitoring
- Database monitoring

### Environment Variables

**Backend (.env)**:

```
DATABASE_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority
SECRET_KEY=your_secret_key_here
# Telegram Bot Token (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
# Google OAuth credentials (optional)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
#Frontend url
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Frontend (.env)**:

```
NUXT_PUBLIC_API_URL=https://api.yourdomain.com
NUXT_PUBLIC_CALENDARIFIC_API_KEY=your_calendarific_api_key_here
```

## Future Enhancements

### Testing

- Unit tests for services and repositories
- Integration tests for API endpoints
- E2E tests for user workflows
- Load testing (1000+ users)

### Features

- System announcements (ANNOUNCEMENT notification type)
- Email notification delivery
- Telegram bot integration
- Mobile app (Flutter)
- Audit trail for all changes
- GPA calculation and reports
- Attendance percentage tracking
- Parent portal

### Architecture

- Hexagonal architecture migration
- Code refactoring (large files)
- Enhanced documentation
- Performance optimization
- Rate limiting implementation

## Contributing

1. Follow DDD architecture patterns
2. Validate all inputs before processing
3. Use lifecycle pattern for soft delete
4. Write meaningful commit messages
5. Request code review

## Support

- Create issues in repository
- Contact development team

---

**Version**: 1.0.0 (Production Ready)  
**Last Updated**: January 2026  
**Database Collections**: 11+  
**API Endpoints**: 80+
