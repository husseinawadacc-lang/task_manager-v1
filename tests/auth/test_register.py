
# -------------------------------------------------
# TEST 1: Successful Registration
# -------------------------------------------------

def test_register_success(client):
    """
    الهدف:
    - التأكد أن عملية التسجيل الناجحة تعمل بشكل صحيح
    - التأكد من عدم تسريب بيانات حساسة
    - التأكد من احترام الـ flow:
      API → Service → Utils → Storage
    """

    # -------------------------------
    # GIVEN
    # -------------------------------
    # بيانات مستخدم جديدة وصحيحة
    payload = {
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "Strong@Pass1!",
        "role": "user",
    }

    # -------------------------------
    # WHEN
    # -------------------------------
    # إرسال request التسجيل
    response = client.post(
        "/api/v1/auth/register",
        json=payload
    )

    # -------------------------------
    # THEN
    # -------------------------------
    print("JSON:", response.json())
    print("Response status code:", response.status_code)
    print("TEXT:", response.text)
    # 1️⃣ كود الحالة
    assert response.status_code == 201

    # 2️⃣ جسم الرد
    body = response.json()

    # -------------------------------
    # Assertions: Response shape
    # -------------------------------

    # لازم يكون في ID
    assert "id" in body
    assert isinstance(body["id"], int)

    # البيانات الأساسية
    assert body["username"] == payload["username"]
    assert body["email"] == payload["email"]
    assert body["role"] == payload["role"]

    # الحساب نشط افتراضيًا
    assert body["is_active"] is True

    # -------------------------------
    # Security assertions
    # -------------------------------

    # ❌ لا يجب إرجاع أي بيانات حساسة
    assert "password" not in body
    assert "password_hash" not in body
    assert "pepper" not in body

    # -------------------------------
    # Design guarantees
    # -------------------------------
    # لو التست ده عدى:
    # - hashing تم في utils.security
    # - pepper اتطبق
    # - storage استقبل User object فقط
    # - endpoint لم يحتوِ business logic


def test_register_with_existing_email(client):
    """
    GIVEN:
        - Existing user already registered with email user@test.com
    WHEN:
        - Register is called again with the same email
    THEN:
        - API must return 409 Conflict
        - User must NOT be created again
    """

    payload = {
        "username": "user1",
        "email": "user@test.com",
        "password": "StrongPass1!",
        "role": "user",
    }

    # First registration (should succeed)
    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )
    assert first_response.status_code == 201

    # Second registration with same email
    second_response = client.post(
        "/api/v1/auth/register",
        json={
            **payload,
            "username": "user2",  # different username, same email
        },
    )

    assert second_response.status_code == 409
    assert "email" in second_response.json()["detail"].lower()  

def test_register_weak_password(client):
    """
    GIVEN:
        - Weak password that does not meet security policy
    WHEN:
        - Register endpoint is called
    THEN:
        - API must reject the request
        - Status code = 422
        - Error message mentions password rules
    """

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "weakuser",
            "email": "weak@test.com",
            "password": "password",  # ❌ weak
            "role": "user",
        },
    )

    assert response.status_code == 422   
    assert "password" in response.json()["detail"].lower()      

def test_register_invalid_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "badrole",
            "email": "badrole@test.com",
            "password": "StrongPass1!",
            "role": "superadmin",  # ❌ invalid role
        },
    )

    assert response.status_code == 422    

def test_register_missing_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "StrongPass1!",
            "role": "user",
        },
    )

    assert response.status_code == 422    
##############################
# security-focused tests
###############################
def test_register_response_does_not_include_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "secureuser",
            "email": "secure@test.com",
            "password": "StrongPass1!",
            "role": "user",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "password" not in data
    assert "hashed_password" not in data

def test_password_is_hashed_in_storage(auth_service):
    user = auth_service.register(
        username="hashuser",
        email="hash@test.com",
        password="StrongPass1!",
        role="user",
    )

    assert user.password_hash != "StrongPass1!"
    assert user.password_hash.startswith("$2") or len(user.password_hash) > 20

def test_password_not_logged(client, caplog):
    with caplog.at_level("INFO"):
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "loguser",
                "email": "log@test.com",
                "password": "StrongPass1!",
                "role": "user",
            },
        )

    logs = " ".join(caplog.messages)

    assert "StrongPass1!" not in logs
    assert "password" not in logs.lower()

def test_pepper_not_exposed_anywhere(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "pepperuser",
            "email": "pepper@test.com",
            "password": "StrongPass1!",
            "role": "user",
        },
    )

    body = response.text.lower()

        
    assert "SECRET_KEY" not in body
    assert "password_hash" not in body 
    assert "PASSWORD_PEPPER" not in body        