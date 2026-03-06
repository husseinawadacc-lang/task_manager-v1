# tests/security/test_jwt_lifecycle.py

PROTECTED_URL = "/api/v1/auth/me"


# -------------------------------------------------
# 1. Missing Token
# -------------------------------------------------

def test_access_protected_endpoint_without_token_is_rejected(client):
    response = client.get(PROTECTED_URL)
    assert response.status_code == 401


# -------------------------------------------------
# 2. Invalid / Tampered Token
# -------------------------------------------------

def test_access_with_invalid_token_is_rejected(client):
    headers = {
        "Authorization": "Bearer invalid.jwt.token"
    }

    response = client.get(PROTECTED_URL, headers=headers)
    assert response.status_code == 401


# -------------------------------------------------
# 3. Expired Token
# -------------------------------------------------

def test_access_with_expired_token_is_rejected(client, expired_user_headers):
    response = client.get(PROTECTED_URL, headers=expired_user_headers)
    assert response.status_code == 401


# -------------------------------------------------
# 4. Valid Token
# -------------------------------------------------

def test_access_with_valid_token_succeeds(client, user_headers):
    response = client.get(PROTECTED_URL, headers=user_headers)
    assert response.status_code == 200