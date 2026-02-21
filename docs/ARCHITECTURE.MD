# Project Architecture

## Overview
This project is a **Task Management API** built with **FastAPI** following a clean, layered architecture.
The goal is to provide a secure, testable, and extensible backend suitable for production use and future SaaS expansion.

---

## High-Level Architecture

Request Flow:

Client  
→ API Router  
→ Dependencies (Auth / Permissions)  
→ Service Layer  
→ Storage Layer  
→ Database  
→ Response

No API endpoint accesses the storage layer directly.

---

## Layers Description

### 1. API Layer
Location:
api/vi/endpoint/
Responsibilities:
- Define HTTP routes
- Parse request data
- Call services
- Return responses

Rules:
- No business logic
- No database access
- No security decisions

---

### 2. Dependency Layer
Location:
api/deps/
Responsibilities:
- Authentication (`get_current_user`)
- Authorization (`require_role`)
- Inject services

This layer ensures:
- Centralized security checks
- Reusable permission logic
- Clean endpoints

---

### 3. Service Layer
Location:
services/
Responsibilities:
- Business logic
- Validation
- Authorization rules
- Security decisions

Examples:
- `AuthService`
- `TaskService`

Rules:
- No FastAPI imports
- No HTTP concerns
- Operates on domain models

---

### 4. Models Layer
Location:models/
Responsibilities:
- Define domain objects (User, Task)
- Represent business entities
- Independent of frameworks

---

### 5. Storage Layer
Location:storage/
Responsibilities:
- Persist and retrieve models
- Abstract database implementation

Implementations:
- MemoryStorage (testing)
- SQLiteStorage (local production)

Accessed only via Storage Factory.

---

### 6. Utils Layer
Location:utils/
Responsibilities:
- Password hashing
- JWT creation/verification
- Rate limiting
- Logging

No business logic exists here.

---

## Storage Factory

Single decision point for storage backend:
```python
get_storage()