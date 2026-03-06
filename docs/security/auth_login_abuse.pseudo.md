# Authentication & Login Abuse – Pseudo Tests (GIVEN / WHEN / THEN)

> 📍 File location
> docs/security/auth_login_abuse.pseudo.md
>
> Purpose:
> Security pseudo-tests written BEFORE implementation.
> This file is a test & security contract.

> Scope: Authentication & Login Security
> Phase: Security Hardening – Test First
> Status: Red phase (no implementation yet)

---

## 1. Login – Valid Credentials

### Scenario 1.1 — Successful Login
**GIVEN** a registered user with correct email and password

**WHEN** the client sends `POST /auth/login`

**THEN** the response status is `200 OK`

**AND** an access token is returned

**AND** no sensitive information is included in the response

---

## 2. Login – Invalid Credentials

### Scenario 2.1 — Wrong Password
**GIVEN** a registered user

**WHEN** the client submits a valid email with a wrong password

**THEN** the response status is `401 Unauthorized`

**AND** the error message is generic

---

### Scenario 2.2 — Non-existing Email (Enumeration Protection)
**GIVEN** no user exists with the provided email

**WHEN** the client submits a login request

**THEN** the response status is `401 Unauthorized`

**AND** the error message is identical to Scenario 2.1

**AND** no indication is given whether the email exists

---

## 3. Brute Force Protection (Conceptual)

### Scenario 3.1 — Multiple Failed Attempts
**GIVEN** repeated failed login attempts from the same source

**WHEN** the failure threshold is exceeded

**THEN** further login attempts are blocked or delayed

---

### Scenario 3.2 — Mixed Email Attempts
**GIVEN** multiple login attempts with different emails from the same source

**WHEN** the rate limit is exceeded

**THEN** the source is temporarily blocked

---

## 4. Timing Attack Resistance

### Scenario 4.1 — Existing vs Non-existing Email
**GIVEN** a valid email and an invalid email

**WHEN** login attempts are made

**THEN** the response time difference is not significant

---

## 5. Error Message Consistency

### Scenario 5.1 — Error Uniformity
**GIVEN** any login failure

**WHEN** the API responds

**THEN** the error message does not reveal:
- whether the email exists
- whether the password was wrong
- internal validation logic

---

## 6. Logging & Monitoring

### Scenario 6.1 — Failed Login Logged
**GIVEN** a failed login attempt

**WHEN** it occurs

**THEN** a security log entry is created

**AND** no password or token data is logged

---

### Scenario 6.2 — Successful Login Logged
**GIVEN** a successful login

**WHEN** it occurs

**THEN** a login event is logged without sensitive data

---

## 7. Account Lockout (Optional / Configurable)

### Scenario 7.1 — Temporary Lockout
**GIVEN** excessive failed login attempts for a single account

**WHEN** the lockout threshold is reached

**THEN** further attempts are rejected for a limited time

---

## 8. Token Issuance Safety

### Scenario 8.1 — Token Only on Success
**GIVEN** a failed login attempt

**WHEN** the response is returned

**THEN** no access token is generated

---

## ✅ Completion Criteria
- All scenarios are converted to automated tests
- Error responses are consistent
- No user enumeration possible
- Brute force paths are covered by tests