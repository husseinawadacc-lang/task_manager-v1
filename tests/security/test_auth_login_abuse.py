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

    