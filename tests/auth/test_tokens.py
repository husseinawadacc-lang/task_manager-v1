def test_access_with_valid_token(client, user_headers):
    response = client.get(
        "/api/v1/auth/me",
        headers=user_headers,
    )

    assert response.status_code == 200
    body = response.json()

    assert "id" in body
    assert "email" in body

def test_access_without_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401

