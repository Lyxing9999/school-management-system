# School Management System – Backend

A modular and scalable backend for a School Management System, built with **Flask**, **MongoDB**, and a clean **Service → Route → Response** architecture.  
The goal is to create a maintainable, production-ready backend with strong separation of concerns.

---

## 🚧 Development Status

**Backend Progress: ~30% Completed**

- ✅ Admin module (CRUD, user management)
- ✅ Authentication skeleton
- ✅ Database models (Pydantic + MongoDB)
- ✅ IAM module
- 🔄 Teacher module – IN PROGRESS
- 🔄 School module – IN PROGRESS
- 🔄 Academic module – IN PROGRESS
- ⏳ Student module – NOT STARTED

---

## 🔧 Tech Stack

- **Flask** (Blueprint modular architecture)
- **MongoDB** (PyMongo)
- **Pydantic** for validation
- **Layered Architecture**
  - Routes → handle HTTP + validate DTOs
  - Services → business logic
  - Repositories → database access
  - Models → define pure OOP domain objects and business rules (no DB access)
- **Docker** support
- CORS, JWT-ready
- Future-proof permission system

---

## 📁 Project Structure
```
app/
├─ contexts/
│  ├─ admin/          ✅ DONE
│  │  ├─ routes.py
│  │  ├─ services.py
│  │  ├─ models.py
│  │  ├─ repository.py
│  │  ├─ read_models.py
│  │  ├─ data_transfer/
│  │  ├─ error/
│  │  └─ tests/
│  ├─ teacher/        🔄 IN PROGRESS
│  ├─ student/        ⏳ NOT STARTED
│  ├─ academic/       🔄 IN PROGRESS
│  ├─ school/         🔄 IN PROGRESS
│  ├─ iam/            ✅ DONE
│  └─ core/
│     ├─ security/
│     └─ placeholder/
├─ uploads/
├─ __init__.py
run.py
requirements.txt
Dockerfile
```

### Why This Structure Works

- Each context is fully isolated
- Routes only handle HTTP
- Services contain business logic
- Models define domain objects (pure OOP, business rules)
- Easy to add new contexts with no breaking changes

---

## ✨ Features (Current & Planned)

✔ Admin/Teacher/Student roles  
✔ Modular Blueprints  
✔ Class & Schedule management  
✔ Grading workflow  
✔ Attendance tracking  
✔ Telegram bot integration ready  
✔ Dynamic permissions (future-ready)  

---

## 🚀 Running the Backend

### Local Development
```bash
pip install -r requirements.txt
python run.py
```

### Docker
```bash
docker build -t school-backend .
docker run -p 5000:5000 --env-file .env school-backend
```

Or with Compose:
```bash
docker-compose up --build
```

Backend runs at: **http://localhost:5001**

---

## ⚙️ Environment Variables

Create a `.env` file:
```bash
FLASK_ENV=development
MONGO_URI=mongodb://localhost:27017/school_db
SECRET_KEY=your-secret-key
```

---

## 📡 Example API Endpoints
```
GET  /api/admin/users
POST /api/admin/create-user
PUT  /api/teacher/grade
GET  /api/academic/classes
```

Use **Postman** or **Thunder Client** for testing.

---

## 🧪 Tests

Each context has its own tests:
```
app/contexts/<context>/tests/
```

---

## 📘 Developer Notes

This backend follows:

- **Clean Architecture**
- No business logic in routes
- No raw DB logic in routes
- Services are the "brain"
- Pydantic for strong typing
- Context-based modularity

---

## ⚠️ Common Issues

**MongoDB connection error:**
- Check your `.env`
- Make sure MongoDB is running

**Port already in use:**
- Change port in `run.py`
- Or kill the conflicting process

---

