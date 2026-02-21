
from fastapi import status

LOGIN_URL = "/api/v1/auth/login"


def test_successful_login_does_not_increase_attempts(client, user):
    """
    GIVEN مستخدم صحيح
    WHEN يسجل دخول بكلمة مرور صحيحة
    THEN يتم الدخول بنجاح (200)
         ولا يتم حظره لاحقًا
    """

    response = client.post(
        LOGIN_URL,
        json={
            "email": user.email,
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == status.HTTP_200_OK


def test_failed_login_increases_attempts_and_blocks(client, user):
    """
    GIVEN مستخدم موجود
    WHEN يحاول تسجيل الدخول بكلمة مرور خاطئة عدة مرات
    THEN بعد تجاوز الحد يتم حظره (429)
    """

    # عدد المحاولات الخاطئة (حسب RateLimiter = 5)
    for i in range(5):
        response = client.post(
            LOGIN_URL,
            json={
                "email": user.email,
                "password": "WrongPassword!",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # المحاولة السادسة → محظور
    response = client.post(
        LOGIN_URL,
        json={
            "email": user.email,
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS



def test_rate_limit_applies_to_non_existing_email(client):
    """
    GIVEN بريد إلكتروني غير موجود
    WHEN محاولة تسجيل الدخول بكلمة مرور خاطئة عدة مرات
    THEN يتم تطبيق rate limiting
         دون كشف أن الإيميل غير موجود
    """

    fake_email = "notfound@test.com"

    # محاولات فاشلة ضمن الحد
    for _ in range(5):
        response = client.post(
            LOGIN_URL,
            json={
                "email": fake_email,
                "password": "WrongPassword!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # تجاوز الحد
    response = client.post(
        LOGIN_URL,
        json={
            "email": fake_email,
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS    



def test_rate_limit_is_per_email(client):
    """
    GIVEN مستخدمين مختلفين (إيميلات مختلفة)
    WHEN تجاوز الأول حد المحاولات
    THEN الثاني لا يتأثر
    """

    email_1 = "user1@test.com"
    email_2 = "user2@test.com"
    password = "WrongPassword!"

    # 🔴 تجاوز الحد للإيميل الأول
    for _ in range(5):
        response = client.post(
            LOGIN_URL,
            json={"email": email_1, "password": password},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post(
        LOGIN_URL,
        json={"email": email_1, "password": password},
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    # 🟢 الإيميل الثاني يجب ألا يتأثر
    response = client.post(
        LOGIN_URL,
        json={"email": email_2, "password": password},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED    

def test_successful_login_resets_counter(client, user):
    """
    GIVEN مستخدم فشل في تسجيل الدخول عدة مرات
    WHEN ينجح في تسجيل الدخول
    THEN يتم reset عداد المحاولات
    """

    email = user.email

    # 🔴 3 محاولات فاشلة
    for _ in range(3):
        response = client.post(
            LOGIN_URL,
            json={"email": email, "password": "WrongPassword!"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 🟢 تسجيل دخول ناجح
    response = client.post(
        LOGIN_URL,
        json={"email": email, "password": "StrongPass1!"},
    )
    assert response.status_code == status.HTTP_200_OK

    # 🔴 محاولة فاشلة جديدة (يجب أن تكون الأولى بعد reset)
    response = client.post(
        LOGIN_URL,
        json={"email": email, "password": "WrongPassword!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  
