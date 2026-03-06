# Pagination & Performance Control – Pseudo Tests (GIVEN / WHEN / THEN)

> 📍 File location
> docs/performance/pagination.pseudo.md
>
> Purpose:
> Performance & pagination pseudo-tests written BEFORE implementation.
> This file is a performance & API contract.

> Scope: Tasks Listing Pagination
> Phase: Performance Hardening – Test First
> Status: Red phase (no implementation yet)

---

## 1. Default Pagination Behavior

### Scenario 1.1 — Default Limit & Offset
**GIVEN** a user with multiple tasks in the system

**WHEN** the client sends `GET /api/v1/tasks` without pagination parameters

**THEN** the response status is `200 OK`

**AND** the response contains:
- `items`
- `limit`
- `offset`
- `total`

**AND** the default `limit` is applied

**AND** the default `offset` is `0`

---

## 2. Limit Parameter

### Scenario 2.1 — Valid Limit
**GIVEN** a user with more than 20 tasks

**WHEN** the client sends `GET /api/v1/tasks?limit=10`

**THEN** the response contains at most 10 items

**AND** `limit` in the response equals 10

---

### Scenario 2.2 — Limit Exceeds Maximum
**GIVEN** the maximum allowed limit is 100

**WHEN** the client sends `GET /api/v1/tasks?limit=1000`

**THEN** the request is rejected

**AND** the response status is `422 Unprocessable Entity`

---

### Scenario 2.3 — Negative Limit
**WHEN** the client sends `GET /api/v1/tasks?limit=-5`

**THEN** the request is rejected

**AND** the response status is `422 Unprocessable Entity`

---

## 3. Offset Parameter

### Scenario 3.1 — Valid Offset
**GIVEN** a user with 30 tasks

**WHEN** the client sends `GET /api/v1/tasks?limit=10&offset=10`

**THEN** the response contains the correct next page of results

**AND** `offset` in the response equals 10

---

### Scenario 3.2 — Negative Offset
**WHEN** the client sends `GET /api/v1/tasks?offset=-10`

**THEN** the request is rejected

**AND** the response status is `422 Unprocessable Entity`

---

## 4. Total Count Integrity

### Scenario 4.1 — Total Count Independent of Limit
**GIVEN** a user with 50 tasks

**WHEN** the client sends `GET /api/v1/tasks?limit=10`

**THEN** `total` equals 50

**AND** `len(items)` equals 10

---

## 5. Performance Protection

### Scenario 5.1 — Large Dataset Handling
**GIVEN** a user with a large number of tasks (e.g., 1000)

**WHEN** paginated requests are made

**THEN** only the requested slice is returned

**AND** no full dataset is loaded into memory unnecessarily

---

## 6. Security & Isolation

### Scenario 6.1 — User Data Isolation with Pagination
**GIVEN** multiple users with tasks

**WHEN** one user requests paginated tasks

**THEN** only that user’s tasks are returned

**AND** `total` reflects only that user’s tasks

---

## ✅ Completion Criteria

- Default pagination is applied when no parameters are provided
- Limit is capped to a maximum value
- Negative values are rejected
- Total count is accurate
- Only paginated slice is returned
- No data leakage between users
- All scenarios are converted to automated pytest tests