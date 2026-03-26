# Task Manager API — System Architecture & Flow

This document describes the complete architecture and internal flows of the system.

---

# 1. System Overview

The system is built using a layered architecture.

Client
↓
API Layer
↓
Dependency Layer
↓
Service Layer
↓
Storage Layer
↓
Database / Cache

---

# 2. Layered Architecture

## API Layer

Responsibilities:

- HTTP routing
- Request validation
- Response serialization
- Dependency injection

Examples:

POST /auth/login
POST /tasks
GET /tasks/{id}

---

## Dependency Layer

Handles:

- Authentication
- Authorization
- Service injection

Examples:

get_current_user
require_permission
get_task_service

---

## Service Layer

Contains business logic.

Services:

AuthService
TaskService
TokenService
AuthorizationService

Responsibilities:

- enforce business rules
- enforce security
- coordinate storage
- handle transactions

---

## Storage Layer

Handles database operations.

Implementations:

MemoryStorage
SQLAlchemyStorage

Responsibilities:

- create records
- update records
- fetch records
- delete records

No business logic allowed.

---

# 3. Request Lifecycle

Client Request
↓
FastAPI Router
↓
Dependency Injection
↓
Authentication Dependency
↓
Authorization Check
↓
Service Layer
↓
Storage Layer
↓
Database
↓
Response

---

# 4. Authentication Flow

Client
↓
POST /auth/login
↓
AuthService.login()
↓
verify_password()
↓
TokenService.issue_tokens()
↓
return access + refresh tokens

---

# 5. Token System

Two token types exist.

Access Token
- JWT
- short lived
- used for API authentication

Refresh Token
- secure random token
- stored hashed in database
- rotated after use

---

# 6. Token Lifecycle Diagram

LOGIN
↓
Issue Access Token
↓
Issue Refresh Token
↓
Store Refresh Token Hash

ACCESS REQUEST
↓
Validate JWT
↓
Check blacklist

REFRESH
↓
Hash refresh token
↓
Find token in DB
↓
Check used / revoked
↓
Mark used
↓
Issue new tokens

LOGOUT
↓
Blacklist access token
↓
Revoke refresh token family

---

# 7. Authorization Flow

Client Request
↓
require_permission()
↓
AuthorizationService.check_permission()
↓
ROLE_PERMISSIONS lookup
↓
Access granted / denied

---

# 8. Task Ownership Security

Prevent IDOR attacks.

GET /tasks/{id}

Flow:

fetch task
↓
compare owner_id with requester_id
↓
if mismatch → TaskNotFoundError

---

# 9. Pagination Flow

Client
↓
GET /tasks?limit=20&offset=0
↓
validate limit
↓
validate offset
↓
query database
↓
return items + total

---

# 10. Security Model

Threats prevented:

IDOR
Token replay
Refresh token reuse
Brute force login
Permission escalation

Security controls:

JWT expiration
Token blacklist
Refresh rotation
Permission checks
Password hashing
Rate limiting

---

# 11. Logging Strategy

Important events logged:

User registered
Login success
Login failure
Permission denied
Token reuse detected

Sensitive data NEVER logged:

password
access token
refresh token

---

# 12. Database Entities

User

id
email
password_hash
role
is_active

Task

id
title
description
owner_id
completed
created_at

RefreshToken

id
user_id
token_hash
expires_at
used
revoked
family_id

---

# 13. Error Handling

Domain exceptions used:

AuthenticationError
PermissionDeniedError
TaskNotFoundError
InvalidPaginationError
TokenError

Errors translated to HTTP responses in API layer.

---

# 14. Transaction Model

All database operations are executed inside UnitOfWork.

Example:

with uow as session:
    storage.operation()

UnitOfWork handles commit / rollback.

---

# 15. Future Expansion

Planned features:

Frontend dashboard
Team collaboration
Notifications
AI assistant
Payment system
Chat system