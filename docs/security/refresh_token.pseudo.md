# Refresh Token Lifecycle – Pseudo Tests (GIVEN / WHEN / THEN)

> Scope: Authentication – Refresh Tokens
> Phase: Security Hardening – Test First
> Status: Pseudo / Specification

---

## 1. Refresh Token – Valid

### Scenario 1.1 — Valid Refresh Issues New Access Token
GIVEN a user with a valid refresh token  
WHEN the refresh endpoint is called  
THEN the response status is 200 OK  

AND a new access token is returned  
AND the access token is different from the previous one  

---

## 2. Refresh Token – Missing

### Scenario 2.1 — Missing Refresh Token
GIVEN no refresh token  
WHEN the refresh endpoint is called  
THEN the response status is 401 Unauthorized  

---

## 3. Refresh Token – Expired

### Scenario 3.1 — Expired Refresh Token Rejected
GIVEN an expired refresh token  
WHEN it is used  
THEN the response status is 401 Unauthorized  

AND the user must re-authenticate  

---

## 4. Refresh Token – Invalid / Tampered

### Scenario 4.1 — Invalid Refresh Token
GIVEN a malformed or tampered refresh token  
WHEN it is used  
THEN the response status is 401 Unauthorized  

AND no token information is leaked  

---

## 5. Refresh Token – Replay (Reuse Attack)

### Scenario 5.1 — Used Refresh Token Rejected
GIVEN a refresh token that was already used  
WHEN it is used again  
THEN the response status is 401 Unauthorized  

AND the session is invalidated  

---

## 6. Token Type Safety

### Scenario 6.1 — Access Token Used as Refresh Token
GIVEN an access token  
WHEN it is sent to the refresh endpoint  
THEN the response status is 401 Unauthorized  

---

## 7. Error Consistency

### Scenario 7.1 — Uniform Error Responses
GIVEN any refresh token failure  
WHEN the API responds  
THEN error messages do not reveal:
- token expiration details
- token type
- internal validation logic

---

## ✅ Completion Criteria
- Refresh tokens cannot be reused
- Expired tokens are rejected
- Access tokens cannot refresh sessions
- New access tokens are always rotated