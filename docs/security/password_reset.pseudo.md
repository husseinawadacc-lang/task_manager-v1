# Password Reset Flow – Pseudo Tests (GIVEN / WHEN / THEN)

> 📍 File location
> docs/security/password_reset.pseudo.md
>
> Purpose:
> Security pseudo-tests written BEFORE implementation.
> This file is a security & test contract.

> Scope: Password Reset Flow
> Phase: Security Hardening – Test First
> Status: Red phase (no implementation yet)

---

## 1. Request Password Reset

### Scenario 1.1 — Existing Email
**GIVEN** a registered user with email `user@example.com`

**WHEN** the client sends `POST /auth/password-reset/request`

**THEN** the response status is `200 OK`

**AND** the response body is generic

**AND** a reset token is generated and stored securely

---

### Scenario 1.2 — Non-existing Email (Enumeration Protection)
**GIVEN** no user exists with email `ghost@example.com`

**WHEN** the client sends a password reset request

**THEN** the response status is `200 OK`

**AND** the response body is identical to Scenario 1.1

**AND** no indication is given whether the email exists

---

## 2. Reset Token Generation

### Scenario 2.1 — Token Security
**GIVEN** a password reset request is accepted

**WHEN** a reset token is generated

**THEN** the token:
- is cryptographically random
- has sufficient length
- cannot be guessed

---

### Scenario 2.2 — Token Storage
**GIVEN** a reset token is generated

**WHEN** it is stored

**THEN** only the hashed token is persisted

**AND** the raw token is never stored

---

## 3. Token Expiration

### Scenario 3.1 — Valid Token
**GIVEN** a valid unused reset token

**AND** the current time is before expiration

**WHEN** the client submits password reset confirmation

**THEN** the token is accepted

---

### Scenario 3.2 — Expired Token
**GIVEN** an expired reset token

**WHEN** it is submitted

**THEN** the request is rejected

**AND** the password is not changed

---

## 4. One-Time Token Usage

### Scenario 4.1 — First Use
**GIVEN** a valid unused reset token

**WHEN** it is submitted with a strong new password

**THEN** the password is updated

**AND** the token is marked as used

---

### Scenario 4.2 — Token Reuse Attempt
**GIVEN** a reset token already used

**WHEN** it is submitted again

**THEN** the request is rejected

**AND** no password change occurs

---

## 5. Invalid Token Handling

### Scenario 5.1 — Random Token
**GIVEN** a random invalid token

**WHEN** it is submitted

**THEN** the request is rejected

**AND** the error message is generic

---

## 6. Password Policy Enforcement

### Scenario 6.1 — Weak Password
**GIVEN** a valid reset token

**WHEN** a weak password is submitted

**THEN** the request is rejected

---

### Scenario 6.2 — Strong Password
**GIVEN** a valid reset token

**WHEN** a strong password is submitted

**THEN** the password is updated successfully

---

## 7. Logging & Security

### Scenario 7.1 — Reset Events Logged
**GIVEN** a password reset request or confirmation

**WHEN** it occurs

**THEN** a security log entry is created

**AND** no sensitive data (passwords, tokens) is logged

---

## 8. Rate Limiting (Conceptual)

### Scenario 8.1 — Excessive Requests
**GIVEN** repeated reset requests from the same source

**WHEN** the rate limit is exceeded

**THEN** further requests are blocked

---

## ✅ Completion Criteria
- No email enumeration possible
- Tokens are one-time and time-limited
- Password policy is enforced
- All scenarios can be converted to pytest tests