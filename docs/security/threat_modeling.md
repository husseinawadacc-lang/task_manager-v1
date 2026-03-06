# Threat Modeling – v2

## Project
Task Manager – v2

## Status
Security Review Phase – Threat Modeling (Completed)

---

## 1. Scope

### In Scope
- Authentication (existing – v1 frozen)
- Authorization (existing – v1 frozen)
- Password Reset (planned) pass
- Refresh Token Rotation (planned) pass
- Pagination & Performance Controls (planned)pass
- Database Upgrade (SQLite → PostgreSQL)
###Authorization Model (v2):(plannes)
- Owner-based access only
- Role field reserved for future RBAC
- Admin privileges intentionally deferred until post-PostgreSQL
### Out of Scope (for now)
- AI features
- Payments
- Multi-tenant SaaS
- Real-time collaboration

---

## 2. Assets

| Asset | Description | Risk |
|----|----|----|
User Accounts | User identity & access | High |
Passwords | Credential takeover | High |
Reset Tokens | Account takeover | High |
JWT / Refresh Tokens | Session hijacking | High |
Tasks Data | Data exposure / corruption | Medium |
Database | Data loss / integrity | High |

---

## 3. Attack Surfaces

- Public API endpoints
- Token lifecycle logic
- Password reset flows
- Pagination & listing endpoints
- Database constraints & queries

---

## 4. Threat Scenarios

### Authentication & Account Recovery
- Password reset enumeration
- Reset token brute force
- Reuse of reset tokens
- Long-lived reset links

### Token Abuse
- Refresh token replay
- Token theft & reuse
- Access token misuse

### Authorization
- IDOR via pagination
- Cross-user access
- Forced browsing

### Abuse & Performance
- Pagination scraping
- Resource exhaustion
- Rate limit bypass

---

## 5. Risk Assessment

| Threat | Likelihood | Impact | Priority |
|----|----|----|----|
Password reset abuse | High | High | 🔴 |
Refresh token replay | Medium | High | 🔴 |
Pagination scraping | Medium | Medium | 🟠 |
DB integrity issues | Low | High | 🟠 |

---

## 6. Security Decisions (Binding)

- No password reset enumeration
- Reset tokens must be:
  - One-time use
  - Time-limited
  - Unlinkable to user existence
- Refresh tokens must support rotation
- Pagination must enforce limits
- Authorization must be enforced at query level
- All security errors must be generic

---

## 7. Explicit Non-Goals

- No long-lived access tokens
- No implicit admin privileges
- No reset tokens stored in plaintext
- No feature implementation without tests

---

## 8. Outcome

Threat Modeling completed.
Implementation is blocked until Roadmap approval.