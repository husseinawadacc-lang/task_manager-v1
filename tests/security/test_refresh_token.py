# tests/security/test_refresh_token_lifecycle.py

REFRESH_URL = "/api/v1/auth/refresh"


# -------------------------------------------------
# 1. Missing Refresh Token
# -------------------------------------------------

def test_refresh_without_token_is_rejected(client):
    response = client.post(REFRESH_URL)
    assert response.status_code == 401


# -------------------------------------------------
# 2. Invalid / Tampered Refresh Token
# -------------------------------------------------

def test_refresh_with_invalid_token_is_rejected(client):
    headers = {
        "Authorization": "Bearer invalid.refresh.token"
    }

    response = client.post(REFRESH_URL, headers=headers)
    assert response.status_code == 401


# -------------------------------------------------
# 3. Expired Refresh Token
# -------------------------------------------------

def test_refresh_with_expired_token_is_rejected(client, expired_refresh_headers):
    response = client.post(REFRESH_URL, headers=expired_refresh_headers)
    assert response.status_code == 401


# -------------------------------------------------
# 4. Valid Refresh Token
# -------------------------------------------------

def test_refresh_with_valid_token_returns_new_access_token(
    client,
    valid_refresh_headers,
):
    response = client.post(REFRESH_URL, headers=valid_refresh_headers)

    assert response.status_code == 200
    body = response.json()

    assert "access_token" in body
    assert body["access_token"]