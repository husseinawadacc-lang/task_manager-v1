# PSEUDO LOGIN – AUTH FLOW (Documentation)

هذا الملف يوضح السلوك المتوقع لعملية تسجيل الدخول (Login)
من ناحية Business Logic + Security بدون أي كود تنفيذي.

==================================================

1) LOGIN SUCCESS
----------------
GIVEN:
- مستخدم مسجل
- Email صحيح
- Password صحيح
- user.is_active = True

WHEN:
POST /auth/login
{
  "email": "user@example.com",
  "password": "StrongPass1!"
}

THEN:
- HTTP 200 OK
- Response:
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}

==================================================

2) INVALID EMAIL
----------------
GIVEN:
- Email غير موجود
- Password أي قيمة

WHEN:
POST /auth/login

THEN:
- HTTP 401 Unauthorized
- Message: "invalid credentials"

(لا يتم كشف أن الإيميل غير موجود)

==================================================

3) INVALID PASSWORD
-------------------
GIVEN:
- Email موجود
- Password خاطئ

WHEN:
POST /auth/login

THEN:
- HTTP 401 Unauthorized
- Message: "invalid credentials"

(نفس رسالة الإيميل الخاطئ لمنع enumeration)

==================================================

4) INACTIVE USER
----------------
GIVEN:
- Email موجود
- Password صحيح
- user.is_active = False

WHEN:
POST /auth/login

THEN:
- HTTP 401 Unauthorized
- Message: "user is inactive"

==================================================

5) MISSING FIELDS
-----------------
GIVEN:
- email مفقود
- أو password مفقود

WHEN:
POST /auth/login

THEN:
- HTTP 422 Unprocessable Entity
- Validation error من API layer

==================================================

6) EMPTY VALUES
---------------
GIVEN:
- email = ""
- أو password = ""

WHEN:
POST /auth/login

THEN:
- HTTP 422
- Validation error

==================================================

7) INVALID TYPES
----------------
GIVEN:
- email رقم
- password object / list

WHEN:
POST /auth/login

THEN:
- HTTP 422
- Validation error

==================================================

8) SECURITY RULES
-----------------
- لا يتم الكشف:
  - هل الإيميل موجود
  - هل الباسورد قريب من الصحيح
- لا stack trace
- لا تفاصيل داخلية
- رسالة موحدة: "invalid credentials"

==================================================

9) TOKEN RULES
--------------
- access_token:
  - JWT صالح
  - يحتوي user_id
- token_type = "bearer"

==================================================

خارج نطاق v1 (مؤجل):
- Rate Limiting
- Refresh Token Rotation
- Device / IP binding