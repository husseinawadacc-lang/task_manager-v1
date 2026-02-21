---

# 🔐 2️⃣ docs/SECURITY.md

انسخ الملف ده أيضًا:

```md
# Security Architecture

## Security Goals

- Prevent unauthorized access
- Protect user credentials
- Avoid information leakage
- Defend against brute-force and abuse
- Ensure secure token handling

---

## Authentication

Method:
- JWT (JSON Web Token)

Token Types:
- Access Token (short-lived)
- Refresh Token (longer-lived)

Stored client-side only.

---

## Password Security

- Passwords are never stored in plain text
- Hashing algorithm: **bcrypt**
- Pepper applied from environment variable
- Password strength enforced

---

## JWT Security

- Signed with SECRET_KEY from environment
- Expiration enforced
- Payload contains only:
  - user_id
  - token type
- No sensitive data inside token

---

## Rate Limiting

Applied on:
- Login endpoint

Strategy:
- Per IP + email
- Time window based
- Automatic reset on success

Purpose:
- Prevent brute-force attacks
- Mitigate credential stuffing

---

## Authorization

Roles:
- user
- admin

Enforced via:
- Dependency layer
- Service layer checks

No role logic inside endpoints.

---

## Error Handling

- Centralized exception handlers
- Generic error messages
- No user enumeration
- Same error for invalid email or password

---

## Abuse Protection

Handled scenarios:
- Invalid tokens
- Expired tokens
- Rate limit exceeded
- Unauthorized access
- Cross-user task access

---

## Environment Security

Secrets stored in:
- `.env` (local)
- Railway environment variables (production)

Never committed to GitHub.

---

## Known Limitations (v1)

- No token rotation
- No session revocation
- No device fingerprinting

Planned for v2.

---

## Security Review Status

✔ Authentication  
✔ Authorization  
✔ Rate limiting  
✔ Password security  
✔ Token expiration  

