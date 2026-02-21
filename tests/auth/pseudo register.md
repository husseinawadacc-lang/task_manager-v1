cat << 'EOF' > tests/auth/pseudo_register.md
# PSEUDO TEST — Auth Register

Endpoint:
POST /api/v1/auth/register

Purpose:
- Create new user securely
- Enforce password policy
- Prevent user enumeration
- Keep service layer clean

--------------------------------------------------
TEST 1: Successful Registration
--------------------------------------------------
GIVEN:
- username not used
- email not used
- strong password (policy-compliant)
- role = "user"

WHEN:
- POST /auth/register

THEN:
- Status = 201 success
- Response includes:
  - id
  - username
  - email
  - role
  - is_active = true
- Response does NOT include:
  - password
  - password_hash
- Password is:
  - validated
  - hashed (bcrypt)
  - pepper applied
- User saved in storage

--------------------------------------------------
TEST 2: Register With Existing Email
--------------------------------------------------
GIVEN:
- Existing user with same email

WHEN:
- POST /auth/register

THEN:
- Status = 409 Conflict
- Error message:
  "User already exists"
- No indication whether email or username exists (anti-enumeration)

--------------------------------------------------
TEST 3: Weak Password
--------------------------------------------------
GIVEN:
- Password violates policy:
  - too short
  - no uppercase
  - no digit
  - no symbol

WHEN:
- POST /auth/register

THEN:
- Status = 422 (unprocessable entiry)
- Error message:
  "Password does not meet security requirements"
- User NOT created

--------------------------------------------------
TEST 4: Invalid Role
--------------------------------------------------
GIVEN:
- role not in allowed roles

WHEN:
- POST /auth/register

THEN:
- Status = 400 Bad Request
- Error message:
  "Invalid role"

--------------------------------------------------
TEST 5: Missing Required Fields
--------------------------------------------------
GIVEN:
- Missing username OR email OR password

WHEN:
- POST /auth/register

THEN:
- Status = 422 Unprocessable Entity
- FastAPI validation error
- AuthService NOT called

--------------------------------------------------
TEST 6: Security Guarantees
--------------------------------------------------
ASSERT:
- Password never logged
- Pepper never exposed
- No sensitive data in response
- Storage never receives raw password

--------------------------------------------------
DESIGN NOTES
--------------------------------------------------
- Validation (shape): FastAPI / Pydantic
- Business rules: AuthService
- Hashing & pepper: utils.security
- Persistence: Storage layer
- Endpoint contains NO business logic
EOF

