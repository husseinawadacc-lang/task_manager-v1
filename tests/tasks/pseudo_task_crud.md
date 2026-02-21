# Task CRUD Basic Tests (v1)

## الهدف
التحقق من CRUD الأساسي للـ Tasks مع الصلاحيات.

---

## 1. Create Task (User)

Given:
- مستخدم مسجّل
- access token صالح

When:
- POST /tasks
- بيانات صحيحة (title, description)

Then:
- status code = 201 Created
- task يحتوي على:
  - id
  - owner = user
  - completed = false

---

## 2. List Tasks (User)

Given:
- مستخدم لديه Tasks

When:
- GET /tasks

Then:
- status code = 200 OK
- يتم إرجاع Tasks الخاصة بالمستخدم فقط

---

## 3. Get Task by ID (Owner)

Given:
- مستخدم يملك Task

When:
- GET /tasks/{task_id}

Then:
- status code = 200 OK
- يتم إرجاع الـ Task

---

## 4. Get Task by ID (Not Owner)

Given:
- مستخدم A
- Task مملوك لمستخدم B

When:
- المستخدم A يحاول الوصول للـ Task

Then:
- status code = 403 Forbidden

---

## 5. Update Task (Owner)

Given:
- مستخدم يملك Task

When:
- PUT /tasks/{task_id}
- بيانات تحديث صحيحة

Then:
- status code = 200 OK
- يتم تحديث الـ Task

---

## 6. Update Task (Not Owner)

Given:
- مستخدم A
- Task مملوك لمستخدم B

When:
- المستخدم A يحاول التحديث

Then:
- status code = 403 Forbidden

---

## 7. Delete Task (Owner)

Given:
- مستخدم يملك Task

When:
- DELETE /tasks/{task_id}

Then:
- status code = 204 No Content
- Task محذوف

---

## 8. Delete Task (Admin)

Given:
- Admin user
- Task لأي مستخدم

When:
- DELETE /tasks/{task_id}

Then:
- status code = 204 No Content

---

## خارج نطاق v1 (مؤجل)
- Pagination
- Search / filter
- Soft delete
- Bulk operations
- Task abuse testing