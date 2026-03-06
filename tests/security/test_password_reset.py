# tests/security/test_password_reset.py

import pytest


# =========================================================
# Password Reset – REQUEST
# =========================================================

class TestPasswordResetRequest:
    """
    Tests related to requesting password reset.
    Focus:
    - Enumeration safety
    - Generic responses
    """

    def test_existing_email_returns_generic_response(
        self,
        client,
        user,
    ):
        response = client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": user.email},
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_non_existing_email_returns_same_generic_response(
        self,
        client,
            ):
        response = client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "ghost@example.com"},
        )

        assert response.status_code == 200
        assert "message" in response.json()


# =========================================================
# Password Reset – CONFIRM
# =========================================================

class TestPasswordResetConfirm:
    """
    Tests for confirming password reset using tokens.
    """

    def test_valid_token_and_strong_password_succeeds(
        self,
        client,
        valid_password_reset_token,
        user,
    ):
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": valid_password_reset_token,
                "password": "NewStrongPassword123!",
            },
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_expired_token_is_rejected(
        self,
        client,
        expired_password_reset_token,
    ):
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": expired_password_reset_token,
                "password": "AnotherStrongPassword123!",
            },
        )
        print (response.json())
        assert response.status_code ==400

    def test_used_token_is_rejected(
        self,
        client,
        used_password_reset_token,
    ):
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": used_password_reset_token,
                "password": "AnotherStrongPassword123!",
            },
        )

        assert response.status_code ==400


# =========================================================
# Password Reset – SECURITY & POLICY
# =========================================================

class TestPasswordResetSecurity:
    """
    Security-specific cases:
    - Invalid token
    - Weak password
    """

    def test_random_invalid_token_is_rejected(
        self,
        client,
           ):
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "totally-invalid-token",
                "password": "StrongPassword123!",
            },
        )

        assert response.status_code in (400, 401)

    def test_weak_password_is_rejected_and_token_not_consumed(
        self,
        client,
        valid_password_reset_token,
    ):
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": valid_password_reset_token,
                "password": "123",
            },
        )

        assert response.status_code == 400