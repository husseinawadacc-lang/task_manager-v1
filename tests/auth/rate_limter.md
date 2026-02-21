# 🔒 Rate Limiter – Pseudo Tests (Single File)

## الهدف
منع:
- Brute Force
- Credential Stuffing
- User Enumeration

مع الحفاظ على:
- رسالة خطأ موحدة
- عدم كشف وجود المستخدم
- عدم كسر flow المصادقة

---

## الإعدادات

- MAX_ATTEMPTS = 5
- WINDOW_SECONDS = 300
- KEY = login:{client_ip}:{email}

---

## القواعد الأساسية

- أي محاولة login فاشلة → تُحسب
- بعد تجاوز الحد → block مؤقت
- أي login ناجح → reset للعداد
- نفس رسالة الخطأ دائمًا:
  "Invalid email or password"

---

## PSEUDO TESTS

---

### 1️⃣ Successful login does NOT increase attempts

GIVEN  
- مستخدم موجود  
- بيانات صحيحة  

WHEN  
- إرسال طلب login صحيح  

THEN  
- يتم تسجيل الدخول بنجاح  
- لا يتم زيادة عداد المحاولات  
- يتم reset لأي محاولات سابقة  

EXPECTED  
- HTTP 200  
- access_token returned  

---

### 2️⃣ Failed login increases attempts

GIVEN  
- مستخدم موجود  

WHEN  
- إرسال password خاطئ  

THEN  
- يتم رفض الدخول  
- زيادة عداد المحاولات بمقدار 1  

EXPECTED  
- HTTP 401  
- "Invalid email or password"  


---

### 3️⃣ Block after max attempts

GIVEN  
- 5 محاولات login فاشلة خلال نفس الـ window  

WHEN  
- محاولة login السادسة  

THEN  
- يتم الحظر المؤقت  

EXPECTED  
- HTTP 429  
- "Too many login attempts, try again later"  

---

### 4️⃣ Rate limit applies to non-existing email

GIVEN  
- Email غير موجود  

WHEN  
- تكرار محاولات login  

THEN  
- يتم تطبيق rate limiter  
- بدون أي تلميح أن المستخدم غير موجود  

EXPECTED  
- HTTP 401 أولًا  
- HTTP 429 بعد تجاوز الحد  

---

### 5️⃣ Rate limit is per user/email

GIVEN  
- User A  
- User B  

WHEN  
- User A يتجاوز الحد  
- User B يحاول login  

THEN  
- User A محظور  
- User B غير محظور  

EXPECTED  
- User A → HTTP 429  
- User B → flow طبيعي  

---

### 6️⃣ Successful login resets counter

GIVEN  
- مستخدم لديه محاولات فاشلة سابقة  

WHEN  
- login ناجح  

THEN  
- reset عداد المحاولات  

EXPECTED  
- HTTP 200  
- المحاولات تبدأ من 0  

---

### 7️⃣ Rate limit expires after time window (delay for next version)

GIVEN  
- مستخدم محظور  

WHEN  
- انتهاء WINDOW_SECONDS  

THEN  
- يمكنه المحاولة مجددًا  

EXPECTED  
- عدم الحظر  
- login يعمل طبيعي  
USE MONKEYPATH TO CHANGE TIME
---

### 8️⃣ Inactive user still counts attempts (delay for next version)

GIVEN  
- مستخدم is_active = False  

WHEN  
- محاولات login  

THEN  
- يتم احتساب المحاولات  
- لا bypass للـ rate limiter  

EXPECTED  
- HTTP 401 أو 403  
- العدّاد يعمل  

---

### 9️⃣ Rate limiter runs BEFORE password verification (delay for next version)

GIVEN  
- مستخدم محظور  

WHEN  
- محاولة login  

THEN  
- لا يتم فحص password  
- يتم الرفض فورًا  

EXPECTED  
- HTTP 429  
- لا تحقق كلمة مرور  

---

## ملاحظات أمنية

- لا يوجد فرق بين:
  - email غير موجود
  - password خاطئ
- كل الأخطاء موحدة
- يمنع enumeration
- يمنع brute force

---

## الحالة

- [x] Pseudo tests مكتوبة
- [ ] تحويل إلى pytest
- [ ] ربط مع CI
7 and 8 and 9 delay for next version