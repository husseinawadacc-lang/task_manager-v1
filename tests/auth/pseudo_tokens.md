# Token Basic Tests (v1)

## الهدف
التحقق من عمل نظام التوكن (JWT) في الحالات الأساسية فقط.

---

## 1. Access token صالح

Given:
- مستخدم مسجّل
- تم تسجيل الدخول بنجاح
- access token صالح

When:
- إرسال Request إلى endpoint محمي (مثل /auth/me أو /tasks)

Then:
- status code = 200 OK
- يتم إرجاع البيانات المطلوبة

---

## 2. Access token مفقود

Given:
- لا يوجد Authorization header

When:
- إرسال Request إلى endpoint محمي

Then:
- status code = 401 Unauthorized
- رسالة خطأ عامة بدون تفاصيل

---

## 3. Access token غير صالح

Given:
- Authorization header موجود
- التوكن:
  - عشوائي
  - أو معدل
  - أو بصيغة JWT غير صحيحة

When:
- إرسال Request إلى endpoint محمي

Then:
- status code = 401 Unauthorized
- لا يتم كشف سبب تفصيلي

---

## 4. Access token منتهي الصلاحية (delay v2اختياري في v1)

Given:
- access token منتهي الصلاحية

When:
- استخدامه للوصول إلى endpoint محمي

Then:
- status code = 401 Unauthorized

---

## خارج نطاق v1 (مؤجل)
- Refresh token misuse
- Token replay
- Token audience / issuer
- Multiple devices