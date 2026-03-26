# tests/security/test_auth_login_abuse.py

import pytest


# =========================
# Auth Login Abuse – Tests
# =========================
#
# Spec:
# docs/security/auth_login_abuse.pseudo.md
#
# Phase: Security Hardening – Test First
# Status: RED phase (expected failures)
#


LOGIN_URL = "/api/v1/auth/login"

@pytest.fixture
def wrong_password_payload():
    return {
        "email": "user@example.com",
        "password": "WrongPassword",
    }
@pytest.fixture
def non_existing_user_payload():
    return {
        "email":"ghost@example.com",
        "password":"samePassword123!"
    }



# ------------------------------------------------------------------
# 1. No User Enumeration
# ------------------------------------------------------------------

def test_login_wrong_password_and_non_existing_user_return_same_error(
    client,
    wrong_password_payload,
    non_existing_user_payload,
):
    """
    GIVEN wrong password and non-existing email
    WHEN login is attempted
    THEN error response must be identical
    """
    response_wrong_password = client.post(
        LOGIN_URL,
        json=wrong_password_payload,
    )

    response_non_existing = client.post(
        LOGIN_URL,
        json=non_existing_user_payload,
    )

    assert response_wrong_password.status_code == response_non_existing.status_code
    assert response_wrong_password.json() == response_non_existing.json()


# ------------------------------------------------------------------
# 2. No Token on Failure
# ------------------------------------------------------------------

def test_login_failure_does_not_return_tokens(client, wrong_password_payload):
    """
    GIVEN a failed login
    WHEN API responds
    THEN no access or refresh tokens are returned
    """
    response = client.post(
        LOGIN_URL,
        json=wrong_password_payload,
    )

    body = response.json()

    assert "access_token" not in body
    assert "refresh_token" not in body


# ------------------------------------------------------------------
# 3. Successful Login Still Works  make(user existed, login)  # sanity check
# ------------------------------------------------------------------

def test_login_success_returns_tokens(client, user):
    payload= {
        "email":user.email,
        "password":"StrongPass1!"
    }
    response = client.post(
        "/api/v1/auth/login",
        json=payload
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

    
def test_access_token_tampering(client, user_headers):

    token = user_headers["Authorization"].split(" ")[1]

    parts = token.split(".")
    tampered = parts[0] + "." + parts[1] + ".invalidsignature"

    headers = {"Authorization": f"Bearer {tampered}"}

    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 401

def test_access_token_after_logout(client, user_headers):

    client.post("/api/v1/auth/logout", headers=user_headers)

    response = client.get("/api/v1/auth/me", headers=user_headers)

    assert response.status_code == 401

def test_refresh_token_reuse_attack(client, valid_refresh_headers):

    client.post("/api/v1/auth/refresh", headers=valid_refresh_headers)

    response = client.post("/api/v1/auth/refresh", headers=valid_refresh_headers)

    assert response.status_code == 401

def test_refresh_after_logout(client, valid_refresh_headers):

    client.post("/api/v1/auth/logout", headers=valid_refresh_headers)

    response = client.post("/api/v1/auth/refresh", headers=valid_refresh_headers)

    assert response.status_code == 401

def test_idor_task_access(client, user_headers, other_user_task):

    response = client.get(
        f"/api/v1/tasks/{other_user_task.id}",
        headers=user_headers
    )

    assert response.status_code == 404

def test_permission_escalation(client, user_headers):

    response = client.delete(
        "/api/v1/tasks/1",
        headers=user_headers
    )

    assert response.status_code in [403, 404]

def test_pagination_validate(client, user_headers):

    response = client.get(
        "/api/v1/tasks?limit=100000",
        headers=user_headers
    )

    assert response.status_code == 422

def test_pagination_negative_limit(client, user_headers):

    response = client.get(
        "/api/v1/tasks?limit=-10",
        headers=user_headers
    )

    assert response.status_code == 422    

def test_request_without_token(client):

    response = client.get("/api/v1/tasks")

    assert response.status_code == 401

def test_invalid_token_type(client, valid_refresh_headers):

    response = client.get(
        "/api/v1/auth/me",
        headers=valid_refresh_headers
    )

    assert response.status_code == 401

def test_expired_token(client, expired_user_headers):

    response = client.get(
        "/api/v1/auth/me",
        headers=expired_user_headers
    )

    assert response.status_code == 401                                        