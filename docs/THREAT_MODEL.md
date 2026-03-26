# Threat Model — Task Manager API

This document describes possible security threats against the system
and the defenses implemented.

---

# 1. System Attack Surface

The API exposes several entry points:

Client
↓
HTTP API
↓
Authentication
↓
Authorization
↓
Business Logic
↓
Database

Potential attack vectors:

- API endpoints
- JWT tokens
- Refresh tokens
- Database queries
- Permission checks

---

# 2. Threat Model Diagram
flowchart TD

Attacker[Attacker]

API[FastAPI API]

Auth[Authentication]

RBAC[Authorization]

Service[Service Layer]

DB[(Database)]

Redis[(Token Blacklist)]

Attacker --> API

API --> Auth
Auth --> RBAC
RBAC --> Service
Service --> DB
Service --> Redis

3. Main Threat Categories
We use a simplified STRIDE model.
Threat
Description
Spoofing
pretending to be another user
Tampering
modifying requests or tokens
Repudiation
denying performed actions
Information Disclosure
leaking data
Denial of Service
overwhelming system
Elevation of Privilege
gaining higher permissions

4. Authentication Threats
Threat: Credential Brute Force
Attack:


attacker → POST /auth/login many times
Defense:


Rate limiting
Constant-time password verification
Generic error messages

5. JWT Threats
Threat: Token Replay
Attack:


stolen JWT reused
Defense:


JWT expiration
Blacklist after logout

6. Refresh Token Theft
Threat:


attacker steals refresh token
Defense:


refresh token hashing
refresh rotation
token family revoke

7. Refresh Token Reuse Attack
Attack:


stolen token reused after refresh
Flow:


attacker → reuse refresh token
Defense:


detect token.used
revoke token family
block request

Diagram

flowchart TD

Reuse[Reuse refresh token]

CheckUsed[Check token.used]

RevokeFamily[Revoke token family]

Reject[Reject request]

Reuse --> CheckUsed
CheckUsed -->|true| RevokeFamily
RevokeFamily --> Reject

8. IDOR Attack
Attack:


user requests task of another user
GET /tasks/123
Defense:


owner_id verification
return 404 instead of 403

Diagram:

flowchart TD

Request[User requests task]

LoadTask[Load task]

CheckOwner[Check owner_id]

ReturnTask[Return task]

Return404[Return 404]

Request --> LoadTask
LoadTask --> CheckOwner

CheckOwner -->|owner match| ReturnTask
CheckOwner -->|not owner| Return404

9. Permission Escalation
Attack:


user tries admin action
Defense:


RBAC permission system
require_permission dependency
AuthorizationService

10. Sensitive Data Exposure
Never logged:


password
access token
refresh token
Logged events:


login attempts
token reuse
permission denied
logout

11. Denial of Service
Possible targets:


login endpoint
refresh endpoint
task listing
Defenses:


rate limiting
pagination limits
MAX_LIMIT enforcement

12. Security Checklist
Control
Implemented
Password hashing
✔
JWT expiration
✔
Token blacklist
✔
Refresh rotation
✔
Token reuse detection
✔
RBAC
✔
Ownership checks
✔
Pagination limits
✔
Structured logging
✔
13. Future Security Improvements
Possible improvements:


device binding for refresh tokens
IP tracking
multi-factor authentication
audit logs
security alerts