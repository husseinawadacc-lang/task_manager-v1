def test_login_success(client, user):
    """
    GIVEN:
        - User exists
        - Correct email
        - Correct password
        - User is active

    WHEN:
        POST /auth/login

    THEN:
        - 200 OK
        - access_token returned
        - token_type = bearer
    """
    response = client.post(
        "api/v1/auth/login",
        json={
            "email": user.email,
            "password": "StrongPass1!",
        },
    )
    
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "notfound@test.com",
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 401

    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Invalid email or password"

def test_login_invalid_password(client, user):
    """
    GIVEN an existing user
    WHEN logging in with wrong password
    THEN return 401 Unauthorized
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401

    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Invalid email or password"  

def test_login_inactive_user(client, auth_service):
    """
    GIVEN an inactive user
    WHEN logging in with correct credentials
    THEN return 401 Unauthorized
    """

    # إنشاء مستخدم غير نشط
    user = auth_service.register(
        username="inactive_user",
        email="inactive@test.com",
        password="StrongPass1!",
        role="user",
        is_active=False,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 401

    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Invalid email or password"          

def test_login_missing_email(client):
    """
    GIVEN login payload missing email
    WHEN calling POST /auth/login
    THEN return 422 validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            # "email" is missing
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 422

    body = response.json()
    assert "detail" in body

def test_login_missing_password(client):
    """
    GIVEN login payload missing password
    WHEN calling POST /auth/login
    THEN return 422 validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@test.com",
            # "password" is missing
        },
    )

    assert response.status_code == 422

    body = response.json()
    assert "detail" in body

def test_login_missing_email_and_password(client):
    """
    GIVEN empty payload
    WHEN calling POST /auth/login
    THEN return 422 validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={},
    )

    assert response.status_code == 422        

def test_login_empty_email(client):
    """
    GIVEN login payload with empty email
    WHEN calling POST /auth/login
    THEN return authentication / validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "   ",        # empty after strip
            "password": "StrongPass1!",
        },
    )

    assert response.status_code in (400, 401, 422)

    body = response.json()
    assert "detail" in body

def test_login_empty_password(client):
    """
    GIVEN login payload with empty password
    WHEN calling POST /auth/login
    THEN return authentication / validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@test.com",
            "password": "",        # empty password
        },
    )

    assert response.status_code in (400, 401, 422)

    body = response.json()
    assert "detail" in body

def test_login_empty_email_and_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "",
            "password": "   ",
        },
    )

    assert response.status_code in (400, 401, 422)

def test_login_invalid_email_type(client):
    """
    GIVEN email with invalid type (int)
    WHEN calling POST /auth/login
    THEN return 422 validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": 12345,          # ❌ invalid type
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 422

    body = response.json()
    assert "detail" in body

def test_login_invalid_password_type(client):
    """
    GIVEN password with invalid type (list)
    WHEN calling POST /auth/login
    THEN return 422 validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@test.com",
            "password": ["not", "a", "string"],  # ❌ invalid type
        },
    )

    assert response.status_code == 422

def test_login_invalid_both_types(client):
    """
    GIVEN email and password with invalid types
    WHEN calling POST /auth/login
    THEN return 422 validation error
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": {"bad": "type"},
            "password": 999,
        },
    )

    assert response.status_code == 422

def test_login_user_role_success(client, user):
    """
    GIVEN a normal USER account
    WHEN login is called
    THEN login succeeds regardless of role
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body

def test_login_admin_role_success(client, admin):
    """
    GIVEN an ADMIN account
    WHEN login is called
    THEN login succeeds
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": admin.email,
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body

def test_login_does_not_check_role(client, user):
    """
    Ensure login does NOT reject based on role
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 200

def test_login_returns_access_token(client, user):
    """
    GIVEN valid credentials
    WHEN login is successful
    THEN response contains access_token and token_type
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
