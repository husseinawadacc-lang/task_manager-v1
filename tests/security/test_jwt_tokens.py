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


def test_refresh_token_cannot_be_reused(client, valid_refresh_headers):

    # first refresh (valid)
    response1 = client.post(
        "/api/v1/auth/refresh",
        headers=valid_refresh_headers
    )

    assert response1.status_code == 200

    # attacker tries to reuse old token
    response2 = client.post(
        "/api/v1/auth/refresh",
        headers=valid_refresh_headers
    )

    assert response2.status_code == 401 

def test_logout_revokes_refresh_token(client, valid_refresh_headers):

    response = client.post(
        "/api/v1/auth/logout",
        headers=valid_refresh_headers
    )

    assert response.status_code == 204

def test_access_token_invalid_after_logout(client, valid_access_headers):

    # logout
    client.post("/api/v1/auth/logout", headers=valid_access_headers)

    # try to use the same access token
    response = client.get(
        "/api/v1/auth/me",
        headers=valid_access_headers
    )

    assert response.status_code == 401



def test_refresh_token_reuse_attack(client, valid_refresh_headers):

    # 1️⃣ أول refresh (يعمل بشكل طبيعي)
    response1 = client.post(
        "/api/v1/auth/refresh",
        headers=valid_refresh_headers
    )

    assert response1.status_code == 200


    # 2️⃣ محاولة استخدام نفس refresh token مرة أخرى
    response2 = client.post(
        "/api/v1/auth/refresh",
        headers=valid_refresh_headers
    )

    # 3️⃣ يجب أن يفشل
    assert response2.status_code == 401   
