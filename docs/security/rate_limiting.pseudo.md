# Rate Limiting & Abuse Control – Pseudo Tests (GIVEN / WHEN / THEN)

> 📍 File location
> docs/security/rate_limiting.pseudo.md
>
> Purpose:
> Define rate limiting & abuse protection rules.
> This file is a security contract written BEFORE implementation.

> Scope: Global & Endpoint-level Rate Limiting
> Phase: Security Hardening – Test First
> Status: Red phase (no implementation yet)

---

## 1. Global Rate Limiting

### Scenario 1.1 — Excessive Requests from Single IP
**GIVEN** a single IP address

**WHEN** it sends requests exceeding the global rate limit

**THEN** further requests are rejected with a rate limit error

**AND** the service remains available for other users

---

### Scenario 1.2 — Distributed Normal Traffic
**GIVEN** multiple IPs sending requests within allowed limits

**WHEN** traffic is processed

**THEN** no request is blocked

---

## 2. Login Rate Limiting

### Scenario 2.1 — Repeated Failed Login Attempts
**GIVEN** repeated failed login attempts from the same IP

**WHEN** the login rate limit threshold is exceeded

**THEN** further login attempts are blocked temporarily

---

### Scenario 2.2 — Successful Login Resets Counter
**GIVEN** failed login attempts from an IP

**WHEN** a successful login occurs

**THEN** the failure counter is reset or reduced

---

## 3. Password Reset Rate Limiting

### Scenario 3.1 — Excessive Reset Requests
**GIVEN** repeated password reset requests from the same IP or email

**WHEN** the threshold is exceeded

**THEN** further reset requests are blocked or delayed

---

### Scenario 3.2 — Enumeration Protection
**GIVEN** reset requests for multiple different emails from the same IP

**WHEN** the rate limit is exceeded

**THEN** requests are blocked

**AND** no information about email existence is leaked

---

## 4. Registration Rate Limiting

### Scenario 4.1 — Account Creation Abuse
**GIVEN** repeated registration attempts from the same IP

**WHEN** the registration limit is exceeded

**THEN** further registrations are blocked

---

## 5. Rate Limit Response Consistency

### Scenario 5.1 — Standard Rate Limit Error
**GIVEN** a request blocked by rate limiting

**WHEN** the API responds

**THEN** the response status indicates rate limiting (e.g. 429)

**AND** the error message is generic

**AND** no internal limit values are exposed

---

## 6. Time Window Handling

### Scenario 6.1 — Fixed or Sliding Window
**GIVEN** a rate limit window

**WHEN** the window expires

**THEN** the request counter resets automatically

---

## 7. Whitelisting & Internal Access

### Scenario 7.1 — Internal Services
**GIVEN** a trusted internal service or admin IP

**WHEN** it sends requests

**THEN** rate limiting rules may be relaxed or bypassed

---

## 8. Logging & Monitoring

### Scenario 8.1 — Rate Limit Events Logged
**GIVEN** a request blocked by rate limiting

**WHEN** it occurs

**THEN** a security log entry is created

**AND** the log does not contain sensitive request data

---

## 9. Abuse Resilience

### Scenario 9.1 — Rate Limit Bypass Attempts
**GIVEN** an attacker attempting to bypass rate limits

**WHEN** abnormal patterns are detected

**THEN** requests are throttled or blocked

---

## ✅ Completion Criteria
- Rate limiting rules are defined per endpoint
- Abuse scenarios are covered by tests
- Error responses are consistent
- No user enumeration or leakage via rate limiting