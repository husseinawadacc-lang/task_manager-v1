# System Pseudo Tests

This document defines all expected behaviours before writing tests.

Format:

GIVEN
WHEN
THEN

---

# AUTHENTICATION TESTS

## Login success

GIVEN
valid email and password

WHEN
POST /auth/login

THEN
response status = 200
access token returned
refresh token returned

---

## Login failure

GIVEN
invalid password

WHEN
POST /auth/login

THEN
response status = 401

---

## User enumeration protection

GIVEN
non existing email

WHEN
POST /auth/login

THEN
response status = 401
same message as invalid password

---

# TOKEN TESTS

## Access token valid

GIVEN
valid access token

WHEN
GET /auth/me

THEN
response status = 200

---

## Access token expired

GIVEN
expired token

WHEN
GET /auth/me

THEN
response status = 401

---

# REFRESH TOKEN TESTS

## Refresh rotation

GIVEN
valid refresh token

WHEN
POST /auth/refresh

THEN
new access token returned
new refresh token returned

---

## Refresh reuse detection

GIVEN
refresh token used once

WHEN
POST /auth/refresh again

THEN
response status = 401
token family revoked

---

# LOGOUT TESTS

## Logout invalidates access token

GIVEN
valid access token

WHEN
POST /auth/logout

THEN
token added to blacklist

---

## Access token invalid after logout

GIVEN
user logged out

WHEN
GET /auth/me

THEN
response status = 401

---

## Refresh token invalid after logout

GIVEN
user logged out

WHEN
POST /auth/refresh

THEN
response status = 401

---

# TASK TESTS

## Create task

GIVEN
authenticated user

WHEN
POST /tasks

THEN
task created
owner_id = user.id

---

## Task ownership

GIVEN
task belongs to user A

WHEN
user B requests GET /tasks/{id}

THEN
response status = 404

---

## Update task

GIVEN
task belongs to user

WHEN
PUT /tasks/{id}

THEN
task updated

---

## Delete task

GIVEN
task belongs to user

WHEN
DELETE /tasks/{id}

THEN
task removed

---

# PAGINATION TESTS

## List tasks

GIVEN
multiple tasks

WHEN
GET /tasks?limit=20&offset=0

THEN
items returned
total returned

---

## Pagination limit protection

GIVEN
limit > MAX_LIMIT

WHEN
GET /tasks

THEN
InvalidPaginationError raised