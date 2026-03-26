
# 🚀 TaskForge (Secure SaaS Task Management System)

TaskForge is a production-ready task management system built with FastAPI and React.

> Build, organize, and scale your work.
---

✨ Features

- 🔐 JWT Authentication (Access + Refresh)
- 🚪 Secure Logout (Token Blacklisting with Redis)
- 👥 Project & Members Management
- 🛡 Role-Based Access Control (RBAC)
  - Owner / Admin / Member / Viewer
- 📂 Task Management System
- 🧾 Audit Logging
- ⚡ Rate Limiting (Abuse Protection)
- 🔒 Anti-IDOR Protection (NotFound masking)

---

🏗 Architecture

This project follows Clean Architecture principles:

- Service Layer (Business Logic)
- Repository Pattern (Storage abstraction)
- Unit of Work (Transaction management)
- Dependency Injection
- Separation of concerns

---

🔐 Security Highlights

- JWT validation (issuer, audience, expiration)
- Token revocation (Blacklist via Redis)
- Refresh token handling
- Anti-IDOR protection
- Rate limiting against abuse
- Password policy enforcement

---

🛠 Tech Stack

Backend

- FastAPI
- PostgreSQL / SQLite (dev)
- SQLAlchemy
- Redis

Frontend

- React (Vite)

---

📚 Documentation

Detailed system design and security documentation:

- docs/SYSTEM_ARCHITECTURE_AND_FLOW.md
- docs/THREAT_MODEL.md
- docs/SYSTEM_PSEUDO_TESTS.md
- docs/ENTERPRISE_ARCHITECTURE.md

---

▶️ Run Locally

1. Clone repository

git clone https://github.com/your-username/task-manager.git
cd task-manager

2. Backend

pip install -r requirements.txt
uvicorn main:app --reload

3. Frontend

cd frontend
npm install
npm run dev

---

📄 API Documentation

Swagger UI:

http://127.0.0.1:8000/docs

---

🧪 Testing

Includes:

- Security tests (RBAC, JWT, Rate limiting)
- Storage tests
- Abuse scenarios

Run tests:

pytest

---

🚀 Future Improvements

- SaaS Billing Integration (Stripe)
- Notifications system
- AI-powered assistant (task suggestions, automation)
- Real-time collaboration (WebSockets)

---

👤 Author

Hussein Awad

---

⭐ Notes

This project is built as a production-level backend system, not just a CRUD demo.
It focuses on real-world security practices and scalable architecture.