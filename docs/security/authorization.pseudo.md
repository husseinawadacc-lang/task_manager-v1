# Access Control & Authorization – Pseudo Tests (GIVEN / WHEN / THEN)

> 📍 File location
> docs/security/authorization.pseudo.md
>
> Purpose:
> Define authorization & access control rules BEFORE implementation.
> This file is a security contract and test specification.

> Scope: Resource Ownership & Permissions
> Phase: Security Hardening – Test First
> Status: Red phase (no implementation yet)

---

## 1. Authentication Required

### Scenario 1.1 — Access Without Token
**GIVEN** no authentication token is provided

**WHEN** a protected endpoint is accessed

**THEN** access is denied

**AND** the response indicates authentication is required

---

### Scenario 1.2 — Invalid Token
**GIVEN** an invalid or expired token

**WHEN** a protected endpoint is accessed

**THEN** access is denied

---

## 2. Resource Ownership

### Scenario 2.1 — Access Own Resource
**GIVEN** an authenticated user

**AND** the resource belongs to that user

**WHEN** the resource is accessed

**THEN** access is granted

---

### Scenario 2.2 — Access Other User Resource
**GIVEN** an authenticated user

**AND** the resource belongs to a different user

**WHEN** the resource is accessed

**THEN** access is denied

---

## 3. Create Permissions

### Scenario 3.1 — Create Own Resource
**GIVEN** an authenticated user

**WHEN** creating a new resource

**THEN** the resource is created

**AND** ownership is assigned to that user

---

## 4. Update Permissions

### Scenario 4.1 — Update Own Resource
**GIVEN** an authenticated user

**AND** the resource belongs to that user

**WHEN** the user updates the resource

**THEN** the update is allowed

---

### Scenario 4.2 — Update Other User Resource
**GIVEN** an authenticated user

**AND** the resource belongs to another user

**WHEN** the user attempts to update it

**THEN** the update is denied

---

## 5. Delete Permissions

### Scenario 5.1 — Delete Own Resource
**GIVEN** an authenticated user

**AND** the resource belongs to that user

**WHEN** the user deletes the resource

**THEN** the deletion is allowed

---

### Scenario 5.2 — Delete Other User Resource
**GIVEN** an authenticated user

**AND** the resource belongs to another user

**WHEN** the user attempts to delete it

**THEN** the deletion is denied

---

## 6. Horizontal Privilege Escalation Protection

### Scenario 6.1 — ID Manipulation
**GIVEN** an authenticated user

**WHEN** the user manipulates a resource ID in the request

**THEN** access is denied

---

## 7. Admin or Special Roles (Optional)

### Scenario 7.1 — Admin Access
**GIVEN** a user with admin privileges

**WHEN** accessing restricted resources

**THEN** access is granted according to role rules

---

### Scenario 7.2 — Non-admin Access
**GIVEN** a regular user

**WHEN** accessing admin-only resources

**THEN** access is denied

---

## 8. Error Response Consistency

### Scenario 8.1 — Authorization Errors
**GIVEN** an authorization failure

**WHEN** the API responds

**THEN** the error message is generic

**AND** does not leak ownership or permission logic

---

## 9. Logging & Audit

### Scenario 9.1 — Authorization Failure Logged
**GIVEN** an authorization failure

**WHEN** it occurs

**THEN** a security log entry is created

**AND** no sensitive data is logged

---

## 10. Defense in Depth

### Scenario 10.1 — Service Layer Enforcement
**GIVEN** a protected operation

**WHEN** called from any layer

**THEN** authorization is enforced at the service layer

---

## ✅ Completion Criteria
- All protected endpoints require authentication
- Resource ownership is strictly enforced
- No horizontal privilege escalation possible
- Authorization rules are testable and centralized