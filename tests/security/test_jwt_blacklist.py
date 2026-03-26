def test_access_token_valid_before_logout(client, user_headers):

    response = client.get(
        "/api/v1/auth/me",
        headers=user_headers
    )

    assert response.status_code == 200

def test_access_token_invalid_after_logout(client, user_headers):

    client.post(
        "/api/v1/auth/logout",
        headers=user_headers
    )

    response = client.get(
        "/api/v1/auth/me",
        headers=user_headers
    )

    assert response.status_code == 401


def test_blacklisted_token_rejected(client, user_headers):

    client.post(
        "/api/v1/auth/logout",
        headers=user_headers
    )

    response = client.get(
        "/api/v1/tasks",
        headers=user_headers
    )

    assert response.status_code == 401
    
            