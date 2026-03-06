# v2 Roadmap (Security-First)

## Rules
- No feature starts without pseudo tests
- No implementation before failing tests
- No step is skipped
- Security is a hard gate

---

## Priority 1 — Password Reset (Highest Risk)

### Why
- Direct account takeover risk
- Publicly exposed flow
- Historically abused feature

### Steps
1. Security design & pseudo tests
2. Enumeration-safe reset request
3. One-time reset tokens
4. Expiry enforcement
5. Token invalidation after use
6. Tests → Pass
7. Security review

---

## Priority 2 — Refresh Token Rotation

### Why
- Reduces impact of token theft
- Complements existing refresh logic

### Steps
1. Design rotation strategy
2. Storage decision
3. Replay detection
4. Forced re-auth on reuse
5. Tests → Pass
6. Review

---

## Priority 3 — Pagination & Performance Controls

### Why
- Data scraping risk
- Performance abuse

### Steps
1. Pagination pseudo tests
2. Max limits enforcement
3. Default ordering
4. Authorization at query level
5. Tests → Pass

---

## Priority 4 — Database Upgrade (PostgreSQL)

### Why
- Data integrity
- Concurrency safety
- Future scalability

### Steps
1. Schema review
2. Migration strategy
3. Constraints & indexes
4. Transaction safety
5. Performance tests

---

## Priority 5 — Optional Enhancements (Deferred)

- Audit logging
- Admin roles
- AI assistant
- SaaS billing

---

## Completion Criteria

- All priority items reviewed
- All tests passing
- v2 ready for feature expansion